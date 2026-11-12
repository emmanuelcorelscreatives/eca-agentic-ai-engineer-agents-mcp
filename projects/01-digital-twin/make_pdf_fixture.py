"""Generate genuine synthetic resume/portfolio PDFs from versioned UTF-8 text.

No binaries are generated on import. The CLI writes new fixtures/generated;
it never overwrites the retained original fixtures/synthetic-resume.pdf.
"""
import argparse
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def make_pdf(destination):
    """Retain the original dependency-free ASCII fixture API for old callers."""
    text = 'SYNTHETIC PROFILE: Amara Okoye builds Python and SQLite reporting tools.'
    stream = f'BT /F1 12 Tf 50 750 Td ({text}) Tj ET'.encode('ascii')
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>', b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>', b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>', b'<< /Length ' + str(len(stream)).encode() + b' >>\nstream\n' + stream + b'\nendstream']
    data = bytearray(b'%PDF-1.4\n')
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data.extend(f'{index} 0 obj\n'.encode() + obj + b'\nendobj\n')
    start = len(data)
    data.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
    for offset in offsets[1:]:
        data.extend(f'{offset:010d} 00000 n \n'.encode())
    data.extend(f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode())
    Path(destination).write_bytes(data)


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _write_unicode_pdf(path, source_text, font_path):
    try:
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError as exc:
        raise RuntimeError('Two-document Unicode fixture generation requires optional reportlab') from exc
    name = 'AcademyFixture' + _sha(font_path.read_bytes())[:16]
    if name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(name, str(font_path)))
    font = pdfmetrics.getFont(name)
    # A missing glyph must fail rather than silently produce tofu in a lesson.
    missing = sorted({ch for ch in source_text if not ch.isspace() and ord(ch) not in font.face.charToGlyph})
    if missing:
        raise ValueError(f'font lacks required glyphs: {missing!r}')
    pdf = canvas.Canvas(str(path), pagesize=(612, 792), invariant=1, pageCompression=1, pdfVersion=(1, 4))
    pdf.setTitle('Synthetic Academy practice profile — Amara Okoye')
    pdf.setAuthor('Emmanuel Corels Academy — fictional practice materials')
    pdf.setFont(name, 11)
    y = 748
    for line in source_text.splitlines():
        if '\t' in line:
            raise ValueError('source contains tabs; replace them with explicit spaces')
        if pdfmetrics.stringWidth(line, name, 11) > 516:
            raise ValueError('source line exceeds page width; wrap it explicitly in the UTF-8 source')
        if y < 48:
            pdf.showPage()
            pdf.setFont(name, 11)
            y = 748
        pdf.drawString(48, y, line)
        y -= 16
    pdf.save()


def generate_documents(output_dir, font_path):
    """Write both documents and actual full-SHA manifest to a NEW directory."""
    output_dir, font_path = Path(output_dir), Path(font_path)
    if not font_path.is_file():
        raise ValueError('a readable Unicode TrueType font is required')
    # Validate both sources before making any document. This remains synthetic
    # data, not an assertion about the real instructor's professional history.
    sources = [(kind, BASE / 'fixtures' / f'{kind}-source.txt') for kind in ('resume', 'portfolio')]
    prepared = [(kind, path, path.read_bytes()) for kind, path in sources]
    for _, _, data in prepared:
        data.decode('utf-8', errors='strict')
    output_dir.mkdir(parents=True, exist_ok=False)
    documents = []
    for kind, source, data in prepared:
        output = output_dir / f'synthetic-{kind}.pdf'
        _write_unicode_pdf(output, data.decode('utf-8'), font_path)
        documents.append({
            'kind': kind,
            'source_path': f'fixtures/{source.name}',
            'source_sha256': _sha(data),
            'source_size_bytes': len(data),
            'pdf_path': output.name,
            'pdf_sha256': _sha(output.read_bytes()),
            'pdf_size_bytes': output.stat().st_size,
        })
    manifest = {
        'schema_version': 1,
        'status': 'generated_not_independently_verified',
        'synthetic': True,
        'persona': 'Amara Okoye — fictional Academy practice persona',
        'font': {'filename': font_path.name, 'sha256': _sha(font_path.read_bytes())},
        'generator_sha256': _sha(Path(__file__).read_bytes()),
        'documents': documents,
        'pending': ['actual pypdf extraction and source-text comparison', 'independent rendered-page inspection', 'human source approval'],
    }
    (output_dir / 'document-provenance.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=BASE / 'fixtures/generated')
    parser.add_argument('--font', type=Path, required=True, help='licensed local Unicode TrueType font file')
    args = parser.parse_args()
    print(json.dumps(generate_documents(args.output_dir, args.font), ensure_ascii=False, indent=2))
