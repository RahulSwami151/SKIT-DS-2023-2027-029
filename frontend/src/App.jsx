import { useEffect, useMemo, useState } from "react";
import { CalendarDays, CheckCircle2, Clock3, RefreshCw, Sparkles } from "lucide-react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";
const STUDENT_ID = 1;

function formatDeadline(deadline) {
  const date = new Date(deadline);
  if (Number.isNaN(date.getTime())) return "Deadline unavailable";
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

function getRecommendations(graph) {
  const tasksById = new Map(graph.nodes.map((task) => [task.id, task]));
  const incompleteTasks = graph.nodes.filter((task) => task.status !== "completed");
  const readyTasks = incompleteTasks.filter((task) =>
    graph.edges
      .filter((edge) => edge.source === task.id)
      .every((edge) => tasksById.get(edge.target)?.status === "completed"),
  );
  const sortByPriority = (first, second) =>
    second.sor_score - first.sor_score ||
    new Date(first.deadline).getTime() - new Date(second.deadline).getTime();

  return {
    ready: readyTasks.sort(sortByPriority),
    blocked: incompleteTasks.length - readyTasks.length,
    completed: graph.nodes.length - incompleteTasks.length,
  };
}

function RecommendationCard({ task, featured = false }) {
  return (
    <article className={`recommendation-card${featured ? " featured" : ""}`}>
      <div className="recommendation-rank" aria-label={featured ? "Top recommendation" : undefined}>
        {featured ? <Sparkles size={18} aria-hidden="true" /> : <span>{task.rank}</span>}
      </div>
      <div className="recommendation-copy">
        <div className="recommendation-labels">
          <span className={`task-status status-${task.status.replaceAll("_", "-")}`}>
            {task.status.replaceAll("_", " ")}
          </span>
          {task.importance && <span className="task-importance">{task.importance} impact</span>}
        </div>
        <h3>{task.title}</h3>
        <p>{[task.subject, task.task_type].filter(Boolean).join(" · ") || "Task"}</p>
        <span className="recommendation-deadline">
          <CalendarDays size={14} aria-hidden="true" />
          Due {formatDeadline(task.deadline)}
        </span>
      </div>
      <div className="recommendation-score">
        <strong>{Number(task.sor_score).toFixed(1)}</strong>
        <span>SOR score</span>
      </div>
    </article>
  );
}

export default function App() {
  const [graph, setGraph] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadRecommendations() {
    setLoading(true);
    setError("");

    try {
      const baseUrl = API_BASE_URL.replace(/\/$/, "");
      const response = await fetch(`${baseUrl}/students/${STUDENT_ID}/dependency-graph`);
      if (!response.ok) {
        throw new Error(`Recommendations could not be loaded (HTTP ${response.status}).`);
      }

      const data = await response.json();
      if (
        !data ||
        !Array.isArray(data.nodes) ||
        !Array.isArray(data.edges) ||
        data.nodes.some(
          (task) =>
            !task ||
            !Number.isInteger(task.id) ||
            typeof task.title !== "string" ||
            typeof task.status !== "string" ||
            task.sor_score == null ||
            !Number.isFinite(Number(task.sor_score)),
        ) ||
        data.edges.some(
          (edge) =>
            !edge ||
            !Number.isInteger(edge.source) ||
            !Number.isInteger(edge.target),
        )
      ) {
        throw new Error("The recommendation service returned an invalid task graph.");
      }
      setGraph(data);
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Recommendations could not be loaded. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadRecommendations();
  }, []);

  const recommendations = useMemo(
    () => (graph ? getRecommendations(graph) : null),
    [graph],
  );
  const rankedTasks = recommendations?.ready.map((task, index) => ({
    ...task,
    rank: index + 1,
  }));
  const nextTask = rankedTasks?.[0];

  return (
    <main className="recommendation-page">
      <header className="recommendation-header">
        <div>
          <span className="eyebrow">Task &amp; Intent Management</span>
          <h1>Your next best step</h1>
          <p>Recommendations are ranked by your live SOR priority score.</p>
        </div>
        <button
          className="btn btn-secondary refresh-button"
          type="button"
          onClick={() => void loadRecommendations()}
          disabled={loading}
        >
          <RefreshCw size={16} aria-hidden="true" className={loading ? "spin" : ""} />
          Refresh
        </button>
      </header>

      {error && (
        <div className="recommendation-message error-message" role="alert">
          <p>{error}</p>
          <span>
            Check that the backend is running and that <code>VITE_API_BASE_URL</code> points to it
            when frontend and backend use different origins.
          </span>
          <button
            className="btn btn-secondary"
            type="button"
            onClick={() => void loadRecommendations()}
          >
            Try again
          </button>
        </div>
      )}

      {loading && !graph && (
        <div className="recommendation-message" role="status">
          <RefreshCw size={18} aria-hidden="true" className="spin" />
          Loading your recommendations…
        </div>
      )}

      {!loading && !error && recommendations && (
        <>
          <section className="recommendation-summary" aria-label="Task summary">
            <div className="summary-intro">
              <span className="summary-icon">
                <Sparkles size={20} aria-hidden="true" />
              </span>
              <div>
                <strong>{recommendations.ready.length} ready to work on</strong>
                <span>Prerequisites are accounted for in these recommendations.</span>
              </div>
            </div>
            <div className="summary-metrics">
              <span>
                <CheckCircle2 size={15} aria-hidden="true" /> {recommendations.completed} completed
              </span>
              <span>
                <Clock3 size={15} aria-hidden="true" /> {recommendations.blocked} waiting
              </span>
            </div>
          </section>

          {nextTask ? (
            <section className="next-task-section" aria-labelledby="next-task-heading">
              <div className="section-head">
                <div>
                  <span className="eyebrow">Recommended next task</span>
                  <h2 id="next-task-heading">Start here</h2>
                </div>
                <span className="next-task-indicator">
                  <Sparkles size={15} aria-hidden="true" /> Best match
                </span>
              </div>
              <RecommendationCard task={nextTask} featured />
            </section>
          ) : (
            <section className="recommendation-message empty-recommendations" role="status">
              <CheckCircle2 size={22} aria-hidden="true" />
              <div>
                <strong>
                  {recommendations.blocked > 0
                    ? "Your remaining tasks are waiting on prerequisites."
                    : "You’re all caught up."}
                </strong>
                <p>
                  {recommendations.blocked > 0
                    ? "Complete a prerequisite task to unlock your next recommendation."
                    : "There are no incomplete tasks to recommend right now."}
                </p>
              </div>
            </section>
          )}

          {rankedTasks.length > 1 && (
            <section
              className="recommendation-list-section"
              aria-labelledby="more-recommendations-heading"
            >
              <div className="section-head">
                <div>
                  <h2 id="more-recommendations-heading">More recommendations</h2>
                  <p>Ready tasks, ordered by highest SOR score.</p>
                </div>
                <span className="recommendation-count">{rankedTasks.length - 1} tasks</span>
              </div>
              <div className="recommendation-list">
                {rankedTasks.slice(1).map((task) => (
                  <RecommendationCard key={task.id} task={task} />
                ))}
              </div>
            </section>
          )}

          {recommendations.blocked > 0 && (
            <p className="blocked-note">
              {recommendations.blocked} task{recommendations.blocked === 1 ? " is" : "s are"} not
              shown because prerequisite tasks are still incomplete.
            </p>
          )}
        </>
      )}
    </main>
  );
}