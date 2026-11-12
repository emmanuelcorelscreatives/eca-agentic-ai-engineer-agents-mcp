"""Run a real local Qdrant ingestion/retrieval and deletion exercise."""
import json
import tempfile
from .core import QdrantRetrieval, CapabilityCatalogue

def main():
    catalogue=CapabilityCatalogue()
    before=catalogue.tools(); catalogue.discover('rag',{'rag'}); after=catalogue.tools()
    with tempfile.TemporaryDirectory() as path:
        store=QdrantRetrieval(path)
        store.ingest('academy','approval-policy','Paper trading orders require explicit human approval before execution.')
        store.ingest('other-tenant','secret','A separate tenant document must never be returned to Academy.')
        rows=store.retrieve('academy','human approval')
        print(json.dumps({'initial_tools':before,'revealed_tools':after,'encoder':store.encoder.identity,'matches':rows},indent=2))
        store.close()
if __name__=='__main__': main()
