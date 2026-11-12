"""Authored Stage 5 ingestion checks; central QA must execute and retain results."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'projects/01-digital-twin'


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, PROJECT / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ingest = load('stage05_repaired_pdf_ingest', 'pdf_ingest.py')
generator = load('stage05_repaired_pdf_fixture', 'make_pdf_fixture.py')


class ProvenanceAndFailureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'profile.pdf'
        generator.make_pdf(self.path)

    def factory(self, *texts):
        return lambda _: SimpleNamespace(
            is_encrypted=False,
            pages=[SimpleNamespace(extract_text=lambda text=text: text) for text in texts],
        )

    def test_multiline_unicode_and_raw_bytes_are_retained(self):
        raw = '  Amara   Okoye\r\nRésumé — café\r\n\r\n  Python\tSQLite  '
        result = ingest.extract_profile(self.path, self.factory(raw))
        self.assertEqual(result['pages'][0]['raw_text'], raw)
        self.assertEqual(result['sections'][0]['text'], 'Amara Okoye\nRésumé — café\n\nPython SQLite')
        self.assertEqual(result['document_sha256'], hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertEqual(result['pages'][0]['raw_text_utf8_sha256'], hashlib.sha256(raw.encode('utf-8')).hexdigest())
        self.assertFalse(result['sections'][0]['approved'])
        self.assertEqual(result['status'], 'human_source_approval_required')

    def test_legacy_reader_factory_and_single_line_normalization(self):
        result = ingest.extract_profile(self.path, self.factory(' Amara   Python '))
        self.assertEqual(result['sections'][0]['text'], 'Amara Python')

    def test_mixed_image_and_text_pages_are_not_silently_dropped(self):
        result = ingest.extract_profile(self.path, self.factory('first page', None, 'third page'))
        self.assertEqual(result['page_count'], 3)
        self.assertTrue(result['incomplete_text_extraction'])
        self.assertEqual([section['provenance']['page'] for section in result['sections']], [1, 3])
        self.assertEqual(result['pages'][1]['raw_text'], '')
        self.assertEqual(len(result['warnings']), 1)

    def test_image_only_has_actionable_error(self):
        with self.assertRaises(ingest.PDFIngestionError) as caught:
            ingest.extract_profile(self.path, self.factory(None, '  '))
        self.assertEqual(caught.exception.code, 'no_extractable_text')

    def test_encrypted_never_attempts_page_access(self):
        class Encrypted:
            is_encrypted = True
            @property
            def pages(self):
                self.fail_if_read = True
                raise AssertionError('encrypted pages must not be read')
        with self.assertRaises(ingest.PDFIngestionError) as caught:
            ingest.extract_profile(self.path, lambda _: Encrypted())
        self.assertEqual(caught.exception.code, 'encrypted_pdf')

    def test_parser_failure_is_corrupt_pdf(self):
        def broken(_):
            raise OSError('unreadable xref')
        with self.assertRaises(ingest.PDFIngestionError) as caught:
            ingest.extract_profile(self.path, broken)
        self.assertEqual(caught.exception.code, 'corrupt_pdf')

    def test_bad_header_is_rejected_before_reader(self):
        self.path.write_bytes(b'not PDF bytes')
        def should_not_run(_):
            raise AssertionError('reader called for invalid header')
        with self.assertRaises(ingest.PDFIngestionError) as caught:
            ingest.extract_profile(self.path, should_not_run)
        self.assertEqual(caught.exception.code, 'corrupt_pdf')

    def test_page_failure_never_returns_partial_success(self):
        def fail():
            raise RuntimeError('damaged page stream')
        reader = SimpleNamespace(is_encrypted=False, pages=[SimpleNamespace(extract_text=lambda: 'usable'), SimpleNamespace(extract_text=fail)])
        with self.assertRaises(ingest.PDFIngestionError) as caught:
            ingest.extract_profile(self.path, lambda _: reader)
        self.assertEqual(caught.exception.code, 'page_extraction_failed')

    def test_exports_preserve_exact_raw_and_hash_all_payloads(self):
        result = ingest.extract_profile(self.path, self.factory('Résumé\n\nPortfolio', 'Café'))
        directory = Path(self.temp.name) / 'export'
        manifest = ingest.export_profile(result, directory)
        self.assertEqual((directory / 'raw-pages.txt').read_text(encoding='utf-8'), 'Résumé\n\nPortfolio\fCafé')
        self.assertEqual(json.loads((directory / 'extraction.json').read_text(encoding='utf-8')), result)
        for item in manifest['files']:
            payload = (directory / item['path']).read_bytes()
            self.assertEqual(item['sha256'], hashlib.sha256(payload).hexdigest())
            self.assertEqual(item['size_bytes'], len(payload))
        self.assertEqual(manifest['approval'], 'not_approved')
        with self.assertRaises(FileExistsError):
            ingest.export_profile(result, directory)

    def test_pending_source_manifest_does_not_claim_generation(self):
        manifest = json.loads((PROJECT / 'fixtures/document-provenance.json').read_text(encoding='utf-8'))
        self.assertEqual(len(manifest['documents']), 2)
        for document in manifest['documents']:
            self.assertIsNone(document['pdf_sha256'])
            self.assertTrue((PROJECT / document['source_path']).is_file())


class RealTwoDocumentPDFTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import pypdf
            import reportlab
        except ImportError as exc:
            raise unittest.SkipTest(f'actual PDF suite requires pypdf and reportlab: {exc}')
        cls.pypdf = pypdf
        cls.font = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        if not cls.font.is_file():
            raise unittest.SkipTest('actual Unicode PDF suite requires a real DejaVuSans.ttf font')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / 'generated'
        self.manifest = generator.generate_documents(self.output, self.font)

    def test_both_real_documents_extract_their_actual_source_facts(self):
        for document in self.manifest['documents']:
            path = self.output / document['pdf_path']
            source = (PROJECT / document['source_path']).read_text(encoding='utf-8')
            result = ingest.extract_profile(path)
            text = '\n'.join(page['raw_text'] for page in result['pages'])
            for line in source.splitlines():
                if line:
                    self.assertIn(line, text)
            self.assertIn('Amara Okoye', text)
            self.assertIn('Cedar Library', text)
            self.assertFalse(result['incomplete_text_extraction'])
            self.assertTrue(all(not section['approved'] for section in result['sections']))
        resume = ingest.extract_profile(self.output / 'synthetic-resume.pdf')
        portfolio = ingest.extract_profile(self.output / 'synthetic-portfolio.pdf')
        self.assertIn('RÉSUMÉ', resume['pages'][0]['raw_text'])
        self.assertIn('café', portfolio['pages'][0]['raw_text'])

    def test_full_generated_manifest_hashes_actual_pdf_source_and_font(self):
        for document in self.manifest['documents']:
            self.assertEqual(document['source_sha256'], hashlib.sha256((PROJECT / document['source_path']).read_bytes()).hexdigest())
            self.assertEqual(document['pdf_sha256'], hashlib.sha256((self.output / document['pdf_path']).read_bytes()).hexdigest())
        self.assertEqual(self.manifest['font']['sha256'], hashlib.sha256(self.font.read_bytes()).hexdigest())
        self.assertEqual(self.manifest['status'], 'generated_not_independently_verified')
        with self.assertRaises(FileExistsError):
            generator.generate_documents(self.output, self.font)

    def test_real_blank_and_encrypted_inputs_rejected(self):
        blank = self.pypdf.PdfWriter()
        blank.add_blank_page(width=612, height=792)
        blank_path = Path(self.temp.name) / 'blank.pdf'
        with blank_path.open('wb') as handle:
            blank.write(handle)
        with self.assertRaises(ingest.PDFIngestionError) as caught:
            ingest.extract_profile(blank_path)
        self.assertEqual(caught.exception.code, 'no_extractable_text')
        encrypted = self.pypdf.PdfWriter()
        encrypted.add_page(self.pypdf.PdfReader(str(self.output / 'synthetic-resume.pdf')).pages[0])
        encrypted.encrypt('synthetic-test-only')
        encrypted_path = Path(self.temp.name) / 'encrypted.pdf'
        with encrypted_path.open('wb') as handle:
            encrypted.write(handle)
        with self.assertRaises(ingest.PDFIngestionError) as caught:
            ingest.extract_profile(encrypted_path)
        self.assertEqual(caught.exception.code, 'encrypted_pdf')

    def test_real_corrupt_pdf_rejected(self):
        corrupt = Path(self.temp.name) / 'corrupt.pdf'
        corrupt.write_bytes(b'%PDF-1.4\nnot a valid PDF object graph\n%%EOF')
        with self.assertRaises(ingest.PDFIngestionError) as caught:
            ingest.extract_profile(corrupt)
        self.assertEqual(caught.exception.code, 'corrupt_pdf')


if __name__ == '__main__':
    unittest.main()
