"""Owner-bound document RAG backed by a real Qdrant service or embedded client.

No daemon, embedding download, or network request occurs until explicitly constructed.
The authenticated principal is supplied by the trusted launcher, never tool arguments.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Protocol
from urllib.parse import urlsplit
import math
import re
import uuid
from .core import HashEmbedding, RetrievalError

@dataclass(frozen=True)
class Principal:
    subject: str
    tenant: str
    permissions: frozenset[str]
    def require(self, permission):
        if not self.subject or not self.tenant or permission not in self.permissions:
            raise PermissionError('principal lacks required capability')

class Encoder(Protocol):
    identity: str
    dimensions: int
    def encode(self, text: str) -> list[float]: ...

class SentenceTransformerEncoder:
    """Optional genuine encoder, pinned to an explicit immutable HF commit.

    No unverified default revision or downloaded-model success is claimed.
    Parent QA must first resolve/record an approved revision and run actual model.
    """
    def __init__(self, model_id, revision, dimensions):
        if not re.fullmatch(r'[0-9a-f]{40}', revision):
            raise RetrievalError('immutable forty-hex embedding revision required')
        if type(dimensions) is not int or not 1 <= dimensions <= 4096:
            raise RetrievalError('invalid embedding dimensions')
        from sentence_transformers import SentenceTransformer
        self.model=SentenceTransformer(model_id,revision=revision,trust_remote_code=False,device='cpu')
        self.identity=f'{model_id}@{revision}'
        self.dimensions=dimensions
        if self.model.get_sentence_embedding_dimension()!=dimensions:
            raise RetrievalError('loaded embedding dimensions disagree with configuration')
    def encode(self,text):
        return self.model.encode(text,normalize_embeddings=True).tolist()

class DocumentRAG:
    def __init__(self, client, principal: Principal, encoder: Encoder | None=None,
                 collection='academy_rag_v1', min_score=0.25):
        from qdrant_client import models
        if not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}',collection): raise RetrievalError('invalid collection')
        if not -1 <= min_score <= 1: raise RetrievalError('invalid cosine score threshold')
        self.client=client; self.models=models; self.principal=principal
        self.encoder=encoder or HashEmbedding(); self.collection=collection; self.min_score=min_score
        if not self.client.collection_exists(collection):
            self.client.create_collection(collection,vectors_config=models.VectorParams(size=self.encoder.dimensions,distance=models.Distance.COSINE))
        info=self.client.get_collection(collection)
        params=info.config.params.vectors
        if getattr(params,'size',None)!=self.encoder.dimensions or str(getattr(params,'distance','')).lower() not in ('cosine','distance.cosine'):
            raise RetrievalError('collection vector configuration differs from encoder')

    @classmethod
    def service(cls, url, principal, encoder=None, collection='academy_rag_v1', api_key=None):
        """Connect to an explicitly configured Qdrant HTTP service, not local mode."""
        from qdrant_client import QdrantClient
        parsed=urlsplit(url)
        if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('','/'):
            raise RetrievalError('Qdrant service requires a bare explicit HTTP origin')
        client=QdrantClient(url=url,api_key=api_key,timeout=5)
        return cls(client,principal,encoder,collection)

    def _filter(self, document_id=None):
        must=[self.models.FieldCondition(key='tenant',match=self.models.MatchValue(value=self.principal.tenant)),
              self.models.FieldCondition(key='encoder',match=self.models.MatchValue(value=self.encoder.identity))]
        if document_id is not None: must.append(self.models.FieldCondition(key='document_id',match=self.models.MatchValue(value=document_id)))
        return self.models.Filter(must=must)

    def ingest(self, document_id, text, source_uri, replace=False):
        self.principal.require('rag:write')
        if not re.fullmatch(r'[a-zA-Z0-9_.-]{1,100}',document_id) or not isinstance(text,str) or not text.strip() or len(text)>50000:
            raise RetrievalError('invalid bounded document')
        parsed=urlsplit(source_uri)
        if parsed.scheme not in ('https','http','academy') or parsed.username or parsed.password or len(source_uri)>1000:
            raise RetrievalError('invalid source provenance URI')
        digest=sha256(text.encode()).hexdigest()
        old=self.client.scroll(self.collection,scroll_filter=self._filter(document_id),limit=1,with_payload=True)[0]
        if old:
            if old[0].payload.get('document_sha256')==digest:
                return {'document_id':document_id,'duplicate':True,'document_sha256':digest,'indexed':False}
            if not replace: raise RetrievalError('document ID conflict; explicit replace required')
        chunks=[]
        # Fixed character windows retain exact offsets and overlap; deterministic IDs.
        for start in range(0,len(text),640):
            excerpt=text[start:start+800]
            if not excerpt.strip(): continue
            chunk_id=str(uuid.uuid5(uuid.NAMESPACE_URL,f'{self.principal.tenant}:{document_id}:{start}:{digest}'))
            payload={'tenant':self.principal.tenant,'document_id':document_id,'chunk_id':chunk_id,
                     'source_uri':source_uri,'document_sha256':digest,'chunk_sha256':sha256(excerpt.encode()).hexdigest(),
                     'start':start,'end':start+len(excerpt),'text':excerpt,'encoder':self.encoder.identity,
                     'ingested_at':datetime.now(timezone.utc).isoformat()}
            vector=self.encoder.encode(excerpt)
            if len(vector)!=self.encoder.dimensions or any(type(x) not in (int,float) or not math.isfinite(x) for x in vector):
                raise RetrievalError('encoder returned invalid vector')
            chunks.append(self.models.PointStruct(id=chunk_id,vector=vector,payload=payload))
        self.client.upsert(self.collection,points=chunks,wait=True)
        if old:
            # Preserve old chunks until the complete replacement was acknowledged.
            # This is two service requests, not an advertised cross-request transaction.
            # A cleanup timeout remains uncertain and must not trigger blind replay.
            stale=self._filter(document_id)
            stale.must_not=[self.models.FieldCondition(key='document_sha256',match=self.models.MatchValue(value=digest))]
            self.client.delete(self.collection,self.models.FilterSelector(filter=stale),wait=True)
        return {'document_id':document_id,'document_sha256':digest,'chunks':len(chunks),'duplicate':False,'indexed':True,'encoder':self.encoder.identity}

    def retrieve(self, query, limit=5):
        self.principal.require('rag:read')
        if not isinstance(query,str) or not query.strip() or len(query)>500 or type(limit) is not int or not 1<=limit<=10:
            raise RetrievalError('invalid bounded query')
        vector=self.encoder.encode(query)
        if len(vector)!=self.encoder.dimensions or any(not math.isfinite(x) for x in vector): raise RetrievalError('invalid query vector')
        result=self.client.query_points(self.collection,query=vector,query_filter=self._filter(),limit=limit,score_threshold=self.min_score)
        return {'query':query,'encoder':self.encoder.identity,'matches':[{'score':p.score,**p.payload} for p in result.points],
                'insufficient_evidence':not result.points}

    def delete(self,document_id):
        self.principal.require('rag:write')
        if not re.fullmatch(r'[a-zA-Z0-9_.-]{1,100}',document_id): raise RetrievalError('invalid document ID')
        self.client.delete(self.collection,self.models.FilterSelector(filter=self._filter(document_id)),wait=True)
        return {'document_id':document_id,'deleted':True}
    def close(self): self.client.close()
