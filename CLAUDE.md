# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Python + GTK3 (PyGObject) desktop app for browsing and editing a MySQL-backed archive of the
Argentine magazine *El Porteño* (1982–1993). Single-user, single-window research tool — no test
suite, no build system, no package manifest (dependencies are installed ad hoc into `venv`/`venv2`).

## Running the app

```bash
python main.py
```

On startup it prompts in the terminal: `¿Desea conectarse remoto (-r) o local (-l)?` — type `-r`
for the remote MySQL connection or anything else for local. Connection credentials come from a
`.env` file (see `config.py` for the expected keys: `DB_HOST_r/l`, `DB_NAME_r/l`, `DB_USER_r/l`,
`DB_PASSWORD_r/l`, `DB_PORT_r`, `DB_SSL_CA_r`). `.env` is gitignored and must already exist locally.

There is no test runner, linter, or formatter configured in this repo.

## Architecture

The app follows a layered structure: **ui → services → database**, with `models.py` and
`application_state.py` as shared state passed through all layers.

- **`models.py`** — plain data classes for domain entities (`Revista`, `Nota`, `Carta`, `Autor`,
  `Tema`, `Categoria`, `StaffMiembro`, `ArchivoResumen`, `Hexagrama`, `ResultadoQuery`). Each has
  `desde_dict` (from a DB dict row) and `desde_sql` (from a raw tuple) constructors, plus
  `to_dict()` on some. No ORM — these are hand-rolled mappers.
- **`database/connection.py`** — `DataBaseConnection` is a classmethod-only singleton wrapping
  `mysql.connector`. `execute_query()` is the single chokepoint for all SQL: it auto-detects
  SELECT vs INSERT/UPDATE/DELETE, commits writes, and — for any write — also inserts an audit row
  into `registro_modificaciones` (capturing the query text and the calling function/file via
  `inspect.stack()`). Any new write path must go through this method to keep that audit trail
  intact.
- **`database/querys.py`** — every SQL string used by the app, as module-level `QUERY_*` constants
  (parameterized with `%s`, no SQL built dynamically elsewhere). Add new queries here, not inline
  in services.
- **`services.py`** — one class per domain area (`RevistaServices`, `StaffServices`,
  `NotaServices`, `CartaServices`, `AutorServices`, `TemaServices`, `AnalisisService`,
  `ServicesArchivoResumen`, plus a small `DBService` base). Services call `database/querys.py`
  constants through `DataBaseConnection.execute_query()` and convert results into `models.py`
  objects (often via the `to_*` helpers in `utils.py`). This is the only layer that should talk to
  the database.
- **`application_state.py`** — `EstadoDeAplicacion` holds cross-window UI state (currently selected
  `Revista`/`Carta`/`Nota`/`Autor`, "is edit mode active" flags, signal-suppression flags). One
  instance is created in `main.py` and threaded through `MainWindow` and dialogs/sub-windows;
  prefer adding new shared UI state here rather than ad hoc globals. Window/dialog-local state
  (e.g. a flag only `notas_window` cares about) should stay local to that window instead of being
  added here — see `git log` around the `notas_window` refactor for the precedent.
- **`ui/`** — GTK widgets and windows:
  - `main_window.py` — the main application window (tabs for Revista/Correo/Autores etc.).
  - `notas_window.py` — the "Notas" editor sub-window.
  - `widgets/` — reusable custom GTK widgets (`lista_multi.py` is a multi-select list used for
    picking/adding Autores and Temas; `text_editor.py`, `etiquetas.py`, `entry_comentarios.py`,
    `labels_centrales.py`, `msg_boxes.py`, `visualizadores.py`).
  - `dialogs/` — modal dialogs (`dialog_add_elementos.py`, `dialog_correo.py`).
  - `gi_setup.py` — must be imported before `gi.repository` anywhere (sets GI version
    requirements); `main.py` imports it first for this reason.
  - `styles/` — GTK CSS (`style_02.css`), loaded once in `main.py:setup_app()`.
  - `icons/` — image assets referenced from `config.py` (e.g. `RESUMEN_ICON_PATH`).
- **`utils.py`** — cross-cutting helpers: hexagrama binary/line conversion, name formatting,
  dict-list → model-list converters (`to_nota`, `to_tema`, `to_cartas`, `to_autor`), HTML↔GTK
  `TextBuffer` conversion (`buffer_to_html`/`html_to_buffer`, used for rich text fields), and fuzzy
  matching (`buscar_similares`, via `thefuzz`/`rapidfuzz`-style threshold) for catching duplicate
  Autor/Tema entries.
- **`config.py`** — single `Config` dataclass (instantiated once as `config`), loads `.env`,
  exposes the hexagram binary-code table (`HEXAGRAMA`), icon paths, and app metadata. Read DB
  credentials from here rather than `os.getenv` directly elsewhere.

## Conventions to follow

- Code, identifiers, comments, and log messages are in **Spanish** — match this in new code.
- All SQL lives in `database/querys.py` as `QUERY_*` constants; services reference them by name.
- All DB access goes through `DataBaseConnection.execute_query()`, never a raw cursor elsewhere —
  this is what keeps the `registro_modificaciones` audit log accurate.
- Model classes take plain constructor args plus `desde_dict`/`desde_sql` classmethods; follow that
  pattern for any new entity rather than introducing a different mapping style.
- Shared cross-window state goes in `EstadoDeAplicacion`; window-local state stays local (recent
  refactors have been actively moving state *out* of `EstadoDeAplicacion` when it's only used by
  one window — see `Pendientes_desarrollo.txt` and recent commits on this branch).

## Known pending work (`Pendientes_desarrollo.txt`, gitignored but present locally)

- Optimize Autor/Tema search.
- Optimize `Goto_nota()` to stop scanning the whole list after a match is found.
- Continue splitting `models.py` and `services.py` into per-domain files (already underway: `models/`
  and the per-class structure in `services.py` are steps toward this).
