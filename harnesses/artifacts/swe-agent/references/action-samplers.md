# Action Samplers

Action samplers are optional per-step mechanisms that increase the quality of each individual action by generating and comparing multiple candidates before committing.

---

## `ask_colleagues`

**Purpose:** sample N parallel completions, synthesize them into a single action.

**Steps:**
1. Query the model N times (default `n_samples = 2`) with the same current message history. Each query is independent.
2. Parse each completion into `{thought, action}`. Skip completions that fail parsing.
3. If zero completions parse successfully, raise a format error.
4. Concatenate all parsed thoughts and proposed actions into a discussion block:
   ```
   Your colleagues had the following ideas:

   Thought (colleague 0): <thought0>
   Proposed Action (colleague 0): <action0>

   Thought (colleague 1): <thought1>
   Proposed Action (colleague 1): <action1>

   Please summarize and compare the ideas and propose and action to take.
   Finally choose one action to perform and explain it in detail and include it as a tool call.
   <important>You must include a thought and action (as a tool/function call). Do not try to invoke commands with triple backticks, use function calls instead.</important>
   ```
5. Append the discussion block as a new `user` message to the history.
6. Query the model once more to produce the final synthesized action.
7. Return the final completion as the step's action.

---

## `binary_comparison`

**Purpose:** sample multiple candidate actions and select the best via pairwise LLM comparison.

**Configuration defaults:** `min_n_samples = 4`, `max_n_samples = 10`.

**Steps:**

**Candidate generation:**
1. Query the model `min_n_samples` times in parallel.
2. Filter out completions that fail parsing. If none survive, raise a format error.
3. Deduplicate by action string. Keep only unique actions.
4. If any candidate action is an edit command (starts with `edit`, `str_replace_editor insert`, or `str_replace_editor str_replace`), sample `max_n_samples - min_n_samples` additional completions, parse, and deduplicate again.
5. If only one unique action remains, warn and use it directly.

**Tournament selection:**
- Compare candidates pairwise: current best vs. each challenger.
- For each comparison, build a three-message prompt:
  - **System**: `You are an expert software engineer overseeing junior developers. They suggest actions to take to solve a problem. You must choose the best action to take.`
  - **User (instance)**: rendered from `instance_template` with `{problem_statement, traj}`. The trajectory is formatted as `Action N: <action>\nObservation N: <observation>` for each prior step.
  - **User (comparison)**: rendered from `comparison_template` with `{thought1, action1, thought2, action2}`:
    ```
    Two junior developers suggested the following actions:

    <thought1>{{thought1}}</thought1>
    <action1>{{action1}}</action1>

    <thought2>{{thought2}}</thought2>
    <action2>{{action2}}</action2>

    Please compare the two actions in detail.
    Which action should we take?
    If you think the first action is better, respond with "first".
    If you think the second action is better, respond with "second".
    The last line of your response MUST be "first" or "second".
    ```
  - When comparing 3 or more candidates, apply `cache_control: {type: ephemeral}` to the instance message.
- Parse the last line of the response: `"first"` → keep current best; `"second"` → promote challenger.
- Return the surviving candidate as the step's action.
- Save the full comparison log (which pairs were compared, messages, responses, selections) in `extra_info.comparison_log` of the step output.
