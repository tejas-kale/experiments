# Cricket Database Project - Complete Implementation Plan

## Project Overview

**Objective**: Create a comprehensive cricket database in DuckDB containing international matches, IPL, and Indian domestic cricket (Ranji Trophy, Syed Mushtaq Ali, Vijay Hazare) with automated weekly rebuilds via GitHub Actions.

**Final Deliverable**: A single `cricket.duckdb` file containing all match and ball-by-ball data, downloadable and ready for analysis.

---

## Project Structure

```
cricket-database/
├── .github/
│   └── workflows/
│       └── rebuild-database.yml       # Weekly rebuild pipeline
├── src/
│   ├── __init__.py
│   ├── config.py                      # Configuration and constants
│   ├── downloaders/
│   │   ├── __init__.py
│   │   ├── cricsheet.py              # Download cricsheet data
│   │   └── espncricinfo.py           # Scrape ESPNcricinfo data
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── cricsheet_parser.py       # Parse cricsheet JSON
│   │   └── espncricinfo_parser.py    # Parse scraped data
│   ├── transformers/
│   │   ├── __init__.py
│   │   └── normalize.py              # Transform to unified schema
│   ├── database/
│   │   ├── __init__.py
│   │   ├── schema.py                 # DuckDB schema definitions
│   │   └── loader.py                 # Load data into DuckDB
│   └── pipeline/
│       ├── __init__.py
│       └── orchestrator.py           # Main pipeline orchestrator
├── data/                              # Git-ignored data directory
│   ├── raw/
│   │   ├── cricsheet/
│   │   └── espncricinfo/
│   ├── processed/
│   │   └── parquet/
│   └── cricket.duckdb                # Final database file
├── tests/
│   ├── __init__.py
│   ├── test_downloaders.py
│   ├── test_parsers.py
│   └── test_database.py
├── scripts/
│   └── build_database.py             # Main entry point
├── requirements.txt
├── .gitignore
├── README.md
└── pyproject.toml                    # Optional: uv project config
```

---

## Phase 1: Project Setup

### Task 1.1: Initialize Project Structure
- Create all directories as shown above
- Initialize git repository
- Create `.gitignore` with:
  ```
  data/
  *.duckdb
  *.duckdb.wal
  __pycache__/
  *.pyc
  .pytest_cache/
  .venv/
  venv/
  *.parquet
  *.zip
  *.json
  .env
  ```

### Task 1.2: Setup Dependencies
Create `requirements.txt`:
```txt
duckdb>=1.1.0
pandas>=2.0.0
pyarrow>=14.0.0
httpx>=0.27.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
tqdm>=4.66.0
python-dateutil>=2.8.0
pyyaml>=6.0
pytest>=8.0.0
```

### Task 1.3: Configuration File
Create `src/config.py`:
```python
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
PARQUET_DIR = PROCESSED_DATA_DIR / "parquet"
DB_PATH = DATA_DIR / "cricket.duckdb"

# Cricsheet URLs
CRICSHEET_BASE_URL = "https://cricsheet.org/downloads"
CRICSHEET_DOWNLOADS = {
    "all_json": f"{CRICSHEET_BASE_URL}/all_json.zip",
    # Add specific downloads if needed for faster processing
}

# ESPNcricinfo settings
ESPNCRICINFO_BASE_URL = "https://www.espncricinfo.com"
DOMESTIC_COMPETITIONS = {
    "ranji_trophy": {
        "series_ids": [1445824, 1383414, 1332913],  # Recent seasons
        "name": "Ranji Trophy"
    },
    "syed_mushtaq_ali": {
        "series_ids": [1440287, 1348024],
        "name": "Syed Mushtaq Ali Trophy"
    },
    "vijay_hazare": {
        "series_ids": [1440288, 1348025],
        "name": "Vijay Hazare Trophy"
    }
}

# Processing settings
BATCH_SIZE = 1000
MAX_WORKERS = 4
```

---

## Phase 2: Cricsheet Data Pipeline

### Task 2.1: Cricsheet Downloader
Create `src/downloaders/cricsheet.py`:

**Functionality:**
- Download all_json.zip from cricsheet.org
- Extract to `data/raw/cricsheet/`
- Handle resume capability (don't re-download if exists)
- Show progress bar with tqdm
- Validate download integrity

**Key functions:**
```python
def download_cricsheet_data(force_download: bool = False) -> Path:
    """Download and extract cricsheet data."""
    pass

def list_cricsheet_files(match_type: str = None) -> list[Path]:
    """List all JSON files, optionally filtered by match type."""
    pass
```

### Task 2.2: Cricsheet Parser
Create `src/parsers/cricsheet_parser.py`:

**Functionality:**
- Parse cricsheet JSON format (version 1.1.0)
- Extract match metadata (info section)
- Extract ball-by-ball data (innings section)
- Handle all match types: Test, ODI, T20I, IPL, BBL, etc.
- Handle edge cases: super overs, DLS method, no results

**Key functions:**
```python
def parse_match_file(json_path: Path) -> dict:
    """Parse a single cricsheet JSON file."""
    pass

def extract_match_info(match_data: dict) -> dict:
    """Extract match-level information."""
    pass

def extract_deliveries(match_data: dict, match_id: str) -> list[dict]:
    """Extract ball-by-ball delivery data."""
    pass
```

**Output schema for deliveries:**
```python
{
    "match_id": str,
    "innings": int,
    "batting_team": str,
    "bowling_team": str,
    "over": int,
    "ball": int,
    "batter": str,
    "bowler": str,
    "non_striker": str,
    "runs_batter": int,
    "runs_extras": int,
    "runs_total": int,
    "extra_type": str | None,
    "is_wicket": bool,
    "wicket_kind": str | None,
    "player_out": str | None,
    "fielders": list[str] | None
}
```

---

## Phase 3: ESPNcricinfo Scraper

### Task 3.1: ESPNcricinfo Downloader
Create `src/downloaders/espncricinfo.py`:

**Functionality:**
- Scrape match listings for domestic competitions
- Extract match IDs from series pages
- Download match JSON data (ESPNcricinfo provides JSON API)
- Implement rate limiting (1-2 requests per second)
- Cache downloaded data to avoid re-scraping

**Key functions:**
```python
def get_series_matches(series_id: int) -> list[int]:
    """Get all match IDs from a series."""
    pass

def download_match_data(match_id: int) -> dict:
    """Download match data from ESPNcricinfo."""
    pass

def scrape_domestic_competitions() -> None:
    """Scrape all configured domestic competitions."""
    pass
```

**ESPNcricinfo JSON API patterns:**
- Match page: `https://www.espncricinfo.com/series/{series_id}/match/{match_id}/full-scorecard`
- JSON endpoint: `https://hs-consumer-api.espncricinfo.com/v1/pages/match/home?lang=en&seriesId={series_id}&matchId={match_id}`

### Task 3.2: ESPNcricinfo Parser
Create `src/parsers/espncricinfo_parser.py`:

**Functionality:**
- Parse ESPNcricinfo JSON structure
- Extract match info (teams, venue, date, result)
- Extract ball-by-ball commentary
- Transform to unified schema (same as cricsheet output)
- Handle different JSON structures across match types

**Key functions:**
```python
def parse_espn_match(match_data: dict) -> dict:
    """Parse ESPNcricinfo match data."""
    pass

def extract_espn_deliveries(match_data: dict, match_id: str) -> list[dict]:
    """Extract deliveries from ESPN data."""
    pass
```

---

## Phase 4: Data Transformation

### Task 4.1: Schema Normalizer
Create `src/transformers/normalize.py`:

**Functionality:**
- Merge cricsheet and ESPNcricinfo data
- Ensure consistent schema
- Generate unique match IDs
- Handle duplicate detection
- Clean data (trim whitespace, normalize team names)
- Convert to pandas DataFrames
- Export to Parquet files

**Key functions:**
```python
def normalize_matches(cricsheet_matches: list[dict],
                      espn_matches: list[dict]) -> pd.DataFrame:
    """Combine and normalize match data."""
    pass

def normalize_deliveries(cricsheet_deliveries: list[dict],
                        espn_deliveries: list[dict]) -> pd.DataFrame:
    """Combine and normalize delivery data."""
    pass

def export_to_parquet(df: pd.DataFrame, output_path: Path) -> None:
    """Export DataFrame to Parquet with compression."""
    pass
```

---

## Phase 5: DuckDB Database Creation

### Task 5.1: Database Schema
Create `src/database/schema.py`:

**Define tables:**

```python
MATCHES_TABLE = """
CREATE TABLE IF NOT EXISTS matches (
    match_id VARCHAR PRIMARY KEY,
    season VARCHAR,
    match_date DATE,
    venue VARCHAR,
    city VARCHAR,
    country VARCHAR,
    match_type VARCHAR,
    competition VARCHAR,
    gender VARCHAR,
    team_type VARCHAR,
    balls_per_over INTEGER,
    team1 VARCHAR,
    team2 VARCHAR,
    toss_winner VARCHAR,
    toss_decision VARCHAR,
    winner VARCHAR,
    result_type VARCHAR,
    result_margin INTEGER,
    result_margin_type VARCHAR,
    player_of_match VARCHAR,
    umpire1 VARCHAR,
    umpire2 VARCHAR,
    tv_umpire VARCHAR,
    reserve_umpire VARCHAR,
    match_referee VARCHAR,
    data_source VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

DELIVERIES_TABLE = """
CREATE TABLE IF NOT EXISTS deliveries (
    delivery_id VARCHAR PRIMARY KEY,
    match_id VARCHAR,
    innings INTEGER,
    batting_team VARCHAR,
    bowling_team VARCHAR,
    over INTEGER,
    ball INTEGER,
    batter VARCHAR,
    bowler VARCHAR,
    non_striker VARCHAR,
    runs_batter INTEGER,
    runs_extras INTEGER,
    runs_total INTEGER,
    extra_type VARCHAR,
    is_wicket BOOLEAN,
    wicket_kind VARCHAR,
    player_out VARCHAR,
    fielders VARCHAR[],
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);
"""

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_match_date ON matches(match_date);",
    "CREATE INDEX IF NOT EXISTS idx_match_type ON matches(match_type);",
    "CREATE INDEX IF NOT EXISTS idx_competition ON matches(competition);",
    "CREATE INDEX IF NOT EXISTS idx_deliveries_match ON deliveries(match_id);",
    "CREATE INDEX IF NOT EXISTS idx_batter ON deliveries(batter);",
    "CREATE INDEX IF NOT EXISTS idx_bowler ON deliveries(bowler);",
    "CREATE INDEX IF NOT EXISTS idx_batting_team ON deliveries(batting_team);",
]
```

### Task 5.2: Database Loader
Create `src/database/loader.py`:

**Functionality:**
- Create DuckDB database
- Load Parquet files into DuckDB
- Create indexes
- Create helpful views for common queries
- Generate database statistics

**Key functions:**
```python
def create_database(db_path: Path) -> None:
    """Create DuckDB database with schema."""
    pass

def load_parquet_to_duckdb(parquet_path: Path,
                           table_name: str,
                           db_path: Path) -> None:
    """Load Parquet file into DuckDB table."""
    pass

def create_indexes(db_path: Path) -> None:
    """Create all indexes."""
    pass

def create_views(db_path: Path) -> None:
    """Create helpful analytical views."""
    pass
```

**Helpful views to create:**
```sql
-- Batting statistics view
CREATE VIEW IF NOT EXISTS batting_stats AS
SELECT
    batter,
    match_type,
    COUNT(DISTINCT match_id) as matches,
    COUNT(*) as balls_faced,
    SUM(runs_batter) as runs,
    SUM(CASE WHEN is_wicket THEN 1 ELSE 0 END) as dismissals,
    ROUND(AVG(runs_batter) * 100, 2) as strike_rate,
    SUM(CASE WHEN runs_batter = 4 THEN 1 ELSE 0 END) as fours,
    SUM(CASE WHEN runs_batter = 6 THEN 1 ELSE 0 END) as sixes
FROM deliveries
GROUP BY batter, match_type;

-- Bowling statistics view
CREATE VIEW IF NOT EXISTS bowling_stats AS
SELECT
    bowler,
    match_type,
    COUNT(DISTINCT match_id) as matches,
    COUNT(*) as balls_bowled,
    SUM(runs_total) as runs_conceded,
    SUM(CASE WHEN is_wicket THEN 1 ELSE 0 END) as wickets,
    ROUND(SUM(runs_total) * 1.0 / NULLIF(SUM(CASE WHEN is_wicket THEN 1 ELSE 0 END), 0), 2) as average,
    ROUND(AVG(runs_total) * 6, 2) as economy
FROM deliveries
GROUP BY bowler, match_type;
```

---

## Phase 6: Pipeline Orchestration

### Task 6.1: Main Orchestrator
Create `src/pipeline/orchestrator.py`:

**Functionality:**
- Coordinate all pipeline steps
- Handle errors gracefully
- Log progress
- Clean up temporary files
- Generate summary statistics

**Pipeline steps:**
```python
def run_pipeline(force_download: bool = False) -> None:
    """
    Execute the complete data pipeline.

    Steps:
    1. Download cricsheet data
    2. Download ESPNcricinfo data
    3. Parse cricsheet files
    4. Parse ESPNcricinfo files
    5. Normalize and merge data
    6. Export to Parquet
    7. Create DuckDB database
    8. Load Parquet into DuckDB
    9. Create indexes and views
    10. Generate summary report
    """
    pass
```

### Task 6.2: Main Entry Point
Create `scripts/build_database.py`:

```python
#!/usr/bin/env python3
"""Main script to build the cricket database."""

import argparse
import logging
from src.pipeline.orchestrator import run_pipeline

def main():
    parser = argparse.ArgumentParser(
        description="Build cricket database from multiple sources"
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Force re-download of all data"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    run_pipeline(force_download=args.force_download)

if __name__ == "__main__":
    main()
```

---

## Phase 7: Testing

### Task 7.1: Unit Tests
Create tests for each module:

**`tests/test_parsers.py`:**
- Test cricsheet JSON parsing
- Test ESPNcricinfo parsing
- Test edge cases (super overs, DLS, ties)

**`tests/test_database.py`:**
- Test schema creation
- Test data loading
- Test query performance
- Test data integrity

**`tests/test_downloaders.py`:**
- Test download functionality (with mocks)
- Test rate limiting
- Test error handling

### Task 7.2: Integration Test
Create end-to-end test with sample data:
- Use 10-20 sample matches
- Run complete pipeline
- Validate database contents
- Check data quality

---

## Phase 8: GitHub Actions Pipeline

### Task 8.1: Workflow Configuration
Create `.github/workflows/rebuild-database.yml`:

```yaml
name: Rebuild Cricket Database

on:
  schedule:
    # Run every Sunday at 2 AM UTC
    - cron: '0 2 * * 0'
  workflow_dispatch:  # Allow manual trigger

jobs:
  build-database:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt

      - name: Create data directories
        run: |
          mkdir -p data/raw data/processed

      - name: Run database build pipeline
        run: |
          python scripts/build_database.py --verbose

      - name: Compress database
        run: |
          gzip -k data/cricket.duckdb

      - name: Get current date
        id: date
        run: echo "date=$(date +'%Y-%m-%d')" >> $GITHUB_OUTPUT

      - name: Upload database as artifact
        uses: actions/upload-artifact@v4
        with:
          name: cricket-database-${{ steps.date.outputs.date }}
          path: |
            data/cricket.duckdb
            data/cricket.duckdb.gz
          retention-days: 90

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: db-${{ steps.date.outputs.date }}
          name: Cricket Database - ${{ steps.date.outputs.date }}
          body: |
            Automated weekly database rebuild

            ## Database Statistics
            - Build Date: ${{ steps.date.outputs.date }}
            - Source: Cricsheet + ESPNcricinfo

            ## Download
            - Download `cricket.duckdb.gz`
            - Decompress: `gunzip cricket.duckdb.gz`
            - Use with DuckDB CLI or Python
          files: |
            data/cricket.duckdb.gz
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Generate database stats
        run: |
          python -c "
          import duckdb
          con = duckdb.connect('data/cricket.duckdb')
          print('=== Database Statistics ===')
          print(f\"Total matches: {con.execute('SELECT COUNT(*) FROM matches').fetchone()[0]}")
          print(f\"Total deliveries: {con.execute('SELECT COUNT(*) FROM deliveries').fetchone()[0]}")
          print(f\"Match types: {con.execute('SELECT match_type, COUNT(*) FROM matches GROUP BY match_type').fetchall()}")
          "
```

### Task 8.2: README Documentation
Create comprehensive `README.md`:

```markdown
# Cricket Database

Comprehensive cricket database containing international matches, IPL, and Indian domestic cricket.

## Quick Start

### Download Latest Database

Visit [Releases](../../releases) and download `cricket.duckdb.gz`

```bash
# Decompress
gunzip cricket.duckdb.gz

# Use with DuckDB CLI
duckdb cricket.duckdb
```

### Query Examples

```sql
-- Top run scorers in IPL
SELECT batter, SUM(runs_batter) as total_runs
FROM deliveries d
JOIN matches m ON d.match_id = m.match_id
WHERE m.competition = 'Indian Premier League'
GROUP BY batter
ORDER BY total_runs DESC
LIMIT 10;

-- Ranji Trophy batting averages
SELECT
    batter,
    COUNT(DISTINCT match_id) as matches,
    SUM(runs_batter) as runs,
    SUM(CASE WHEN is_wicket THEN 1 ELSE 0 END) as dismissals,
    ROUND(SUM(runs_batter) * 1.0 / NULLIF(SUM(CASE WHEN is_wicket THEN 1 ELSE 0 END), 0), 2) as average
FROM deliveries d
JOIN matches m ON d.match_id = m.match_id
WHERE m.competition = 'Ranji Trophy'
GROUP BY batter
HAVING SUM(CASE WHEN is_wicket THEN 1 ELSE 0 END) > 0
ORDER BY average DESC
LIMIT 20;
```

## Data Sources

- **International Cricket**: [Cricsheet.org](https://cricsheet.org)
- **IPL**: [Cricsheet.org](https://cricsheet.org)
- **Ranji Trophy**: ESPNcricinfo
- **Syed Mushtaq Ali**: ESPNcricinfo
- **Vijay Hazare**: ESPNcricinfo

## Database Schema

[Include schema documentation]

## Build Locally

```bash
# Clone repository
git clone <repo-url>
cd cricket-database

# Install dependencies
pip install -r requirements.txt

# Build database
python scripts/build_database.py
```

## Automated Updates

Database is automatically rebuilt weekly via GitHub Actions every Sunday at 2 AM UTC.

## License

Data: Subject to source licenses (Cricsheet, ESPNcricinfo)
Code: MIT License
```

---

## Phase 9: Final Validation & Cleanup

### Task 9.1: Data Quality Checks
Create `src/pipeline/validation.py`:

**Checks to implement:**
- No duplicate match IDs
- All foreign keys valid
- Date ranges reasonable
- No NULL values in required fields
- Delivery counts match over counts
- Team names consistent

### Task 9.2: Performance Optimization
- Add appropriate indexes
- Optimize Parquet compression (snappy vs gzip)
- Consider partitioning large tables
- Test query performance on common patterns

### Task 9.3: Documentation
- Code docstrings for all functions
- Inline comments for complex logic
- Architecture diagram (optional)
- Data dictionary

---

## Execution Instructions for Claude Code (YOLO Mode)

### Priority Order:
1. **Phase 1**: Setup (critical foundation)
2. **Phase 2**: Cricsheet pipeline (easier, validates approach)
3. **Phase 5**: DuckDB setup (needed to test Phase 2)
4. **Phase 6**: Orchestrator (ties Phase 2 & 5 together)
5. **Phase 3**: ESPNcricinfo scraper (more complex)
6. **Phase 4**: Data normalization (combines both sources)
7. **Phase 7**: Testing
8. **Phase 8**: GitHub Actions
9. **Phase 9**: Validation & polish

### Key Decisions Pre-Made:
- ✅ Use Python 3.11+
- ✅ Use DuckDB (not PostgreSQL)
- ✅ Store intermediate data as Parquet
- ✅ Use httpx for HTTP requests
- ✅ Use pandas for data transformation
- ✅ Weekly GitHub Actions rebuild
- ✅ Store database as GitHub Release artifact
- ✅ Scrape ESPNcricinfo (don't use paid APIs)

### Error Handling Strategy:
- Log all errors, don't fail entire pipeline
- Skip malformed match files, log IDs
- Continue processing even if some matches fail
- Generate error report at end

### Performance Targets:
- Process ~20K matches in < 30 minutes
- Final database size < 2GB
- Query response time < 1 second for common queries

---

## Expected Timeline (YOLO Mode)

- **Phase 1-2**: 2-3 hours (setup + cricsheet)
- **Phase 3**: 3-4 hours (ESPNcricinfo scraping is tricky)
- **Phase 4-6**: 2-3 hours (integration)
- **Phase 7**: 1-2 hours (testing)
- **Phase 8**: 1 hour (GitHub Actions)
- **Phase 9**: 1 hour (validation)

**Total**: ~12-15 hours of autonomous work

---

## Success Criteria

✅ DuckDB file created and < 2GB
✅ Contains international cricket from cricsheet
✅ Contains IPL from cricsheet
✅ Contains Ranji Trophy from ESPNcricinfo
✅ Contains Syed Mushtaq Ali from ESPNcricinfo
✅ Contains Vijay Hazare from ESPNcricinfo
✅ All tests passing
✅ GitHub Actions workflow runs successfully
✅ Database queryable with sample queries
✅ README with usage examples complete
✅ Database uploaded as GitHub Release

---

## Notes for Execution

**The assistant should:**
1. Not ask for permission at each step
2. Make reasonable decisions when encountering edge cases
3. Log issues but continue processing
4. Create a working database even if some data is incomplete
5. Fix bugs encountered during execution without asking

**When encountering issues:**
- Try alternative approaches automatically
- Log the problem and workaround used
- Continue with rest of pipeline
- Report issues in summary at end
