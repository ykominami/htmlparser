# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run the main entry point (requires a YAML config file as argument)
uv run htmlparser <config.yaml>

# Other CLI entry points
uv run htmlparser_clear <config.yaml>    # Clear the DB
uv run htmlparser_count <config.yaml>    # Count DB entries
uv run htmlparser_print_list_text <config.yaml>  # Print titles
uv run htmlparser_prepare <config.yaml>  # Prepare directory structure

# Lint and type checking
uv run ruff check ./src
uv run mypy ./src

# Format
uv run black ./src

# Run tests
uv run pytest
```

## Architecture

This is a Python HTML scraper package that parses saved HTML pages from various e-commerce/educational sites and stores extracted data in a YAML database.

**Dependency:** Relies heavily on the local sibling package `yklibpy` (at `../yklibpy`), which provides base classes and utilities. Key imports:
- `yklibpy.htmlparser.scraper.Scraper` — base class for all scrapers
- `yklibpy.htmlparser.app.App` — base class for `Subapp`
- `yklibpy.common.env.Env` — handles config/environment
- `yklibpy.db.DbYaml` — YAML-based persistence layer

**Data flow:**
1. A YAML config file is passed as a CLI argument
2. `top.py` loads the config via `TopConfigDb` and initializes a `DbYaml` database
3. `Subapp` (extends `App`) dispatches to the appropriate scraper based on the `mode` string from config
4. Each scraper parses HTML using BeautifulSoup and populates `links_assoc` (a `dict[str, dict]`)
5. Results are merged back into the DB and saved

**Scraper pattern:** Each scraper in `src/htmlparser/` follows the same structure:
- Inherits from `yklibpy.htmlparser.scraper.Scraper`
- Contains an inner `WorkInfo` class that holds extracted fields and a `to_assoc()` method
- Implements `scrape(info: Info) -> None` to parse `info.soup` (BeautifulSoup object)
- Calls `Scraper._add_assoc(self.links_assoc, key, sequence, assoc_dict)` to store results

**Supported scraper modes** (registered in `subapp.py`):
- `"udemy"` → `UdemyScraper`
- `"ku"` → `KUScraper` (Amazon Kindle Unlimited)
- `"fanza_doujin_basket"` → `FanzaDoujinBasketScraper`
- `"fanza_doujin_purchased"` → `FanzaDoujinPurchasedScraper`
- `"amazon_saved_cart"` → `AmazonSavedCartScraper`

**Adding a new scraper:** Create a new file in `src/htmlparser/`, subclass `Scraper`, implement `scrape()` and `add_assoc()`, then register the mode string in `Subapp.create_scraper()` in `subapp.py`. The `add_assoc()` method calls `Scraper._add_assoc(self.links_assoc, key, sequence, work_info.to_assoc())` where `key` is a unique identifier (e.g., `course_id`, `content_id`).

**YAML config keys** (read by `TopConfigDb`):
- `db_file` — filename of the YAML DB relative to the config file's directory
- `db_kind` — DB type string (e.g., `"yaml"`)
- `patterns` — list of glob/pattern strings used by `Env.set_pattern()` to locate HTML files
- `config_file` — optional secondary config file path passed to `Env`

**`db_loadx()` note:** `top.py` hard-codes YAML tags for `AmazonSavedCartScraper.WorkInfo` and `FanzaDoujinBasketScraper.WorkInfo` to handle custom object deserialization. If a new scraper serializes `WorkInfo` objects directly into the DB, add its YAML tag to the `tags` list in `Top.db_loadx()`.

## Tool Configuration

- **Linter:** ruff with rules `E`, `F`, `I`, `N`; `E501` (line length) is ignored
- **Type checker:** mypy in strict mode; `mypy_path = "src"`
- **Formatter:** black, line length 88
- **Python:** requires >=3.14
