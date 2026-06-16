import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

const PROBLEM_TYPES = ["classification", "regression"];

const MODEL_ICONS = {
  XGBoost: "🚀",
  LightGBM: "⚡",
  "Random Forest": "🌲",
  "Gradient Boosting": "📈",
  "Logistic Regression": "📊",
  "Linear Regression": "📏",
  "Decision Tree": "🌿",
  "K-Nearest Neighbors": "🔍",
  "Naive Bayes": "🎯",
  "Support Vector Machine": "🔬",
  Ridge: "🏔️",
  Lasso: "🎣",
};

const CATEGORY_COLORS = {
  Boosting: "#7c3aed",
  Ensemble: "#059669",
  Linear: "#2563eb",
  Tree: "#d97706",
  Distance: "#db2777",
  Probabilistic: "#0891b2",
  Kernel: "#dc2626",
};

export default function AutoMLPage() {
  const navigate = useNavigate();
  const pollRef = useRef(null);

  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState("");
  const [targetColumn, setTargetColumn] = useState("");
  const [problemType, setProblemType] = useState("classification");
  const [columns, setColumns] = useState([]);
  const [testSize, setTestSize] = useState(0.2);
  const [hyperparamTuning, setHyperparamTuning] = useState(false);

  const [trainingStatus, setTrainingStatus] = useState(null); // null | 'loading' | 'training' | 'completed' | 'failed'
  const [sessionId, setSessionId] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [bestModel, setBestModel] = useState(null);
  const [results, setResults] = useState(null);
  const [activeTab, setActiveTab] = useState("setup"); // setup | training | leaderboard | details

  // Fetch datasets on mount
  useEffect(() => {
    fetchDatasets();
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const fetchDatasets = async () => {
    try {
      const res = await api.get("/api/datasets");
      setDatasets(res.data.datasets || []);
    } catch (err) {
      console.error("Error fetching datasets:", err);
    }
  };

  const fetchDatasetColumns = async (datasetId) => {
    try {
      const res = await api.get(`/api/preprocessing/analyze?dataset_id=${datasetId}`);
      setColumns(res.data.info?.columns || []);
    } catch (err) {
      console.error("Error fetching columns:", err);
    }
  };

  const detectProblemType = async () => {
    if (!selectedDataset || !targetColumn) return;
    try {
      const res = await api.post("/api/preprocessing/detect-problem-type", {
        dataset_id: parseInt(selectedDataset),
        target_column: targetColumn,
      });
      if (res.data.problem_type) {
        setProblemType(res.data.problem_type);
      }
    } catch (err) {
      console.error("Problem type detection failed:", err);
    }
  };

  const startTraining = async () => {
    if (!selectedDataset || !targetColumn) {
      alert("Please select a dataset and target column first.");
      return;
    }

    setTrainingStatus("loading");
    setActiveTab("training");
    setLeaderboard([]);
    setBestModel(null);

    try {
      const res = await api.post("/api/automl/train", {
        engineered_dataset_id: parseInt(selectedDataset),
        target_column: targetColumn,
        problem_type: problemType,
        test_size: testSize,
        hyperparameter_tuning: hyperparamTuning,
      });

      const sid = res.data.session_id;
      setSessionId(sid);
      setTrainingStatus("training");

      // Start polling
      pollRef.current = setInterval(() => pollStatus(sid), 3000);
    } catch (err) {
      setTrainingStatus("failed");
      console.error("Training failed to start:", err);
    }
  };

  const pollStatus = async (sid) => {
    try {
      const res = await api.get(`/api/automl/status/${sid}`);
      const status = res.data.status;

      if (status === "completed") {
        clearInterval(pollRef.current);
        setTrainingStatus("completed");
        const r = res.data.results;
        setResults(r);
        setLeaderboard(r.leaderboard || []);
        setBestModel(r.best_model);
        setActiveTab("leaderboard");
      } else if (status === "failed") {
        clearInterval(pollRef.current);
        setTrainingStatus("failed");
      } else {
        setTrainingStatus(status);
      }
    } catch (err) {
      console.error("Polling error:", err);
    }
  };

  const getPrimaryMetric = (modelResult) => {
    if (problemType === "classification") {
      return {
        label: "Accuracy",
        value: modelResult.metrics?.accuracy,
        percent: true,
      };
    }
    return {
      label: "R² Score",
      value: modelResult.metrics?.r2_score,
      percent: false,
    };
  };

  const getBarWidth = (value, maxValue) => {
    if (!value || !maxValue) return "0%";
    return `${Math.min((value / maxValue) * 100, 100)}%`;
  };

  const maxScore = leaderboard.length > 0
    ? Math.max(...leaderboard.map((m) => getPrimaryMetric(m).value || 0))
    : 1;

  return (
    <div style={styles.page}>
      {/* Header */}
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>🤖 AutoML Engine</h1>
          <p style={styles.subtitle}>Train multiple ML models simultaneously and compare results</p>
        </div>
        {trainingStatus === "completed" && (
          <div style={styles.headerBadge}>
            <span>✅ Training Complete</span>
            <span style={styles.bestModelBadge}>
              Best: {bestModel?.replace("_", " ")}
            </span>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div style={styles.tabs}>
        {["setup", "training", "leaderboard", "details"].map((tab) => (
          <button
            key={tab}
            style={{
              ...styles.tab,
              ...(activeTab === tab ? styles.activeTab : {}),
            }}
            onClick={() => setActiveTab(tab)}
          >
            {tab === "setup" && "⚙️ "}
            {tab === "training" && "🏋️ "}
            {tab === "leaderboard" && "🏆 "}
            {tab === "details" && "📊 "}
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Setup Tab */}
      {activeTab === "setup" && (
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>Training Configuration</h2>
          <div style={styles.grid2}>
            {/* Dataset selection */}
            <div style={styles.formGroup}>
              <label style={styles.label}>Dataset</label>
              <select
                style={styles.select}
                value={selectedDataset}
                onChange={(e) => {
                  setSelectedDataset(e.target.value);
                  if (e.target.value) fetchDatasetColumns(e.target.value);
                }}
              >
                <option value="">-- Select Dataset --</option>
                {datasets.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.original_name || d.name} ({d.rows} rows)
                  </option>
                ))}
              </select>
            </div>

            {/* Target column */}
            <div style={styles.formGroup}>
              <label style={styles.label}>Target Column</label>
              <select
                style={styles.select}
                value={targetColumn}
                onChange={(e) => {
                  setTargetColumn(e.target.value);
                }}
                onBlur={detectProblemType}
                disabled={!columns.length}
              >
                <option value="">-- Select Target --</option>
                {columns.map((col) => (
                  <option key={col} value={col}>{col}</option>
                ))}
              </select>
            </div>

            {/* Problem type */}
            <div style={styles.formGroup}>
              <label style={styles.label}>Problem Type</label>
              <div style={styles.radioGroup}>
                {PROBLEM_TYPES.map((pt) => (
                  <label key={pt} style={styles.radioLabel}>
                    <input
                      type="radio"
                      name="problemType"
                      value={pt}
                      checked={problemType === pt}
                      onChange={() => setProblemType(pt)}
                    />
                    {pt === "classification" ? "🎯 Classification" : "📈 Regression"}
                  </label>
                ))}
              </div>
            </div>

            {/* Test size */}
            <div style={styles.formGroup}>
              <label style={styles.label}>Test Size: {(testSize * 100).toFixed(0)}%</label>
              <input
                type="range"
                min="0.1"
                max="0.4"
                step="0.05"
                value={testSize}
                onChange={(e) => setTestSize(parseFloat(e.target.value))}
                style={styles.slider}
              />
              <div style={styles.sliderLabels}>
                <span>10%</span><span>40%</span>
              </div>
            </div>
          </div>

          {/* Hyperparameter tuning toggle */}
          <div style={styles.toggleRow}>
            <div>
              <strong>Hyperparameter Tuning</strong>
              <p style={styles.toggleDesc}>
                Use GridSearchCV to find optimal parameters. This takes longer but improves accuracy.
              </p>
            </div>
            <button
              style={{
                ...styles.toggle,
                background: hyperparamTuning ? "#7c3aed" : "#e5e7eb",
                color: hyperparamTuning ? "#fff" : "#374151",
              }}
              onClick={() => setHyperparamTuning(!hyperparamTuning)}
            >
              {hyperparamTuning ? "ON ✓" : "OFF"}
            </button>
          </div>

          <button
            style={{
              ...styles.trainBtn,
              opacity: !selectedDataset || !targetColumn ? 0.5 : 1,
            }}
            onClick={startTraining}
            disabled={!selectedDataset || !targetColumn}
          >
            🚀 Start AutoML Training
          </button>
        </div>
      )}

      {/* Training Tab */}
      {activeTab === "training" && (
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>Training Progress</h2>
          {trainingStatus === "loading" && (
            <div style={styles.statusBox}>
              <div style={styles.spinner} />
              <p>Initializing training session...</p>
            </div>
          )}
          {trainingStatus === "training" && (
            <div style={styles.statusBox}>
              <div style={styles.trainingAnimation}>
                {["XGBoost", "LightGBM", "Random Forest", "Gradient Boosting", "Logistic Regression"].map((m, i) => (
                  <div key={m} style={{ ...styles.trainingModel, animationDelay: `${i * 0.3}s` }}>
                    <span>{MODEL_ICONS[m] || "🤖"}</span>
                    <span style={styles.modelTrainingName}>{m}</span>
                    <div style={styles.trainingBar}>
                      <div style={{ ...styles.trainingBarFill, animationDelay: `${i * 0.5}s` }} />
                    </div>
                  </div>
                ))}
              </div>
              <p style={styles.trainingText}>Training models simultaneously... ⏳</p>
              <p style={styles.trainingSubtext}>Session: {sessionId}</p>
            </div>
          )}
          {trainingStatus === "failed" && (
            <div style={styles.errorBox}>
              <p>❌ Training failed. Please check your dataset and try again.</p>
              <button style={styles.retryBtn} onClick={() => setActiveTab("setup")}>← Back to Setup</button>
            </div>
          )}
          {trainingStatus === "completed" && (
            <div style={styles.successBox}>
              <p>✅ Training complete! View results in the Leaderboard tab.</p>
              <button style={styles.leaderboardBtn} onClick={() => setActiveTab("leaderboard")}>
                🏆 View Leaderboard →
              </button>
            </div>
          )}
        </div>
      )}

      {/* Leaderboard Tab */}
      {activeTab === "leaderboard" && (
        <div>
          {leaderboard.length === 0 ? (
            <div style={styles.emptyState}>
              <p>No results yet. Start training first.</p>
              <button style={styles.trainBtn} onClick={() => setActiveTab("setup")}>
                ⚙️ Setup Training
              </button>
            </div>
          ) : (
            <div>
              {/* Summary stats */}
              <div style={styles.statsRow}>
                <div style={styles.statCard}>
                  <div style={styles.statValue}>{leaderboard.length}</div>
                  <div style={styles.statLabel}>Models Trained</div>
                </div>
                <div style={styles.statCard}>
                  <div style={{ ...styles.statValue, color: "#7c3aed" }}>
                    {bestModel?.replace(/_/g, " ")}
                  </div>
                  <div style={styles.statLabel}>Best Model</div>
                </div>
                <div style={styles.statCard}>
                  <div style={{ ...styles.statValue, color: "#059669" }}>
                    {leaderboard[0] && (
                      `${(getPrimaryMetric(leaderboard[0]).value * 100).toFixed(1)}%`
                    )}
                  </div>
                  <div style={styles.statLabel}>Best Score</div>
                </div>
                <div style={styles.statCard}>
                  <div style={styles.statValue}>
                    {problemType === "classification" ? "🎯" : "📈"} {problemType}
                  </div>
                  <div style={styles.statLabel}>Problem Type</div>
                </div>
              </div>

              {/* Leaderboard table */}
              <div style={styles.card}>
                <h2 style={styles.cardTitle}>🏆 Model Leaderboard</h2>
                <div style={styles.leaderboardTable}>
                  {leaderboard.map((model, idx) => {
                    const metric = getPrimaryMetric(model);
                    const isWinner = idx === 0;
                    return (
                      <div
                        key={model.model_name}
                        style={{
                          ...styles.leaderboardRow,
                          ...(isWinner ? styles.winnerRow : {}),
                          borderLeft: `4px solid ${CATEGORY_COLORS[model.category] || "#ccc"}`,
                        }}
                      >
                        <div style={styles.rankBadge}>
                          {idx === 0 ? "🥇" : idx === 1 ? "🥈" : idx === 2 ? "🥉" : `#${idx + 1}`}
                        </div>

                        <div style={styles.modelInfo}>
                          <div style={styles.modelNameRow}>
                            <span style={styles.modelIcon}>
                              {MODEL_ICONS[model.display_name] || "🤖"}
                            </span>
                            <span style={styles.modelDisplayName}>{model.display_name}</span>
                            <span
                              style={{
                                ...styles.categoryBadge,
                                background: CATEGORY_COLORS[model.category] + "22",
                                color: CATEGORY_COLORS[model.category],
                              }}
                            >
                              {model.category}
                            </span>
                            {isWinner && <span style={styles.bestBadge}>BEST</span>}
                          </div>
                          <div style={styles.metricsRow}>
                            {problemType === "classification" ? (
                              <>
                                <span style={styles.metricChip}>F1: {model.metrics?.f1_score?.toFixed(3)}</span>
                                <span style={styles.metricChip}>Precision: {model.metrics?.precision?.toFixed(3)}</span>
                                <span style={styles.metricChip}>Recall: {model.metrics?.recall?.toFixed(3)}</span>
                                {model.metrics?.roc_auc && (
                                  <span style={styles.metricChip}>AUC: {model.metrics.roc_auc?.toFixed(3)}</span>
                                )}
                              </>
                            ) : (
                              <>
                                <span style={styles.metricChip}>RMSE: {model.metrics?.rmse?.toFixed(3)}</span>
                                <span style={styles.metricChip}>MAE: {model.metrics?.mae?.toFixed(3)}</span>
                                <span style={styles.metricChip}>MSE: {model.metrics?.mse?.toFixed(3)}</span>
                              </>
                            )}
                            <span style={styles.metricChip}>
                              CV: {(model.cv_mean * 100).toFixed(1)}% ± {(model.cv_std * 100).toFixed(1)}%
                            </span>
                            <span style={styles.metricChip}>⏱ {model.training_time_seconds}s</span>
                          </div>
                        </div>

                        <div style={styles.scoreSection}>
                          <div style={styles.scoreValue}>
                            {(metric.value * 100).toFixed(1)}%
                          </div>
                          <div style={styles.scoreLabel}>{metric.label}</div>
                          <div style={styles.scoreBar}>
                            <div
                              style={{
                                ...styles.scoreBarFill,
                                width: getBarWidth(metric.value, maxScore),
                                background: isWinner ? "#7c3aed" : "#93c5fd",
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Details Tab */}
      {activeTab === "details" && results && (
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>📊 Training Details</h2>
          <div style={styles.detailsGrid}>
            <div style={styles.detailItem}>
              <span style={styles.detailLabel}>Session ID</span>
              <span style={styles.detailValue}>{results.session_id}</span>
            </div>
            <div style={styles.detailItem}>
              <span style={styles.detailLabel}>Dataset Shape</span>
              <span style={styles.detailValue}>{results.dataset_shape?.join(" × ")}</span>
            </div>
            <div style={styles.detailItem}>
              <span style={styles.detailLabel}>Features Used</span>
              <span style={styles.detailValue}>{results.feature_count}</span>
            </div>
            <div style={styles.detailItem}>
              <span style={styles.detailLabel}>Training Samples</span>
              <span style={styles.detailValue}>{results.train_samples}</span>
            </div>
            <div style={styles.detailItem}>
              <span style={styles.detailLabel}>Test Samples</span>
              <span style={styles.detailValue}>{results.test_samples}</span>
            </div>
            <div style={styles.detailItem}>
              <span style={styles.detailLabel}>Models Trained</span>
              <span style={styles.detailValue}>{results.models_trained}</span>
            </div>
            <div style={styles.detailItem}>
              <span style={styles.detailLabel}>Models Failed</span>
              <span style={styles.detailValue}>{results.models_failed}</span>
            </div>
            <div style={styles.detailItem}>
              <span style={styles.detailLabel}>Hyperparameter Tuning</span>
              <span style={styles.detailValue}>{results.hyperparameter_tuning ? "Yes ✓" : "No"}</span>
            </div>
          </div>

          {results.failed_models && results.failed_models.length > 0 && (
            <div style={styles.failedModels}>
              <h3 style={{ color: "#dc2626" }}>❌ Failed Models</h3>
              {results.failed_models.map((m) => (
                <div key={m.model_name} style={styles.failedItem}>
                  <strong>{m.display_name}</strong>: {m.error}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const styles = {
  page: { padding: "24px", maxWidth: "1200px", margin: "0 auto", fontFamily: "system-ui, sans-serif" },
  header: { display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "24px" },
  title: { margin: 0, fontSize: "28px", fontWeight: 700, color: "#111827" },
  subtitle: { margin: "4px 0 0", color: "#6b7280", fontSize: "14px" },
  headerBadge: { display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "6px" },
  bestModelBadge: { background: "#7c3aed", color: "#fff", padding: "4px 12px", borderRadius: "20px", fontSize: "13px" },
  tabs: { display: "flex", gap: "4px", marginBottom: "24px", borderBottom: "2px solid #e5e7eb", paddingBottom: "0" },
  tab: { padding: "10px 20px", border: "none", borderRadius: "8px 8px 0 0", background: "transparent", cursor: "pointer", color: "#6b7280", fontSize: "14px", fontWeight: 500 },
  activeTab: { background: "#7c3aed", color: "#fff" },
  card: { background: "#fff", borderRadius: "12px", padding: "24px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", marginBottom: "20px" },
  cardTitle: { margin: "0 0 20px", fontSize: "18px", fontWeight: 600, color: "#111827" },
  grid2: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "20px" },
  formGroup: { display: "flex", flexDirection: "column", gap: "6px" },
  label: { fontSize: "13px", fontWeight: 600, color: "#374151" },
  select: { padding: "8px 12px", border: "1px solid #d1d5db", borderRadius: "8px", fontSize: "14px", background: "#fff" },
  radioGroup: { display: "flex", gap: "16px" },
  radioLabel: { display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "14px" },
  slider: { width: "100%", accentColor: "#7c3aed" },
  sliderLabels: { display: "flex", justifyContent: "space-between", fontSize: "11px", color: "#9ca3af" },
  toggleRow: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px", background: "#f9fafb", borderRadius: "8px", marginBottom: "20px" },
  toggleDesc: { margin: "4px 0 0", fontSize: "13px", color: "#6b7280" },
  toggle: { padding: "8px 20px", borderRadius: "20px", border: "none", cursor: "pointer", fontWeight: 600, fontSize: "14px", transition: "all 0.2s" },
  trainBtn: { width: "100%", padding: "14px", background: "linear-gradient(135deg, #7c3aed, #4f46e5)", color: "#fff", border: "none", borderRadius: "10px", fontSize: "16px", fontWeight: 600, cursor: "pointer" },
  statusBox: { textAlign: "center", padding: "40px 20px" },
  spinner: { width: "40px", height: "40px", border: "4px solid #e5e7eb", borderTopColor: "#7c3aed", borderRadius: "50%", animation: "spin 0.8s linear infinite", margin: "0 auto 16px" },
  trainingAnimation: { display: "flex", flexDirection: "column", gap: "12px", maxWidth: "400px", margin: "0 auto 24px" },
  trainingModel: { display: "grid", gridTemplateColumns: "30px 1fr auto", gap: "10px", alignItems: "center" },
  modelTrainingName: { fontSize: "14px", textAlign: "left" },
  trainingBar: { width: "80px", height: "6px", background: "#e5e7eb", borderRadius: "3px", overflow: "hidden" },
  trainingBarFill: { height: "100%", background: "#7c3aed", borderRadius: "3px", animation: "progress 2s ease-in-out infinite alternate" },
  trainingText: { fontSize: "16px", color: "#374151", marginBottom: "8px" },
  trainingSubtext: { fontSize: "12px", color: "#9ca3af", fontFamily: "monospace" },
  errorBox: { background: "#fef2f2", border: "1px solid #fecaca", borderRadius: "8px", padding: "20px", textAlign: "center", color: "#dc2626" },
  successBox: { background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: "8px", padding: "20px", textAlign: "center" },
  leaderboardBtn: { marginTop: "12px", padding: "10px 24px", background: "#7c3aed", color: "#fff", border: "none", borderRadius: "8px", cursor: "pointer", fontSize: "14px", fontWeight: 600 },
  retryBtn: { marginTop: "12px", padding: "8px 20px", background: "#fff", border: "1px solid #d1d5db", borderRadius: "8px", cursor: "pointer" },
  emptyState: { textAlign: "center", padding: "60px 20px", color: "#6b7280" },
  statsRow: { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "16px", marginBottom: "20px" },
  statCard: { background: "#fff", borderRadius: "12px", padding: "20px", textAlign: "center", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" },
  statValue: { fontSize: "20px", fontWeight: 700, color: "#111827", marginBottom: "4px" },
  statLabel: { fontSize: "12px", color: "#6b7280" },
  leaderboardTable: { display: "flex", flexDirection: "column", gap: "12px" },
  leaderboardRow: { display: "grid", gridTemplateColumns: "50px 1fr 130px", gap: "16px", alignItems: "center", padding: "16px", background: "#f9fafb", borderRadius: "10px", border: "1px solid #e5e7eb" },
  winnerRow: { background: "#faf5ff", border: "1px solid #ddd6fe" },
  rankBadge: { fontSize: "24px", textAlign: "center" },
  modelInfo: { display: "flex", flexDirection: "column", gap: "8px" },
  modelNameRow: { display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" },
  modelIcon: { fontSize: "18px" },
  modelDisplayName: { fontWeight: 600, fontSize: "15px", color: "#111827" },
  categoryBadge: { padding: "2px 8px", borderRadius: "12px", fontSize: "11px", fontWeight: 500 },
  bestBadge: { background: "#7c3aed", color: "#fff", padding: "2px 8px", borderRadius: "12px", fontSize: "11px", fontWeight: 700 },
  metricsRow: { display: "flex", gap: "6px", flexWrap: "wrap" },
  metricChip: { background: "#fff", border: "1px solid #e5e7eb", padding: "2px 8px", borderRadius: "10px", fontSize: "11px", color: "#374151" },
  scoreSection: { textAlign: "center" },
  scoreValue: { fontSize: "22px", fontWeight: 700, color: "#7c3aed" },
  scoreLabel: { fontSize: "11px", color: "#6b7280", marginBottom: "4px" },
  scoreBar: { height: "6px", background: "#e5e7eb", borderRadius: "3px", overflow: "hidden" },
  scoreBarFill: { height: "100%", borderRadius: "3px", transition: "width 0.5s ease" },
  detailsGrid: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px" },
  detailItem: { display: "flex", flexDirection: "column", gap: "4px", padding: "12px", background: "#f9fafb", borderRadius: "8px" },
  detailLabel: { fontSize: "11px", color: "#6b7280", fontWeight: 500 },
  detailValue: { fontSize: "14px", fontWeight: 600, color: "#111827" },
  failedModels: { marginTop: "20px", padding: "16px", background: "#fef2f2", borderRadius: "8px" },
  failedItem: { fontSize: "13px", color: "#dc2626", padding: "4px 0" },
};
