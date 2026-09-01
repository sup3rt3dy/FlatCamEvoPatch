# FlatCAM Evo — working notes

PyQt6 desktop CAM application for preparing CNC jobs from PCB files. This repo is a fork
carrying stability and compatibility patches on top of FlatCAM Evo; upstream authorship is
Marius Stanciu's, based on Juan Pablo Caram's original FlatCAM.

Main branch for PRs: **`patch-8995`**.

## Running the app

**Use the `flatcam` conda environment, not the base one.** The base install has a different
Python and will not match what ships.

```
C:\Users\install\miniconda3\envs\flatcam\python.exe    # Python 3.10.18
```

**The `PATH` matters.** `freetype-py` binds against the FreeType DLL it finds first; without the
environment's `Library\bin` at the front you get this, on ~113 modules at once:

```
AttributeError: function 'FTC_CMapCache_Lookup' not found
```

That is a DLL resolution failure, *not* a code error. `start_flatcam.bat` sets the PATH for
exactly this reason — mirror it when invoking Python directly:

```bat
set "PATH=%CONDA%\envs\flatcam\Library\bin;%CONDA%\envs\flatcam\DLLs;%CONDA%\envs\flatcam\Scripts;%CONDA%\envs\flatcam;%SystemRoot%\system32;%SystemRoot%"
```

`start_flatcam.bat` hardcodes `pushd "C:\temp\flatcam_beta_broken"`, so **it always launches the
main checkout** — it will not test a git worktree. Point it at the working directory explicitly.

For headless checks, `QT_QPA_PLATFORM=offscreen` works. OpenGL context creation fails under it,
which is harmless for import/construction tests but means canvas rendering is not exercised.

### Runtime environment (verified)

| | |
|---|---|
| Python | 3.10.18 |
| PyQt6 | 6.9.1 |
| Shapely | 2.1.1 (GEOS 3.13.1) |
| VisPy | 0.15.2 |
| numpy | 2.2.6 |

Optional dependencies **not** installed locally: `rasterio`, `svgtrace` (both needed by the Image
Import plugin), `gdal`. `appPlugins/__init__.py` swallows their `ImportError`, so a plugin that
fails to import disappears silently rather than erroring — check the log if one is missing.

## Conventions

- **Line endings are CRLF** in the working tree, with `core.autocrlf=true` (git stores LF).
  Match CRLF when writing files. Do not use the git blob as the reference for what the working
  tree should look like — it is normalized and will mislead you.
- No test suite. Verify by importing every module and constructing the app headless; see below.
- Translations run through `gettext` with `_()` installed into `builtins`.

## Architecture notes

- `appMain.py` — the `App` class; owns options, the object collection, plugins and editors.
- `camlib.py` — `Geometry` / `CNCjob` base classes. Note `Geometry.__init__` attaches a canvas
  shape collection, so parser and plugin instances are coupled to the canvas.
- `appParsers/` — Gerber, Excellon, SVG, DXF, HPGL2 parsing.
- `appPlugins/` — ~35 plugins, all subclasses of `AppTool`, each building its full widget tree
  in `__init__`. They register app-level signal handlers there too
  (`proj_selection_changed`, `cleanup`), so **deferring their construction changes behaviour**.
- `appGUI/VisPyVisuals.py` — `ShapeCollectionVisual`, the canvas shape store. Objects are plotted
  on a **worker thread**, so `add()` and the redraw path can run concurrently.
- Long operations go through `worker_task.emit({'fcn': ..., 'params': [...]})`.

### Widget lifetime

Qt destroys the C++ side of a widget while Python still holds the wrapper — on tab close, object
delete, or UI rebuild. Touching it then raises:

```
RuntimeError: wrapped C/C++ object of type X has been deleted
```

This has been the single largest source of crashes in this fork. Use
`appGUI.GUIElements.safe_widget_call` — a decorator that swallows **only** that RuntimeError and
re-raises everything else — or include `RuntimeError` in the except clause. Any `try` block that
touches `self.ui.<widget>` should handle it. Do not catch bare `Exception` for this; it hides
real bugs.

### Qt slots and decorators

`safe_widget_call` must **not** be applied to a method connected to a Qt signal. PyQt reads the
slot's declared argument count and silently drops any extra signal arguments — it is normal here
for a `pyqtSignal(object, int)` to be connected to a handler taking one argument. A
`(*args, **kwargs)` wrapper erases that count, so PyQt passes everything through and the call dies
with *"takes 2 positional arguments but 3 were given"*, at signal time rather than at import.

A blanket sweep that decorated 592 signal handlers this way broke opening a project, and was
reverted. Guard signal handlers with an explicit `try/except RuntimeError` instead, or build a
signature-preserving wrapper first.

### Geometry

Shapely 2 is required. Its `unary_union` is far faster than the old `buffer(+eps).buffer(-eps)`
union trick (which was the faster option under Shapely 1.x) and already returns valid geometry on
GEOS ≥ 3.8, so a follow-up `buffer(0)` repair is pure waste. One caveat: the epsilon double-buffer
also welded polygons a few nanometres apart, which `unary_union` does not — use
`shapely.set_precision()` / `union_all(grid_size=...)` if that welding is actually wanted.

## Verifying a change

There is no test suite, so use these:

```bash
# every module imports (run with the runtime env + PATH above)
python -c "import importlib,pkgutil; [importlib.import_module('%s.%s'%(p,m.name)) for p in ('appPlugins','appParsers','appObjects','appEditors','appGUI','appHandlers','appCommon','tclCommands') for m in pkgutil.iter_modules([p])]"
```

Then construct the app headless (`QT_QPA_PLATFORM=offscreen`) and assert: all 33 plugins present,
25 Plugins-menu actions, four editors constructed. For parser changes, compare geometry against
an unmodified checkout (`git archive HEAD | tar -x -C <tmp>`) — compare area, geometry count and
validity, not just timings.

**Benchmark on an idle machine.** Parallel Python processes skew timings by 2x or more; when in
doubt run baseline and candidate alternating, so load affects both equally.

## Repo layout

- `patches/` — already-applied one-off patch scripts kept as history. Nothing there is imported
  or executed; see `patches/README.md`.
- `CHANGELOG.md` — reverse-chronological, `D.MM.YYYY` date headings, CRLF. Add new entries at the
  top, directly under the second `====` divider.
