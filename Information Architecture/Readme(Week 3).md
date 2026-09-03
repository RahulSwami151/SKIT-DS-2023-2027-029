Week 3 (6/9/26 – 12/9/26) — Final consistency pass & lock
Step	Deliverable	File
1 — Consistency audit	Compared Screen Inventory, Sitemap, Card Sort, and the user flow against each other. Found a real contradiction: the Week 2 sitemap listed "Dependency Graph" as its own separate sidebar route, but the user flow has the graph rendering directly on the Dashboard. Confirmed with stakeholder: Dashboard IS the graph screen.	This README
2 — Corrected route structure	True routes: Onboarding/Login, Dashboard, Journal, Settings, Profile. Task List, Add/Edit Task, Task Detail, and the Dependency Graph are sections/modals inside the single Dashboard page — not separate routes.	Screen_Inventory.xlsx (new "Route Type" column), IA_Week3_Sitemap_Final.png / .svg
3 — Handoff to Database Design	Entity/field list for the next user story (starts 12/9/26), drawn from the content audit — see below	This README

Week 3 progress: 100% — Information Architecture user story CLOSED.

Handoff to Database Design

Starting point only — Rahul should confirm types/constraints against his existing schema:
User — name, email, password/student ID
Task — title, description, deadline, subject/category, priority, importance, mood (at creation), status
TaskDependency — task_id, depends_on_task_id, relation_type
SORScore — computed field on Task (not user-entered); inputs: deadline, priority, importance, mood, journal-derived mental state
JournalEntry — mood rating, stress level, energy level, free-text note (optional), timestamp
Key design decisions
The Dependency Graph lives ON the Dashboard — it is not a separate page. Task entry, the "Generate Graph" action, and the rendered graph all happen on one screen. There is no standalone Dependency Graph route anywhere in the app. (Corrected in Week 3 — the Week 2 sitemap had this wrong.)
Task List, Add/Edit Task, and Task Detail are also not separate routes. They're sections/modals within the same Dashboard page. The only real routes in the whole app are: Onboarding/Login, Dashboard, Journal, Settings, Profile.
The graph doubles as the recommendation surface. Node size/prominence encodes each task's SOR (priority) rank; edges encode relative urgency (horizontal = higher urgency/thicker, downward from the #1 node = 2nd priority/thinner) — so a stressed student reads what's urgent and what's blocking what in one glance. This is why FR-003 and FR-004 both map onto the Dashboard's graph section rather than a dedicated screen.
Mood feeds SOR from two places. Once per task (entered alongside deadline/priority/importance) and once via the optional Journal section, where answers are analyzed for the student's broader mental state.
This is a website, not a mobile app — navigation is a left sidebar (Dashboard, Journal as primary items; Account as a smaller secondary item), not a bottom tab bar.
