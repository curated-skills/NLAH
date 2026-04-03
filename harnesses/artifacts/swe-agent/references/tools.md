# Tool Contracts

All tools are available to the agent in each step of the observe-reason-act loop. Tools are provided either as native bash commands or as custom binaries installed in the sandbox.

---

## Bash tool

The agent can run any bash command. This is the primary action surface for exploration, testing, and running scripts.

**Blocked commands** — the following are forbidden and return an error instead of executing:

Prefix blocklist (any command starting with these strings):
- `vim`, `vi`, `emacs`, `nano`, `nohup`, `gdb`, `less`, `tail -f`, `python -m venv`, `make`

Standalone blocklist (command is exactly one of these):
- `python`, `python3`, `ipython`, `bash`, `sh`, `/bin/bash`, `/bin/sh`, `nohup`, `vi`, `vim`, `emacs`, `nano`, `su`

Conditional blocklist (block unless also matching the given regex):
- `radare2` / `r2`: allowed only when invoked with `-c` flag

When a blocked command is detected, return: `Operation '<action>' is not supported by this environment.`

---

## Windowed file viewer tools

These tools maintain a persistent "window" into a file. The window position is stored in `/root/state.json` under `open_file` and `working_dir`. State is refreshed after each step via the bundle's state command.

**`open "<path>" [<line_number>]`**
Opens the file at `path` in the editor window. If `line_number` is provided, the window is positioned to include that line. Prints the windowed view (default 100 lines) with line numbers.

**`goto <line_number>`**
Moves the window to show `line_number`.

**`scroll_up`**
Moves the window up by one window height.

**`scroll_down`**
Moves the window down by one window height.

**`create <filename>`**
Creates a new empty file and opens it in the window.

Window output format (each line is `N: content`):
```
[File: /repo/foo.py (200 lines total)]
(100 more lines above)
101: def bar():
102:     pass
(98 more lines below)
```

---

## Edit tools — `str_replace_editor`

A stateful editor for viewing, creating, and modifying files.

```
str_replace_editor <command> <path> [options]
```

**Commands:**

- **`view`** — display file with line numbers (`cat -n`), or list a directory up to 2 levels deep. Optional `--view_range [start, end]`.
- **`create`** — create a new file at `path` with content `--file_text <text>`. Fails if the file already exists.
- **`str_replace`** — replace the first occurrence of `--old_str <text>` with `--new_str <text>`. `old_str` must match exactly (including whitespace) and must be unique in the file.
- **`insert`** — insert `--new_str <text>` after line `--insert_line <n>`.
- **`undo_edit`** — revert the last edit made to `path`.

Notes:
- State is persistent across calls.
- Long output is truncated and marked `<response clipped>`.
- `str_replace` uniqueness: if `old_str` matches multiple locations, the replacement is rejected; include more surrounding context.

---

## Search tools

**`find_file <file_name> [<dir>]`**
Finds all files with the given name or shell-style wildcard pattern (e.g., `*.py`) under `dir`. Defaults to current directory.

**`search_dir <search_term> [<dir>]`**
Searches for `search_term` in all files under `dir`. Defaults to current directory.

**`search_file <search_term> [<file>]`**
Searches for `search_term` in `file`. Defaults to the currently open file.

---

## Submit tool

**`submit`** (soft, when `review_on_submit_m` bundle is active)
Triggers the review checklist described in the main skill Stage 3e. Does not finalize.

**`submit -f`** (hard)
Finalizes submission. Produces a git diff from the repository and writes it as the submission patch. Emits `<<SWE_AGENT_SUBMISSION>>` in the output.

If the soft submit bundle is not active, `submit` always finalizes immediately.

---

## Registry and state files

- `/root/.swe-agent-env`: JSON file written at setup with registry variables accessible to tool scripts (e.g., `USE_FILEMAP`, `SUBMIT_REVIEW_MESSAGES`).
- `/root/state.json`: JSON file updated by state commands after each step. Contains fields such as `open_file` and `working_dir`. Read by the Agent substrate to inject shell-state context into observation messages.

---

## Environment variables set at startup

| Variable | Value |
|---|---|
| `PAGER` | `cat` |
| `MANPAGER` | `cat` |
| `LESS` | `-R` |
| `PIP_PROGRESS_BAR` | `off` |
| `TQDM_DISABLE` | `1` |
| `GIT_PAGER` | `cat` |
