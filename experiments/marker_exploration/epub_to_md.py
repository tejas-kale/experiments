from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup
from ebooklib import epub
from weasyprint import HTML

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.settings import settings as marker_settings


LOGGER = logging.getLogger("epub_to_md")
FRONT_MATTER_TOKENS = ("cover", "titlepage", "nav", "toc")
ARTIFACT_SUFFIXES = {".pdf", ".html", ".htm", ".json"}


@dataclass(slots=True)
class Chapter:
    order: int
    title: str
    safe_title: str
    html_bytes: bytes
    source_name: str


def normalise_title(title: str) -> str:
    sanitized = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-"))
    sanitized = sanitized.strip()
    return sanitized.replace(" ", "_")


def looks_like_front_matter(name: str) -> bool:
    lowered = name.lower()
    return any(token in lowered for token in FRONT_MATTER_TOKENS)


def extract_chapters(epub_path: Path, include_front_matter: bool = False) -> List[Chapter]:
    book = epub.read_epub(str(epub_path))
    allowed_types = {"application/xhtml+xml", "text/html"}
    chapters: List[Chapter] = []
    used_names: set[str] = set()

    for position, (idref, _) in enumerate(book.spine, start=1):
        item = book.get_item_with_id(idref)
        if item is None or item.media_type not in allowed_types:
            continue

        html_bytes = item.get_content()
        soup = BeautifulSoup(html_bytes, "html.parser")
        title_tag = soup.find(["h1", "h2", "title"])

        fallback_title = item.file_name or idref or f"chapter_{position}"
        if not include_front_matter and looks_like_front_matter(fallback_title):
            LOGGER.debug("Skipping front-matter item %s", fallback_title)
            continue

        title = title_tag.get_text(strip=True) if title_tag else fallback_title
        safe_title = normalise_title(title) or normalise_title(Path(fallback_title).stem)
        if not safe_title:
            safe_title = f"chapter_{position:02d}"

        unique = safe_title
        suffix = 1
        while unique in used_names:
            unique = f"{safe_title}_{suffix:02d}"
            suffix += 1
        used_names.add(unique)

        chapters.append(
            Chapter(
                order=len(chapters) + 1,
                title=title,
                safe_title=unique,
                html_bytes=html_bytes,
                source_name=item.file_name,
            )
        )

    LOGGER.info("Found %d chapter candidates", len(chapters))
    return chapters


def html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    try:
        html = HTML(filename=str(html_path), base_url=str(html_path.parent))
        html.write_pdf(str(pdf_path))
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"WeasyPrint failed for {html_path.name}") from exc


def build_marker_converter(use_llm: bool = False, attention: str | None = None) -> PdfConverter:
    artifact_dict = create_model_dict(
        device=marker_settings.TORCH_DEVICE_MODEL,
        dtype=marker_settings.MODEL_DTYPE,
        attention_implementation=attention,
    )
    config = {"use_llm": use_llm, "disable_tqdm": True}
    return PdfConverter(artifact_dict=artifact_dict, config=config)


def convert_pdf_with_marker(pdf_path: Path, converter: PdfConverter):
    return converter(str(pdf_path))


def write_metadata(metadata_path: Path, metadata: dict) -> None:
    try:
        with metadata_path.open("w", encoding="utf-8") as meta_file:
            json.dump(metadata, meta_file, indent=2, default=str)
    except TypeError:
        with metadata_path.open("w", encoding="utf-8") as meta_file:
            json.dump({}, meta_file)


def cleanup_artifacts(output_dir: Path) -> int:
    removed = 0
    for path in output_dir.iterdir():
        if not path.is_file():
            continue

        suffix = path.suffix.lower()
        name_lower = path.name.lower()
        if suffix in ARTIFACT_SUFFIXES or name_lower.endswith(".metadata.json"):
            path.unlink(missing_ok=True)
            removed += 1
    return removed


def configure_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s %(message)s")


def epub_to_markdown(
    epub_path: str | os.PathLike[str],
    output_dir: str | os.PathLike[str],
    *,
    stop_on_error: bool = False,
    skip_existing: bool = False,
    clean_output: bool = False,
    use_llm: bool = False,
    attention_implementation: str | None = None,
    include_front_matter: bool = False,
    cleanup_non_md: bool = False,
) -> tuple[int, int]:
    epub_path = Path(epub_path)
    out_dir = Path(output_dir)

    if clean_output and out_dir.exists():
        LOGGER.info("Cleaning output directory %s", out_dir)
        shutil.rmtree(out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    chapters = extract_chapters(epub_path, include_front_matter=include_front_matter)
    converter = build_marker_converter(use_llm=use_llm, attention=attention_implementation)

    successes = 0
    failures = 0

    for chapter in chapters:
        html_path = out_dir / f"{chapter.order:02d}_{chapter.safe_title}.html"
        pdf_path = out_dir / f"{chapter.order:02d}_{chapter.safe_title}.pdf"
        md_path = out_dir / f"{chapter.order:02d}_{chapter.safe_title}.md"
        meta_path = md_path.with_suffix(".metadata.json")

        if skip_existing and md_path.exists():
            LOGGER.info("Skipping %s (markdown already exists)", chapter.title)
            continue

        LOGGER.info("Processing chapter %s (%s)", chapter.order, chapter.title)
        try:
            with html_path.open("wb") as html_file:
                html_file.write(chapter.html_bytes)

            html_to_pdf(html_path, pdf_path)
            result = convert_pdf_with_marker(pdf_path, converter)

            with md_path.open("w", encoding="utf-8") as md_file:
                md_file.write(result.markdown)

            if getattr(result, "metadata", None):
                write_metadata(meta_path, result.metadata)

            successes += 1
        except Exception as exc:
            failures += 1
            LOGGER.exception("Failed to process '%s': %s", chapter.title, exc)
            if stop_on_error:
                raise
            continue

    if cleanup_non_md:
        removed = cleanup_artifacts(out_dir)
        LOGGER.info("Cleanup removed %d HTML/PDF/JSON artifacts", removed)

    LOGGER.info("Conversion complete: %d succeeded, %d failed", successes, failures)
    return successes, failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert an EPUB into per-chapter Markdown using WeasyPrint and Marker."
            " Requires WeasyPrint system deps and Marker OCR models."
        )
    )
    parser.add_argument("epub", help="Path to the input EPUB file")
    parser.add_argument("outdir", help="Directory for HTML/PDF/Markdown artifacts")
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Abort on the first chapter error instead of continuing",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip chapters whose Markdown output already exists",
    )
    parser.add_argument(
        "--clean-output",
        action="store_true",
        help="Delete the output directory before processing",
    )
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Enable Marker LLM-powered processors (requires GOOGLE_API_KEY)",
    )
    parser.add_argument(
        "--attention-implementation",
        choices=["sdpa", "flash_attention_2", "eager"],
        help="Optional attention backend override for Surya models",
    )
    parser.add_argument(
        "--include-front-matter",
        action="store_true",
        help="Process cover/titlepage/toc sections instead of skipping",
    )
    parser.add_argument(
        "--cleanup-non-md",
        action="store_true",
        help="Delete HTML/PDF/JSON artifacts after a run (keeps .md and images)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging output",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_logging(args.verbose)
    epub_to_markdown(
        args.epub,
        args.outdir,
        stop_on_error=args.stop_on_error,
        skip_existing=args.skip_existing,
        clean_output=args.clean_output,
        use_llm=args.use_llm,
        attention_implementation=args.attention_implementation,
        include_front_matter=args.include_front_matter,
        cleanup_non_md=args.cleanup_non_md,
    )


if __name__ == "__main__":
    main()
