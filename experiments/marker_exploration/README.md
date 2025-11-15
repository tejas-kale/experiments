# EPUB → Markdown Converter

Utility script `epub_to_md.py` turns an EPUB into per-chapter HTML, PDF, and Markdown artifacts using ebooklib for spine traversal, WeasyPrint for HTML→PDF, and Marker for PDF→Markdown.

## Prerequisites
- Python 3.10+.
- Python deps (already installed in this environment): `ebooklib`, `beautifulsoup4`, `marker-pdf`, `weasyprint`.
- WeasyPrint native deps (install via your package manager if missing): Cairo, Pango, GDK-PixBuf, libffi, and suitable fonts.
- Marker downloads OCR/vision checkpoints on first use; ensure enough disk space and network access. Optional LLM features require `GOOGLE_API_KEY`.

Quick install command if you are setting up a new env:

```bash
pip install ebooklib beautifulsoup4 marker-pdf weasyprint
```

## Usage

```bash
python epub_to_md.py <path/to/book.epub> <output_dir> [options]
```

Helpful flags:
- `--verbose` – extra logging.
- `--clean-output` – wipe the target directory before writing.
- `--skip-existing` – leave chapters whose Markdown already exists.
- `--stop-on-error` – abort on the first conversion failure.
- `--include-front-matter` – also convert cover/titlepage/toc sections (skipped by default).
- `--cleanup-non-md` – delete intermediate HTML/PDF/JSON artifacts, leaving Markdown (and any images) intact.
- `--use-llm` – enable Marker LLM processors (needs `GOOGLE_API_KEY`).
- `--attention-implementation {sdpa,flash_attention_2,eager}` – override Surya attention backend if you need deterministic CPU runs.

Example using the bundled novel:

```bash
python epub_to_md.py "<book>.epub" <output_folder> --clean-output --verbose
```

The command writes `<nn>_<chapter>.html/.pdf/.md` files and `<nn>_<chapter>.metadata.json` for Marker metadata. Logs report chapter-level progress; failures are surfaced with stack traces and the offending chapter title.

## Troubleshooting
- `Cannot resolve dependency for parameter: recognition_model`: ensure you are running the updated script, which now provisions Marker models through `marker.models.create_model_dict`.
- WeasyPrint complains about missing libraries: install Cairo/Pango/Pixman packages for your OS, and ensure fonts are available (e.g., `sudo apt install fonts-noto-core libpango-1.0-0 libcairo2` on Debian/Ubuntu).
- Marker download failures: rerun with `--verbose` to see the remote URL being fetched, or pre-download artifacts via the `MARKER_CACHE_DIR` environment variable per the Marker README.