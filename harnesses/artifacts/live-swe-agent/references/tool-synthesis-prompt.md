# Tool Synthesis Prompt and Examples

This reference captures the tool-synthesis behavior that makes this agent self-evolving.
After every observation, the agent is prompted to reflect and optionally create a Python helper.

---

## Reflection Trigger

The following prompt fragment appears after every short observation (output under 10,000 characters):

```
Reflect on the previous trajectories and decide if there are any tools you can create
to help you with the current task.
Note that just because you can use basic commands doesn't mean you should not create
any tools that can still be helpful.
```

When this prompt appears, the agent must decide:
- Is the current task routine enough to handle with standard commands?
- Would a custom helper reduce command count, improve accuracy, or handle output structure better?

If yes, the next step should synthesize the tool before continuing with the main workflow.

---

## Tool Creation Pattern

A synthesized tool is a Python script written to a file in one step, then invoked in subsequent steps.

**Step A — Write the tool:**

```
THOUGHT: I need to precisely replace strings in multiple files without relying on sed's
regex escaping. I'll write a Python edit tool that takes a file path, old string, and
new string as arguments and reports exactly what changed.

cat <<'EOF' > /tmp/edit_file.py
#!/usr/bin/env python3
import sys

def main():
    if len(sys.argv) != 4:
        print("Usage: edit_file.py <filepath> <old_string> <new_string>")
        sys.exit(1)
    filepath, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(filepath, 'r') as f:
        content = f.read()
    if old not in content:
        print(f"ERROR: string not found in {filepath}")
        sys.exit(1)
    updated = content.replace(old, new, 1)
    with open(filepath, 'w') as f:
        f.write(updated)
    print(f"Replaced in {filepath}")
EOF
```

**Step B — Invoke the tool:**

```
THOUGHT: Now I'll use the edit tool to apply the fix at the identified location.

python /tmp/edit_file.py /repo/src/module.py "old_function_call()" "new_function_call()"
```

---

## Tool Naming and Location

- Write task-local tools to `/tmp/` or another path outside the target codebase.
- Name tools descriptively: `edit_file.py`, `search_ast.py`, `check_imports.py`.
- Reuse the same tool for multiple invocations across the task.
- Do not commit synthesized tools; they are ephemeral helpers.

---

## Minimum Required Tool

Always synthesize at least one edit tool that:
1. Accepts a file path, old string, and new string as arguments.
2. Replaces the first occurrence of the old string with the new string.
3. Prints the file path and the lines modified.
4. Exits with a non-zero code and an error message if the old string is not found.

This ensures reliable multi-location edits without shell escaping errors.

---

## When Not to Synthesize

Do not synthesize a tool when:
- A single standard command suffices (e.g., `grep -n pattern file`).
- The tool would be used only once for a trivial operation.
- The remaining workflow has only one or two steps left.

Synthesize selectively—each new tool has an upfront cost in one step. The benefit must outweigh that cost.
