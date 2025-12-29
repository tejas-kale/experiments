# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a personal experiments repository containing various AI-coded tools, data science projects, and exploratory work across different domains. Each experiment is self-contained within its own subdirectory under `experiments/`.

## Environment

**Python Version**: 3.11 (specified in `.python-version`)
**Package Manager**: uv
**Virtual Environment**: `.venv` (located in repository root)

### Virtual Environment Setup

```bash
# Create virtual environment (already exists at .venv)
uv venv

# Activate virtual environment
source .venv/bin/activate
```

## Repository Structure

The repository follows a flat structure where each experiment is isolated:

```
experiments/
├── indian_health_insurance_assistant/   # CLI tool for health insurance guidance
├── marker_exploration/                  # EPUB to Markdown conversion utility
├── personal_finance/                    # Personal finance data (db/ and raw/)
├── retail_labour_demand/                # Retail labor demand analysis with CSV data
├── ai_model_exploration/                # AI model experiments
└── xg_graph/                           # Graph experiments
```

Individual experiments may have their own `CLAUDE.md`, `README.md`, and `requirements.txt` files. Always check for experiment-specific documentation before making changes.

## Working with Individual Experiments

### 1. Indian Health Insurance Assistant (`experiments/indian_health_insurance_assistant/`)

**Type**: CLI application (Work in Progress)
**Tech Stack**: Python 3.11+, Rich (terminal UI)
**Purpose**: Interactive CLI for navigating Indian health insurance options

**Key Files**:
- `cli.py`: Main entry point with banner display and chat loop
- `requirements.txt`: Dependencies (Rich library)
- `CLAUDE.md`: Detailed project-specific instructions
- `README.md`: User documentation and testing scenarios

**Running**:
```bash
cd experiments/indian_health_insurance_assistant
source ../../.venv/bin/activate  # Activate root venv
uv pip install -r requirements.txt
python cli.py
```

**Architecture Notes**:
- Simple CLI with placeholder responses (WIP status)
- Uses Rich library for formatted terminal output
- Exit commands: `exit`, `quit`, Ctrl+C, Ctrl+D
- Future: Will integrate with policy databases and AI-powered recommendations

### 2. Marker Exploration (`experiments/marker_exploration/`)

**Type**: Document conversion utility
**Tech Stack**: Python 3.10+, ebooklib, WeasyPrint, marker-pdf
**Purpose**: Convert EPUB files to per-chapter Markdown using OCR and vision models

**Key Files**:
- `epub_to_md.py`: Main conversion script
- `README.md`: Usage instructions and troubleshooting

**Running**:
```bash
cd experiments/marker_exploration
python epub_to_md.py <path/to/book.epub> <output_dir> [options]
```

**Key Options**:
- `--verbose`: Extra logging
- `--clean-output`: Wipe target directory first
- `--skip-existing`: Skip chapters with existing Markdown
- `--stop-on-error`: Abort on first failure
- `--cleanup-non-md`: Delete intermediate HTML/PDF/JSON artifacts
- `--use-llm`: Enable LLM processors (requires `GOOGLE_API_KEY`)
- `--attention-implementation {sdpa,flash_attention_2,eager}`: Override attention backend

**Architecture Notes**:
- Pipeline: EPUB → HTML (per chapter) → PDF → Markdown
- Uses ebooklib for EPUB spine traversal
- WeasyPrint for HTML→PDF conversion (requires Cairo, Pango, GDK-PixBuf)
- Marker for PDF→Markdown with OCR/vision models
- Downloads OCR checkpoints on first use
- Skips front matter (cover, titlepage, toc) by default

### 3. Retail Labour Demand (`experiments/retail_labour_demand/`)

**Type**: Data analysis project
**Purpose**: Analyze retail labor demand patterns

**Data Files**:
- `data/labour_productivity.csv`: Labour productivity metrics
- `data/historical_sales_data/`: Kaggle historical retail sales dataset
  - `Features data set.csv`
  - `sales data-set.csv`
  - `stores data-set.csv`

### 4. Personal Finance (`experiments/personal_finance/`)

**Type**: Data project
**Structure**:
- `db/`: Database files
- `raw/`: Raw data files

## Development Guidelines

### Adding New Experiments

1. Create a new subdirectory under `experiments/`
2. Include a `README.md` with usage instructions
3. Include `requirements.txt` for Python dependencies (if applicable)
4. Optionally include `CLAUDE.md` for project-specific instructions
5. Keep experiments self-contained and isolated

### Dependency Management

- Use `uv` as the package manager (NEVER execute `uv` commands directly)
- If new packages are needed, notify Tejas to install them
- Each experiment can have its own `requirements.txt`
- The root `.venv` can be used for experiments, or experiments can create their own virtual environments

### Data Files

- CSV data files are stored within experiment directories
- Personal data is kept in experiment-specific subdirectories (`db/`, `raw/`)
- No specific data versioning or tracking is enforced

## Project-Specific Instructions

When working on a specific experiment:
1. **Always check for experiment-specific `CLAUDE.md` first** - it takes precedence
2. Read the experiment's `README.md` for context and usage
3. Respect the isolation of each experiment
4. Don't make cross-experiment changes without explicit permission

## Notes

- This is a personal repository for experimentation and learning
- Each experiment is at a different stage of development
- Some experiments are WIP with placeholder functionality
- Focus on simplicity and clarity over premature optimization
- Git branch naming follows the pattern: `claude/<description>-<ID>`
