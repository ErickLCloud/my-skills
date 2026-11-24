---
name: project-init
description: >-
  Scaffolds the standard project-workspace layout into a connected folder, or refreshes the
  managed instruction block in an existing workspace's claude.md. Use ONLY when the user
  explicitly asks, never as a step inside another task, and never write anything before showing
  the plan and getting explicit confirmation.
---

# project-init

Fills a workspace folder that already exists and is already connected to this session. One
workspace folder per project; there is no level above it.

## Load-bearing invariants

1. **Never write before an explicit confirm.** Step 3 is a hard gate. The trigger for this skill
   is textual and can misfire — if nothing is written before the confirm, a misfire costs one
   message. Do not skip it even when the request looks unambiguous.
2. **Never overwrite in scaffold mode.** If a target file exists, skip it and report the skip.
3. **Refresh replaces the managed block and nothing else.** Everything outside the markers in
   `claude.md` belongs to the user, including the `Goal:` line.
4. **Get the write route right.** In a cloud Cowork session plain `Write` writes to the ephemeral
   cloud container, not the user's disk — it appears to succeed and produces nothing.
5. **This skill only creates and replaces. It never deletes and never migrates.**

## Write route — determine this FIRST

| Situation | Route |
|---|---|
| Cloud Cowork session (`mcp__remote-devices__*` tools present) | `mcp__remote-devices__device_bash` — runs on the user's machine with connected folders mounted read-write. |
| Cowork running "on your computer", or Claude Code CLI | Plain `Write`. |

On the `device_bash` route the mount forbids unlink: `rm` / `rmdir` fail with "Operation not
permitted". Scaffold mode never needs them. **Refresh mode must truncate-write** (`cat > file`),
never delete-then-recreate.

## Modes — decide from what is on disk, do not ask first

| Found in the target folder | Mode |
|---|---|
| No `claude.md` | **Scaffold** |
| `claude.md` containing both markers | **Refresh** |
| `claude.md` with no markers, or with a marker appearing more than once | **Stop.** Report what was found. Do not guess where a managed block belongs. |
| `projects/` | **Stop.** This is an older nested (umbrella) workspace; migration is out of scope. |
| `.context/` (dot) and no `_context/` | **Stop.** This is a v4-layout workspace. Tell the user to rename `.context/` to `_context/` themselves (this skill never migrates), then rerun refresh. |
| Some layout files present, some missing | **Scaffold**, listing precisely what will be created and what will be skipped. |

## Procedure

### Step 1 — Explore

1. Determine the write route. On the cloud route, resolve the connected folder's absolute device
   path with `mcp__remote-devices__get_device_info` / `device_list_dir`.
2. List the target folder, including dot-entries (a v4 `.context/` will not appear in a
   default listing). Note everything present.
3. Pick the mode from the table above. If it says stop, report and stop.

### Step 2 — Ask

Scaffold mode needs exactly one thing: the **goal**, one or two lines, for the `Goal:` line of
`claude.md`. Required — do not invent it. If the user has not said what the project is for, ask.

Refresh mode needs nothing. Go straight to Step 3.

### Step 3 — Confirm (hard gate)

- **Scaffold:** show the exact tree to be created and the filled-in `claude.md` in full. List any
  file that already exists and will be skipped.
- **Refresh:** show a diff between the workspace's current managed block and the one in
  [assets/claude.md.tpl](assets/claude.md.tpl). If they are already identical, say so and stop —
  there is nothing to do. State plainly that any hand-edits inside the markers will be lost.

Wait for an explicit yes. A vague or partial reply is not a yes.

### Step 4 — Write

**Scaffold.** Create the tree below via the route from Step 1. Build `claude.md` from
[assets/claude.md.tpl](assets/claude.md.tpl), substituting `{{GOAL}}`. Copy the five `_context`
seeds verbatim. Give `input/` and `output/` a `.gitkeep` each. Skip — never overwrite — any file
that already exists. **Verify no `{{` remains** in the written `claude.md`.

**Refresh.** Read [assets/claude.md.tpl](assets/claude.md.tpl) and extract everything between its
two markers, markers included. In the workspace's `claude.md`, replace everything between its own
two markers with that text, then truncate-write the whole file. Touch nothing else — not the
`Goal:` line, not the `_context` files, not `input/` or `output/`.

### Step 5 — Report

State what was created, replaced or skipped, and why. In scaffold mode, remind the user that
starting another workspace later means creating the empty folder and connecting it themselves
first — this skill cannot create a sibling of the folder it is attached to.

## What gets created

```
<workspace-folder>/
├── claude.md                        from assets/claude.md.tpl, {{GOAL}} substituted
├── _context/
│   ├── progress.md                  current status — overwrite in place
│   ├── todo.md                      idea inbox
│   ├── reference.md                 durable-facts sink
│   └── on-demand/
│       ├── journal.md               append-only history
│       └── notes.md                 drained scratchpad
├── input/                           read-only drop zone (.gitkeep)
└── output/                          deliverables, flat, _vN versioned (.gitkeep)
```

| Seed | Lands at |
|---|---|
| [assets/claude.md.tpl](assets/claude.md.tpl) | `claude.md` — the only file with variable content |
| [assets/progress.md](assets/progress.md) | `_context/progress.md` |
| [assets/todo.md](assets/todo.md) | `_context/todo.md` |
| [assets/reference.md](assets/reference.md) | `_context/reference.md` |
| [assets/journal.md](assets/journal.md) | `_context/on-demand/journal.md` |
| [assets/notes.md](assets/notes.md) | `_context/on-demand/notes.md` |

Each `_context` seed carries its own header stating its purpose, update trigger and budget.
`claude.md` deliberately does not repeat them.

## Out of scope — do not do these

- **Create the workspace folder itself.** The user creates and connects it; this skill fills it.
- **Migrate an older nested workspace.** Detect, report, stop.
- **Sync anything between machines.** Per-machine divergence is the chosen design.
- **Touch Claude account preferences.**
- **Delete anything.**
- **Write to the cloud container and call it done.**
