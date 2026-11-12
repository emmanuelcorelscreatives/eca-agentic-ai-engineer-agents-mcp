"""Actual optional pypdf extraction; new text is unapproved by default."""
import argparse
import json
from pathlib import Path


def extract_profile(path, reader_factory=None):
    path=Path(path)
    if not path.is_file() or path.suffix.lower()!='.pdf':
        raise ValueError('existing PDF file required')
    if reader_factory is None:
        from pypdf import PdfReader
        reader_factory=PdfReader
    reader=reader_factory(str(path))
    if reader.is_encrypted:
        raise ValueError('encrypted input needs an explicit separate unlock workflow')
    sections=[]
    for index,page in enumerate(reader.pages,1):
        text=' '.join((page.extract_text() or '').split())
        if text:
            sections.append({'id':f'{path.stem}-page-{index}','title':f'{path.stem} page {index}','text':text,'approved':False})
    if not sections:
        raise ValueError('no extractable text: use reviewed OCR for image-only documents')
    return {'source':path.name,'status':'human_source_approval_required','sections':sections}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('pdf');args=parser.parse_args()
    print(json.dumps(extract_profile(args.pdf),indent=2))
