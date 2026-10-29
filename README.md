# SKIT-DS-2023-2027-029
Final Year Project - TIM (Task Interdependency Mapper) : Student Mental Health Support System

## SOR scoring progress

The initial SOR scoring slice implements the structural-impact factor. For each task,
structural impact is the number of tasks that directly depend on it in the student's
dependency graph. The `GET /students/{student_id}/dependency-graph` endpoint returns
this count as `structural_impact` on every node, and the dashboard displays it in the
selected task's details.

This is not yet a composite SOR score. Overload association, deadline pressure, and
feasibility remain to be implemented; the existing `tasks.sor_score` field is not
populated by this slice.
