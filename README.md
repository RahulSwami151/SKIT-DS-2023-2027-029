# SKIT-DS-2023-2027-029
Final Year Project - TIM (Task Interdependency Mapper) : Student Mental Health Support System


## SOR scoring

The dependency-graph endpoint computes a live Structural Overload Relief (SOR) score
for every task and returns the score and its components on each graph node:

`SOR(v) = S(v) + O(v) + D(v) - P(v)`

The score uses three task inputs and one dependency-derived factor:

- `S(v)`: structural impact. The required importance labels `High`, `Med`, and
  `Low` map to 3, 2, and 1.
- `O(v)`: overload association, calculated as the number of unique, incomplete
  prerequisite tasks in the task's dependency chain. The dependency graph is
  traversed prerequisite-first; a completed task and its prerequisite chain no
  longer contribute to downstream overload.
- `D(v)`: deadline pressure, 5 when due/overdue, and otherwise
  `5 / (1 + days remaining)`, capped at 5.
- `P(v)`: mood-based feasibility relief subtracted from the score. Mood labels map
  to `high energy=5`, `good=4`, `neutral=3`, `fatigued=2`, and `overwhelmed=1`.
  Structural impact, overload, deadline, and mood are all required; missing or
  unsupported values and cyclic dependency graphs are reported as API validation
  errors.

The dashboard displays the score and factor breakdown and orders its task list from
highest to lowest SOR score. Scores are computed from current task status and graph
data when the graph is requested; they are not persisted to `tasks.sor_score`.
Task records must include importance, deadline, and mood. Existing SQLite databases
using numeric importance values need to be recreated or migrated to the categorical
`High`/`Med`/`Low` values before use.

## Recommendation interface milestone

The React frontend provides an initial recommendation screen for student `1`. It
loads `/students/1/dependency-graph`, shows the highest-scoring task whose
prerequisites are complete, and lists the other ready tasks in descending SOR score.
Incomplete tasks with unfinished prerequisites are counted as waiting, not presented
as actionable recommendations. If the frontend and API are on different origins,
set `VITE_API_BASE_URL` to the backend origin before starting/building the frontend.
