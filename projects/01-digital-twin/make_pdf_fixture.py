"""Create a genuine one-page synthetic PDF without third-party dependencies."""
from pathlib import Path

def make_pdf(destination):
    text='SYNTHETIC PROFILE: Amara Okoye builds Python and SQLite reporting tools.'
    stream=f'BT /F1 12 Tf 50 750 Td ({text}) Tj ET'.encode('ascii')
    objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',b'<< /Length '+str(len(stream)).encode()+b' >>\nstream\n'+stream+b'\nendstream']
    data=bytearray(b'%PDF-1.4\n');offsets=[0]
    for index,obj in enumerate(objects,1):
        offsets.append(len(data));data.extend(f'{index} 0 obj\n'.encode()+obj+b'\nendobj\n')
    start=len(data);data.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
    for offset in offsets[1:]:data.extend(f'{offset:010d} 00000 n \n'.encode())
    data.extend(f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode())
    Path(destination).write_bytes(data)

if __name__=='__main__':make_pdf(Path(__file__).parent/'fixtures/synthetic-resume.pdf')
