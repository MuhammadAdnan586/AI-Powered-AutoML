import React, { useState, useEffect } from "react";
import api from "../services/api";

export default function FeatureEngineeringPage() {
  const [processedDatasets, setProcessedDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState("");
  const [targetColumn, setTargetColumn] = useState("");
  const [columns, setColumns] = useState([]);
  const [problemType, setProblemType] = useState("classification");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [correlationData, setCorrelationData] = useState(null);
  const [activeView, setActiveView] = useState("config"); // config | results | correlation

  const [config, setConfig] = useState({
    auto_generate: true,
    remove_low_variance: true,
    remove_correlated: true,
    select_best: true,
    k_best: 20,
    variance_threshold: 0.01,
    correlation_threshold: 0.95,
  });

  useEffect(() => {
    fetchProcessedDatasets();
  }, []);

  const fetchProcessedDatasets = async () => {
    try {
      const res = await api.get("/api/datasets/processed");
      setProcessedDatasets(res.data.datasets || []);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchColumns = async (dsId) => {
    try {
      const res = await api.get(`/api/preprocessing/analyze?dataset_id=${dsId}`);
      setColumns(res.data.info?.columns || []);
    } catch (e) {}
  };

  const runFE = async () => {
    if (!selectedDataset || !targetColumn) return;
    setLoading(true);
    try {
      const res = await api.post("/api/feature-engineering/run", {
        processed_dataset_id: parseInt(selectedDataset),
        target_column: targetColumn,
        problem_type: problemType,
        ...config,
      });
      setResult(res.data);
      setActiveView("results");
    } catch (e) {
      alert("Feature Engineering failed: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchCorrelation = async () => {
    if (!selectedDataset) return;
    try {
      const res = await api.get(`/api/feature-engineering/correlation/${selectedDataset}`);
      setCorrelationData(res.data);
      setActiveView("correlation");
    } catch (e) {
      alert("Could not fetch correlation data.");
    }
  };

  const getHeatmapColor = (value) => {
    const v = Math.max(-1, Math.min(1, value));
    if (v > 0) {
      const r = Math.round(255 * (1 - v));
      return `rgb(${r}, ${Math.round(255 * (1 - v * 0.3))}, 255)`;
    } else {
      const g = Math.round(255 * (1 + v));
      return `rgb(255, ${g}, ${Math.round(255 * (1 + v * 0.3))})`;
    }
  };

  return (
    <div style={s.page}>
      <h1 style={s.title}>🔧 Feature Engineering</h1>
      <p style={s.subtitle}>Auto-generate, select, and optimize features for better model performance</p>

      <div style={s.viewTabs}>
        {["config", "results", "correlation"].map((v) => (
          <button key={v} style={{ ...s.tab, ...(activeView === v ? s.tabActive : {}) }} onClick={() => setActiveView(v)}>
            {v === "config" && "⚙️ Configuration"}
            {v === "results" && "📊 Results"}
            {v === "correlation" && "🔥 Correlation Matrix"}
          </button>
        ))}
      </div>

      {activeView === "config" && (
        <div>
          {/* Dataset Setup */}
          <div style={s.card}>
            <h2 style={s.cardTitle}>Dataset Setup</h2>
            <div style={s.grid3}>
              <div style={s.fg}>
                <label style={s.label}>Processed Dataset</label>
                <select style={s.select} value={selectedDataset}
                  onChange={(e) => { setSelectedDataset(e.target.value); if (e.target.value) fetchColumns(e.target.value); }}>
                  <option value="">-- Select --</option>
                  {processedDatasets.map((d) => (
                    <option key={d.id} value={d.id}>{d.name || `Dataset #${d.id}`} ({d.rows} rows)</option>
                  ))}
                </select>
              </div>
              <div style={s.fg}>
                <label style={s.label}>Target Column</label>
                <select style={s.select} value={targetColumn} onChange={(e) => setTargetColumn(e.target.value)} disabled={!columns.length}>
                  <option value="">-- Select --</option>
                  {columns.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div style={s.fg}>
                <label style={s.label}>Problem Type</label>
                <select style={s.select} value={problemType} onChange={(e) => setProblemType(e.target.value)}>
                  <option value="classification">Classification</option>
                  <option value="regression">Regression</option>
                </select>
              </div>
            </div>
          </div>

          {/* Feature Engineering Options */}
          <div style={s.card}>
            <h2 style={s.cardTitle}>Feature Engineering Steps</h2>
            <div style={s.optionsGrid}>
              {[
                {
                  key: "auto_generate",
                  title: "🤖 Auto Feature Generation",
                  desc: "Create interaction, ratio, log, sqrt, squared, and row-aggregate features automatically."
                },
                {
                  key: "remove_low_variance",
                  title: "📉 Remove Low Variance",
                  desc: `Remove features with variance below ${config.variance_threshold}. These features add little value.`
                },
                {
                  key: "remove_correlated",
                  title: "🔗 Remove Correlated",
                  desc: `Remove features with correlation above ${config.correlation_threshold}. Reduces redundancy.`
                },
                {
                  key: "select_best",
                  title: "⭐ Select Best Features",
                  desc: `Keep top ${config.k_best} most important features using statistical tests.`
                }
              ].map((opt) => (
                <div key={opt.key} style={{ ...s.optionCard, ...(config[opt.key] ? s.optionCardActive : {}) }}>
                  <div style={s.optionHeader}>
                    <div>
                      <div style={s.optionTitle}>{opt.title}</div>
                      <div style={s.optionDesc}>{opt.desc}</div>
                    </div>
                    <button
                      style={{ ...s.toggle, background: config[opt.key] ? "#7c3aed" : "#e5e7eb", color: config[opt.key] ? "#fff" : "#374151" }}
                      onClick={() => setConfig({ ...config, [opt.key]: !config[opt.key] })}
                    >
                      {config[opt.key] ? "ON" : "OFF"}
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Advanced params */}
            <div style={s.advancedParams}>
              <h3 style={s.advTitle}>Advanced Parameters</h3>
              <div style={s.paramGrid}>
                <div style={s.fg}>
                  <label style={s.label}>Top K Features: {config.k_best}</label>
                  <input type="range" min="5" max="50" value={config.k_best}
                    onChange={(e) => setConfig({ ...config, k_best: parseInt(e.target.value) })}
                    style={s.slider} disabled={!config.select_best} />
                </div>
                <div style={s.fg}>
                  <label style={s.label}>Variance Threshold: {config.variance_threshold}</label>
                  <input type="range" min="0.001" max="0.1" step="0.001" value={config.variance_threshold}
                    onChange={(e) => setConfig({ ...config, variance_threshold: parseFloat(e.target.value) })}
                    style={s.slider} disabled={!config.remove_low_variance} />
                </div>
                <div style={s.fg}>
                  <label style={s.label}>Correlation Threshold: {config.correlation_threshold}</label>
                  <input type="range" min="0.7" max="0.99" step="0.01" value={config.correlation_threshold}
                    onChange={(e) => setConfig({ ...config, correlation_threshold: parseFloat(e.target.value) })}
                    style={s.slider} disabled={!config.remove_correlated} />
                </div>
              </div>
            </div>
          </div>

          <div style={s.btnRow}>
            <button style={s.btn} onClick={runFE} disabled={loading || !selectedDataset || !targetColumn}>
              {loading ? "Processing..." : "🚀 Run Feature Engineering"}
            </button>
            <button style={s.secondaryBtn} onClick={fetchCorrelation} disabled={!selectedDataset}>
              🔥 View Correlation Matrix
            </button>
          </div>
        </div>
      )}

      {activeView === "results" && result && (
        <div>
          <div style={{ ...s.card, borderLeft: "4px solid #10b981" }}>
            <h2 style={{ ...s.cardTitle, color: "#059669" }}>✅ Feature Engineering Complete!</h2>
            <div style={s.resultStats}>
              {result.feature_engineering_report?.steps?.map((step, idx) => (
                <div key={idx} style={s.stepBox}>
                  <div style={s.stepNum}>{idx + 1}</div>
                  <div>
                    <div style={s.stepName}>{step.step.replace(/_/g, " ")}</div>
                    <div style={s.stepShape}>
                      Shape after: {step.shape_after?.[0]} × {step.shape_after?.[1]}
                    </div>
                    {step.details?.new_features_generated !== undefined && (
                      <div style={s.stepDetail}>+{step.details.new_features_generated} features generated</div>
                    )}
                    {step.removed_features?.length > 0 && (
                      <div style={s.stepDetail}>-{step.removed_features.length} features removed</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div style={s.card}>
            <h3 style={s.cardTitle}>Final Feature Set</h3>
            <div style={s.finalFeatures}>
              {result.final_columns?.map((col) => (
                <span key={col} style={s.featureTag}>{col}</span>
              ))}
            </div>
            <p style={s.hint}>{result.final_columns?.length} features ready for training</p>
          </div>

          <button style={s.btn} onClick={() => window.location.href = "/automl"}>
            🤖 Go to AutoML Training →
          </button>
        </div>
      )}

      {activeView === "correlation" && correlationData && (
        <div style={s.card}>
          <h2 style={s.cardTitle}>🔥 Correlation Heatmap</h2>
          <p style={s.hint}>Values close to 1 or -1 indicate high correlation</p>
          <div style={{ overflowX: "auto" }}>
            <table style={s.heatmapTable}>
              <thead>
                <tr>
                  <th style={s.heatmapHeader}></th>
                  {correlationData.columns.map((col) => (
                    <th key={col} style={s.heatmapColHeader}>{col.substring(0, 8)}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {correlationData.matrix.map((row, i) => (
                  <tr key={i}>
                    <td style={s.heatmapRowHeader}>{correlationData.columns[i]?.substring(0, 8)}</td>
                    {row.map((val, j) => (
                      <td key={j} style={{ ...s.heatmapCell, background: getHeatmapColor(val), color: Math.abs(val) > 0.6 ? "#fff" : "#333" }}>
                        {val.toFixed(2)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeView === "correlation" && !correlationData && (
        <div style={s.emptyState}>
          <p>Select a dataset and click "View Correlation Matrix" to see the heatmap.</p>
          <button style={s.btn} onClick={() => setActiveView("config")}>← Go to Configuration</button>
        </div>
      )}
    </div>
  );
}

const s = {
  page: { padding: "24px", maxWidth: "1100px", margin: "0 auto", fontFamily: "system-ui, sans-serif" },
  title: { margin: 0, fontSize: "26px", fontWeight: 700, color: "#111827" },
  subtitle: { margin: "4px 0 20px", color: "#6b7280", fontSize: "14px" },
  viewTabs: { display: "flex", gap: "4px", marginBottom: "24px" },
  tab: { padding: "10px 20px", border: "1px solid #e5e7eb", borderRadius: "8px", background: "#fff", cursor: "pointer", fontSize: "14px", fontWeight: 500, color: "#374151" },
  tabActive: { background: "#7c3aed", color: "#fff", border: "1px solid #7c3aed" },
  card: { background: "#fff", borderRadius: "12px", padding: "24px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", marginBottom: "20px" },
  cardTitle: { margin: "0 0 16px", fontSize: "18px", fontWeight: 600, color: "#111827" },
  grid3: { display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "16px" },
  fg: { display: "flex", flexDirection: "column", gap: "6px" },
  label: { fontSize: "13px", fontWeight: 600, color: "#374151" },
  select: { padding: "8px 12px", border: "1px solid #d1d5db", borderRadius: "8px", fontSize: "14px" },
  optionsGrid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "20px" },
  optionCard: { border: "2px solid #e5e7eb", borderRadius: "10px", padding: "16px", transition: "all 0.2s" },
  optionCardActive: { border: "2px solid #c4b5fd", background: "#faf5ff" },
  optionHeader: { display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "12px" },
  optionTitle: { fontWeight: 600, fontSize: "14px", color: "#111827", marginBottom: "4px" },
  optionDesc: { fontSize: "12px", color: "#6b7280" },
  toggle: { padding: "6px 14px", borderRadius: "16px", border: "none", cursor: "pointer", fontWeight: 600, fontSize: "12px", whiteSpace: "nowrap", flexShrink: 0 },
  advancedParams: { padding: "16px", background: "#f9fafb", borderRadius: "8px" },
  advTitle: { margin: "0 0 16px", fontSize: "14px", fontWeight: 600 },
  paramGrid: { display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "16px" },
  slider: { width: "100%", accentColor: "#7c3aed" },
  btnRow: { display: "flex", gap: "12px" },
  btn: { padding: "12px 24px", background: "linear-gradient(135deg, #7c3aed, #4f46e5)", color: "#fff", border: "none", borderRadius: "8px", cursor: "pointer", fontWeight: 600, fontSize: "14px" },
  secondaryBtn: { padding: "12px 24px", background: "#fff", color: "#374151", border: "2px solid #e5e7eb", borderRadius: "8px", cursor: "pointer", fontWeight: 600, fontSize: "14px" },
  resultStats: { display: "flex", flexDirection: "column", gap: "10px" },
  stepBox: { display: "flex", gap: "14px", alignItems: "flex-start", padding: "12px", background: "#f9fafb", borderRadius: "8px" },
  stepNum: { width: "28px", height: "28px", background: "#7c3aed", color: "#fff", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: "13px", flexShrink: 0 },
  stepName: { fontWeight: 600, fontSize: "14px", color: "#111827", textTransform: "capitalize" },
  stepShape: { fontSize: "12px", color: "#6b7280", marginTop: "2px" },
  stepDetail: { fontSize: "12px", color: "#059669", marginTop: "2px" },
  finalFeatures: { display: "flex", flexWrap: "wrap", gap: "6px" },
  featureTag: { padding: "4px 10px", background: "#ede9fe", color: "#5b21b6", borderRadius: "12px", fontSize: "12px", fontFamily: "monospace" },
  hint: { fontSize: "12px", color: "#6b7280", marginTop: "8px" },
  heatmapTable: { borderCollapse: "collapse" },
  heatmapHeader: { padding: "8px", fontSize: "11px" },
  heatmapColHeader: { padding: "6px 4px", fontSize: "9px", fontWeight: 600, color: "#374151", transform: "rotate(-45deg)", display: "block", whiteSpace: "nowrap", minWidth: "50px" },
  heatmapRowHeader: { padding: "4px 8px", fontSize: "9px", fontWeight: 600, color: "#374151", whiteSpace: "nowrap" },
  heatmapCell: { width: "50px", height: "50px", textAlign: "center", fontSize: "10px", fontWeight: 500, border: "1px solid #fff" },
  emptyState: { textAlign: "center", padding: "60px", color: "#6b7280" },
};
