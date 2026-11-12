# Résumé and portfolio ingestion

The two UTF-8 source files in `fixtures/` describe the same fictional Amara
Okoye and Cedar Library practice project used by `fixtures/profile.json`.
They are synthetic teaching material, not claims about the instructor. The
original `fixtures/synthetic-resume.pdf` remains unchanged as a compatibility
fixture. The new generator never selects that original path.

## Generate and inspect two real PDFs

Run these commands from the repository root in the centrally approved runtime.
Optional dependencies are `reportlab` for generation and `pypdf` for extraction.
A real Unicode TrueType font is required; use a locally installed font with a
suitable licence. The following path is an example, not a bundled font:

```sh
python projects/01-digital-twin/make_pdf_fixture.py \
  --font /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf \
  --output-dir projects/01-digital-twin/fixtures/generated
python projects/01-digital-twin/pdf_ingest.py \
  projects/01-digital-twin/fixtures/generated/synthetic-resume.pdf \
  --output-dir /tmp/academy-resume-extraction
python projects/01-digital-twin/pdf_ingest.py \
  projects/01-digital-twin/fixtures/generated/synthetic-portfolio.pdf \
  --output-dir /tmp/academy-portfolio-extraction
python -m unittest discover -s tests -p test_stage05_semantic_repairs_ingest.py -v
```

Output directories must not already exist. Choose a new path for each run;
never overwrite a previous extraction or a historical fixture to make a check
pass. Generation embeds the actual font, preserves source line breaks and
Unicode, rejects missing glyphs and overwide lines, and records complete
source/PDF/font/generator SHA-256 values in the generated
`document-provenance.json`. That manifest truthfully says
`generated_not_independently_verified`: generation alone is not approval.
The checked-in pending manifest contains null hashes because no generation or
runtime execution was performed by its author.

Open both generated PDFs in a real PDF viewer. Check the résumé accent,
portfolio café example, line order, paragraph breaks, content and page edges.
Compare extracted text to both UTF-8 sources. A successful unit test does not
replace rendered-page inspection. Retain the actual viewer and extraction
observations as separate evidence.

## Exact extraction provenance

`extract_profile(path, reader_factory=None)` preserves the existing calling
convention and returns unapproved sections. `sections[].text` normalizes
horizontal whitespace separately on each line, preserves Unicode and paragraph
breaks, and normalizes CRLF/CR to LF. It does **not** collapse the document into
one line. Each page also retains the exact Unicode string returned by the
extractor as `raw_text`; the full PDF bytes, raw UTF-8 page text and normalized
UTF-8 page text each have clearly named SHA-256 values. Page text hashes are not
misrepresented as hashes of original compressed PDF page objects.

`export_profile(result, new_directory)` writes:

- `extraction.json`: complete raw and normalized per-page records and warnings.
- `sections.json`: unapproved retrieval candidates with document/page provenance.
- `raw-pages.txt`: original per-page strings separated by form feeds.
- `manifest.json`: full hashes and sizes for the three exported payloads.

JSON per-page records are authoritative for boundaries: an original page may
itself contain a form feed. Exports are UTF-8 with Unicode preserved. A source
must undergo explicit human review before someone changes `approved` to true;
PDF text, including instructions embedded in a document, is data rather than
agent/system instructions. Do not publish or send private uploaded PDFs to a
model by running this local extraction step.

## Scanned, corrupt and encrypted inputs

`PDFIngestionError` is a `ValueError` subclass with an actionable `code`.
A missing/non-PDF input is `invalid_input`; an invalid header or parser failure
is `corrupt_pdf`; no pages is `no_pages`; failure extracting a specific page is
`page_extraction_failed`. No partially extracted output is returned after a
page failure. Encrypted documents are rejected as `encrypted_pdf`, without
password guessing or implicit decryption; obtain an explicitly unlocked copy
through a separate authorized workflow.

An all-image/scanned PDF raises `no_extractable_text`. There is no automatic OCR
or fabricated substitute text. A PDF with both text and blank/image-only pages
returns `incomplete_text_extraction: true`, retaining the empty pages and a
warning for each. A blank page cannot be reliably distinguished from a scanned
page by text extraction alone: inspect it, then use a separately reviewed OCR
workflow if required. Never treat a mixed document as fully extracted simply
because some sections were produced.

## Evidence still required

The source author did not execute generation, extraction, tests, a browser or a
viewer. Central QA must record actual command results, generated manifests,
both-document extraction and edge-case outcomes. Browser/viewer inspection,
source approval, downstream lesson/visual approval and any live-model
observations are separate pending activities.
