"""Extract PDF text and retain exact input/page provenance; never approve a source.

pypdf is imported only on the real extraction path. ``reader_factory`` remains
available for isolated tests and adapters using the original two-argument API.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path


class PDFIngestionError(ValueError):
    """Actionable input failure with a stable code for UI and batch callers."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _clean_text(raw):
    # Keep Unicode, paragraph boundaries and line order. Only normalize line
    # endings and horizontal layout whitespace; raw_text remains byte-for-byte
    # equivalent to the extractor's Unicode string after UTF-8 encoding.
    lines = raw.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    return '\n'.join(re.sub(r'[^\S\n]+', ' ', line).strip() for line in lines).strip('\n')


def extract_profile(path, reader_factory=None):
    path = Path(path)
    if not path.is_file() or path.suffix.lower() != '.pdf':
        raise PDFIngestionError('invalid_input', 'existing PDF file required')
    data = path.read_bytes()
    if not data.startswith(b'%PDF-'):
        raise PDFIngestionError('corrupt_pdf', 'input lacks a PDF header; repair or replace the document')
    if reader_factory is None:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError('PDF extraction requires the optional pypdf dependency') from exc
        reader_factory = PdfReader
    try:
        reader = reader_factory(str(path))
        if reader.is_encrypted:
            raise PDFIngestionError('encrypted_pdf', 'encrypted input needs an explicit separate unlock workflow')
        pages = list(reader.pages)
    except PDFIngestionError:
        raise
    except Exception as exc:
        raise PDFIngestionError('corrupt_pdf', 'PDF could not be parsed; repair or replace it before ingestion') from exc
    if not pages:
        raise PDFIngestionError('no_pages', 'PDF contains no pages; supply a valid text document')
    sections, page_records = [], []
    document_sha = _sha(data)
    for index, page in enumerate(pages, 1):
        try:
            raw = page.extract_text()
        except Exception as exc:
            raise PDFIngestionError('page_extraction_failed', f'page {index} extraction failed; no partial result was approved') from exc
        if raw is None:
            raw = ''
        if not isinstance(raw, str):
            raise PDFIngestionError('invalid_extractor_output', f'page {index} extractor must return text or None')
        text = _clean_text(raw)
        page_record = {
            'page': index,
            'raw_text': raw,
            'raw_text_utf8_sha256': _sha(raw.encode('utf-8')),
            'text': text,
            'text_utf8_sha256': _sha(text.encode('utf-8')),
            # This hashes page text, not original compressed PDF page bytes.
            'status': 'extracted' if text else 'no_extractable_text_review_required',
        }
        page_records.append(page_record)
        if text:
            sections.append({
                'id': f'{path.stem}-page-{index}',
                'title': f'{path.stem} page {index}',
                'text': text,
                'approved': False,
                'provenance': {
                    'document_sha256': document_sha,
                    'page': index,
                    'raw_text_utf8_sha256': page_record['raw_text_utf8_sha256'],
                    'text_utf8_sha256': page_record['text_utf8_sha256'],
                },
            })
    if not sections:
        raise PDFIngestionError('no_extractable_text', 'no extractable text: use separately reviewed OCR for scanned/image-only documents')
    return {
        'schema_version': 2,
        'source': path.name,
        'document_sha256': document_sha,
        'size_bytes': len(data),
        'page_count': len(pages),
        'status': 'human_source_approval_required',
        'incomplete_text_extraction': any(not p['text'] for p in page_records),
        'warnings': [f"page {p['page']}: no text; inspect for scanned, blank or unsupported content" for p in page_records if not p['text']],
        'pages': page_records,
        'sections': sections,
    }


def export_profile(result, destination):
    """Export exact raw text and structured unapproved sections, with file hashes.

    A new directory is required so two extractions cannot silently replace one
    another. JSON preserves Unicode; page text in raw-pages.txt is separated by
    a form-feed character, documented in the manifest.
    """
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    payloads = {
        'extraction.json': (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8'),
        'sections.json': (json.dumps(result['sections'], ensure_ascii=False, indent=2) + '\n').encode('utf-8'),
        'raw-pages.txt': '\f'.join(p['raw_text'] for p in result['pages']).encode('utf-8'),
    }
    for name, payload in payloads.items():
        (destination / name).write_bytes(payload)
    manifest = {
        'schema_version': 1,
        'document_sha256': result['document_sha256'],
        'source': result['source'],
        'approval': 'not_approved',
        'raw_page_separator': 'U+000C FORM FEED; see extraction.json for unambiguous per-page boundaries',
        'files': [{'path': name, 'sha256': _sha(payload), 'size_bytes': len(payload)} for name, payload in payloads.items()],
    }
    (destination / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf')
    parser.add_argument('--output-dir', type=Path, help='new directory for provenance and raw-text exports')
    args = parser.parse_args()
    try:
        result = extract_profile(args.pdf)
        if args.output_dir:
            export_profile(result, args.output_dir)
    except PDFIngestionError as exc:
        parser.exit(2, f'{exc.code}: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
