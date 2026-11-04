# SKIT-DS-2023-2027-029
Final Year Project - TIM (Task Interdependency Mapper) : Student Mental Health Support System


## SOR scoring

The dependency-graph endpoint computes a live Structural Overload Relief (SOR) score
for every task and returns the score and its components on each graph node:

`SOR(v) = S(v) + O(v) + D(v) - P(v)`

The current equally weighted factors are:

- `S(v)`: task importance plus structural impact (the number of direct dependents).
- `O(v)`: task priority, used as the overload-association value.
- `D(v)`: deadline pressure, 0 with no deadline, 5 when due/overdue, and otherwise
  `5 / (1 + days remaining)`, capped at 5.
- `P(v)`: mood-based feasibility relief subtracted from the score. The task mood
  labels map to `good=5`, `okay=3`, `tired=2`, and `stressed=1`. Missing optional
  inputs contribute 0; unsupported mood labels are reported as an API validation
  error rather than silently interpreted.

The dashboard displays the score and factor breakdown and orders its task list from
highest to lowest SOR score. Scores are computed from current task and graph data
when the graph is requested; they are not persisted to `tasks.sor_score`.
