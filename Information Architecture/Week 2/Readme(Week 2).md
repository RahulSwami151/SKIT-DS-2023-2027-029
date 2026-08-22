Step 1 — Sitemap (FINAL, built in Whimsical)
  Reflects a left sidebar navigation (this is a website, not a mobile
  app): Dashboard, Dependency Graph, Journal as primary sidebar items;
  Account as a secondary, icon-access item. Onboarding/Login sits outside
  the sidebar as a separate pre-auth flow.
  

Step 2 — Navigation model & rationale
  Left sidebar nav, not a bottom tab bar. Dashboard, Dependency Graph,
  and Journal always visible; Account tucked into a smaller secondary
  section. Rationale tied to NFR-001 (simple, low-effort interface for
  students under academic stress).
  File: IA_Week2_Documentation.docx

Step 3 — Final user flow diagram (FINAL, built in Whimsical)
  One continuous flow, not multiple separate flows:
  Login -> enter multiple tasks (deadline, priority, importance, and
  per-task mood) -> optional Journal branch (journal answers analyzed
  for mental state, feeds SOR) -> user clicks "Generate Graph" on the
  Dashboard -> system runs dependency detection + SOR calculation ->
  prioritized graph renders on the Dashboard itself.


Step 4 — Cross-check against FR-002 / FR-004
  Verified graph nodes/edges and SOR display against backend output.
  One gap found and fixed: Task Detail needed the SOR score shown
  explicitly, not just implied by the graph.
  File: IA_Week2_Documentation.docx

Step 5 — Documentation packet
  This README plus all files listed above, compiled together.

Week 2 progress: 100%
