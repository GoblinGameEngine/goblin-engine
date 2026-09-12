# Goblins

A first-person neighborhood RPG built in Godot 4.3, developed via headless
CLI scripting (Blender for assets, Godot for the engine).

## Version

**Current: `0.6.0-prealpha.12`** — pre-alpha. Tracked in the `VERSION` file
at the repo root (single source of truth) and mirrored into
`godot_project/project.godot`'s `config/version`.

Scheme: `MAJOR.MINOR.PATCH-phase.N`, phase one of `prealpha` / `alpha` /
`beta` / `rc`, dropped entirely at `1.0.0` (first real release):
- `MAJOR.MINOR.PATCH` bumps like normal SemVer — patch for fixes, minor
  for new features, major reserved for 1.0.0 and later breaking changes.
- `N` is a counter within the current phase, bumped on each tagged push
  during that phase (`prealpha.1`, `prealpha.2`, ...).
- Advancing phases (e.g. pre-alpha → alpha) resets `N` to `1` and is a
  deliberate call, not automatic — currently pre-alpha until told
  otherwise.

Each versioned push is tagged in git as `v<version>` (e.g. `v0.1.0-prealpha.1`).

## GitHub

Repo: **https://github.com/GoblinGameEngine/goblins** (private)

Pushed with `gh` CLI (installed locally at `~/.local/bin/gh`, no sudo
needed), authenticated as the `GoblinGameEngine` account.

`.gitignore` excludes, deliberately:
- `/reference/` — personal photos and character-reference images used as
  source material while building assets, not meant to be published.
  Kept local-only.
- `godot_project/.godot/` — Godot's editor cache/import artifacts,
  fully regenerated automatically on next open.
- `godot_project/build/` — exported game binaries, regenerate via
  Godot's export, not source.
- `*.blend1` / `*.blend2` — Blender autosave backups.
- `/godot/` — a spare local copy of the Godot engine binary, not project
  code (redundant with `~/newtons-garden/tools/`).

Everything else (scripts, scenes, textures, `.blend` project files,
tools) is committed.

### Git identity

This repo's commits use `GoblinGameEngine <GoblinGameEngine@users.noreply.github.com>`
as the author, set locally for this repo only — it does not affect your
global git config or any other project.

### Pushing future changes

```bash
cd ~/goblins
git add -A
git commit -m "..."
git push
```

### If you ever want the reference images backed up too

They're excluded from git on purpose (see above). Including them later
is a separate, deliberate decision — nothing currently depends on that
folder being in the repo.
