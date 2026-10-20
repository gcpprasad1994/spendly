# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Spendly: a Flask + SQLite personal expense tracker. It is a step-by-step teaching skeleton: `app.py` and `database/db.py` mark unfinished parts with "students will implement" / "coming in Step N" placeholders. Only the landing, register, login and terms pages render; the forms are not wired to any logic yet.

## Commands

Use the local venv (Python 3.14); each shell command is fresh, so call the binaries directly instead of activating.

- Install deps: `venv/bin/pip install -r requirements.txt`
- Run the app: `venv/bin/python app.py` (debug mode, port **5001**, not Flask's default 5000)
- Run tests: `venv/bin/pytest` (pytest + pytest-flask are installed, but no tests exist yet)
- Single test: `venv/bin/pytest tests/test_x.py::test_name`

There is no linter or build step configured.

## Architecture

- `app.py` is the single entry point and holds every route. Routes for logout, profile and add/edit/delete expense are string-returning placeholders tagged with their course step number. Replace them in place rather than adding new route files.
- `database/db.py` is a comment-only stub specifying the intended API: `get_db()` (SQLite connection with `row_factory` and foreign keys enabled), `init_db()` (`CREATE TABLE IF NOT EXISTS`), `seed_db()` (dev data). `app.py` does not import it yet. The SQLite file `expense_tracker.db` is gitignored.
- Templates all extend `templates/base.html` (navbar, footer, Google Fonts, `css/style.css`, `js/main.js`). Pages add their own assets through the `head` and `scripts` blocks. `landing.html` uses `head` to load `css/landing.css` and `scripts` for its inline JS, including the demo video modal. Link between pages with `url_for(...)`.
- Styling is split: `static/css/style.css` is global, `static/css/landing.css` is landing-page only (`lp-` class prefix). `static/js/main.js` is an empty placeholder.
- Currency in the copy is rupees (₹).
