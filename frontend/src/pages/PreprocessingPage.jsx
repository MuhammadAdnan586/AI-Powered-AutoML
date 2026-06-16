import React, { useState, useEffect } from "react";
import api from "../services/api";

const STEPS = [
  { id: 1, title: "Select Dataset", icon: "📁" },
  { id: 2, title: "Analyze Data", icon: "🔍" },
  { id: 3, title: "Configure", icon: "⚙️" },
  { id: 4, title: "Run & Review", icon: "✅" },
];

export default function PreprocessingPage() {
  const [currentStep, setCurrentStep] = useState(1);
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [problemTypeInfo, setProblemTypeInfo] = useState(null);
  const [targetColumn, setTargetColumn] = useState("");
  const [loading, setLoading] = useState(false);
  const [preprocessingResult, setPreprocessingResult] = useState(null);

  const [config, setConfig] = useState({
    remove_duplicates: true,
    missing_strategy: "auto",
    encoding_strategy: "auto",
    scaling_method: "standard",
    drop_threshold: 0.5,
  });

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      const res = await api.get("/api/datasets");
      setDatasets(res.data.datasets || []);
    } catch (e) {
      console.error(e);
    }
  };

  const analyzeDataset = async () => {
    if (!selectedDataset) return;
    setLoading(true);
    try {
      const res = await api.get(`/api/preprocessing/analyze?dataset_id=${selectedDataset.id}`);
      setDatasetInfo(res.data.info);
      setCurrentStep(2);
    } catch (e) {
      alert("Error analyzing dataset: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const detectProblemType = async () => {
    if (!targetColumn) return;
    try {
      const res = await api.post("/api/preprocessing/detect-problem-type", {
        dataset_id: selectedDataset.id,
        target_column: targetColumn,
      });
      setProblemTypeInfo(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const runPreprocessing = async () => {
    setLoading(true);
    try {
      const res = await api.post("/api/preprocessing/run", {
        dataset_id: selectedDataset.id,
        target_column: targetColumn,
        ...config,
      });
      setPreprocessingResult(res.data);
      setCurrentStep(4);
    } catch (e) {
      alert("Preprocessing failed: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const getMissingCount = () => {
    if (!datasetInfo?.missing_values) return 0;
    return Object.values(datasetInfo.missing_values).reduce((a, b) => a + b, 0);
  };

  return (
    <div style={s.page}>
      <h1 style={s.title}>🧹 Data Preprocessing</h1>
      <p style={s.subtitle}>Clean, encode, and scale your data for model training</p>

      {/* Step indicator */}
      <div style={s.stepBar}>
        {STEPS.map((step, idx) => (
          <React.Fragment key={step.id}>
            <div style={{ ...s.step, ...(currentStep >= step.id ? s.stepActive : {}) }}>
              <div style={{ ...s.stepCircle, ...(currentStep >= step.id ? s.stepCircleActive : {}) }}>
                {currentStep > step.id ? "✓" : step.icon}
              </div>
              <span style={s.stepLabel}>{step.title}</span>
            </div>
            {idx < STEPS.length - 1 && (
              <div style={{ ...s.stepLine, ...(currentStep > step.id ? s.stepLineActive : {}) }} />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Step 1: Select Dataset */}
      {currentStep === 1 && (
        <div style={s.card}>
          <h2 style={s.cardTitle}>Select a Dataset</h2>
          <div style={s.datasetGrid}>
            {datasets.map((d) => (
              <div
                key={d.id}
                style={{
                  ...s.datasetCard,
                  ...(selectedDataset?.id === d.id ? s.datasetCardSelected : {}),
                }}
                onClick={() => setSelectedDataset(d)}
              >
                <div style={s.datasetIcon}>📊</div>
                <div style={s.datasetName}>{d.original_name || d.name}</div>
                <div style={s.datasetMeta}>{d.rows} rows · {d.columns} columns</div>
                <div style={s.datasetDate}>
                  {d.version && <span style={s.versionBadge}>v{d.version}</span>}
                </div>
              </div>
            ))}
          </div>
          <button
            style={{ ...s.btn, opacity: !selectedDataset ? 0.5 : 1 }}
            onClick={analyzeDataset}
            disabled={!selectedDataset || loading}
          >
            {loading ? "Analyzing..." : "🔍 Analyze Dataset →"}
          </button>
        </div>
      )}

      {/* Step 2: Analyze */}
      {currentStep === 2 && datasetInfo && (
        <div>
          {/* Overview cards */}
          <div style={s.statsRow}>
            <div style={s.statCard}>
              <div style={s.statNum}>{datasetInfo.shape.rows}</div>
              <div style={s.statLbl}>Total Rows</div>
            </div>
            <div style={s.statCard}>
              <div style={s.statNum}>{datasetInfo.shape.columns}</div>
              <div style={s.statLbl}>Total Columns</div>
            </div>
            <div style={{ ...s.statCard, borderColor: getMissingCount() > 0 ? "#f59e0b" : "#10b981" }}>
              <div style={{ ...s.statNum, color: getMissingCount() > 0 ? "#f59e0b" : "#10b981" }}>
                {getMissingCount()}
              </div>
              <div style={s.statLbl}>Missing Values</div>
            </div>
            <div style={{ ...s.statCard, borderColor: datasetInfo.duplicate_rows > 0 ? "#ef4444" : "#10b981" }}>
              <div style={{ ...s.statNum, color: datasetInfo.duplicate_rows > 0 ? "#ef4444" : "#10b981" }}>
                {datasetInfo.duplicate_rows}
              </div>
              <div style={s.statLbl}>Duplicate Rows</div>
            </div>
            <div style={s.statCard}>
              <div style={s.statNum}>{datasetInfo.numeric_columns.length}</div>
              <div style={s.statLbl}>Numeric Columns</div>
            </div>
            <div style={s.statCard}>
              <div style={s.statNum}>{datasetInfo.categorical_columns.length}</div>
              <div style={s.statLbl}>Categorical Columns</div>
            </div>
          </div>

          {/* Column details */}
          <div style={s.card}>
            <h3 style={s.cardTitle}>Column Analysis</h3>
            <div style={s.colTable}>
              <div style={s.colHeader}>
                <span>Column Name</span>
                <span>Type</span>
                <span>Unique</span>
                <span>Missing</span>
                <span>Missing %</span>
              </div>
              {datasetInfo.columns.map((col) => {
                const missingPct = datasetInfo.missing_percentage?.[col] || 0;
                return (
                  <div key={col} style={s.colRow}>
                    <span style={s.colName}>{col}</span>
                    <span style={{
                      ...s.typeBadge,
                      background: datasetInfo.numeric_columns.includes(col) ? "#dbeafe" : "#fce7f3",
                      color: datasetInfo.numeric_columns.includes(col) ? "#1d4ed8" : "#be185d"
                    }}>
                      {datasetInfo.numeric_columns.includes(col) ? "Numeric" : "Categorical"}
                    </span>
                    <span>{datasetInfo.unique_counts?.[col]}</span>
                    <span style={{ color: (datasetInfo.missing_values?.[col] || 0) > 0 ? "#f59e0b" : "#10b981" }}>
                      {datasetInfo.missing_values?.[col] || 0}
                    </span>
                    <span>
                      <div style={s.missingBar}>
                        <div style={{
                          ...s.missingBarFill,
                          width: `${missingPct}%`,
                          background: missingPct > 30 ? "#ef4444" : missingPct > 10 ? "#f59e0b" : "#10b981"
                        }} />
                      </div>
                      {missingPct}%
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Target column selection */}
          <div style={s.card}>
            <h3 style={s.cardTitle}>🎯 Select Target Column</h3>
            <div style={s.targetRow}>
              <select
                style={s.select}
                value={targetColumn}
                onChange={(e) => setTargetColumn(e.target.value)}
                onBlur={detectProblemType}
              >
                <option value="">-- Select Target Column --</option>
                {datasetInfo.columns.map((col) => (
                  <option key={col} value={col}>{col}</option>
                ))}
              </select>
              <button style={s.detectBtn} onClick={detectProblemType} disabled={!targetColumn}>
                Auto-Detect Problem Type
              </button>
            </div>
            {problemTypeInfo && (
              <div style={{
                ...s.problemTypeBadge,
                background: problemTypeInfo.problem_type === "classification" ? "#ede9fe" : "#dcfce7",
                color: problemTypeInfo.problem_type === "classification" ? "#5b21b6" : "#166534"
              }}>
                <strong>
                  {problemTypeInfo.problem_type === "classification" ? "🎯" : "📈"}{" "}
                  {problemTypeInfo.problem_type === "classification" ? "Classification" : "Regression"}
                </strong>
                {" — "}
                {problemTypeInfo.reason}
                {" "}
                <span style={s.confidenceBadge}>
                  Confidence: {(problemTypeInfo.confidence * 100).toFixed(0)}%
                </span>
              </div>
            )}
          </div>

          <button style={s.btn} onClick={() => setCurrentStep(3)} disabled={!targetColumn}>
            ⚙️ Configure Preprocessing →
          </button>
        </div>
      )}

      {/* Step 3: Configure */}
      {currentStep === 3 && (
        <div style={s.card}>
          <h2 style={s.cardTitle}>⚙️ Preprocessing Configuration</h2>
          <div style={s.configGrid}>
            <div style={s.configSection}>
              <h3 style={s.configSectionTitle}>Data Cleaning</h3>
              <label style={s.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={config.remove_duplicates}
                  onChange={(e) => setConfig({ ...config, remove_duplicates: e.target.checked })}
                />
                Remove duplicate rows
              </label>
            </div>

            <div style={s.configSection}>
              <h3 style={s.configSectionTitle}>Missing Values</h3>
              {[
                { value: "auto", label: "Auto (Smart selection per column)" },
                { value: "impute", label: "Impute (Fill with mean/mode)" },
                { value: "drop", label: "Drop (Remove rows/columns)" },
              ].map((opt) => (
                <label key={opt.value} style={s.radioLabel}>
                  <input
                    type="radio"
                    name="missing"
                    value={opt.value}
                    checked={config.missing_strategy === opt.value}
                    onChange={() => setConfig({ ...config, missing_strategy: opt.value })}
                  />
                  {opt.label}
                </label>
              ))}
            </div>

            <div style={s.configSection}>
              <h3 style={s.configSectionTitle}>Encoding</h3>
              {[
                { value: "auto", label: "Auto (Label for low, One-hot for high)" },
                { value: "label", label: "Label Encoding (all categorical)" },
                { value: "onehot", label: "One-Hot Encoding (all categorical)" },
              ].map((opt) => (
                <label key={opt.value} style={s.radioLabel}>
                  <input
                    type="radio"
                    name="encoding"
                    value={opt.value}
                    checked={config.encoding_strategy === opt.value}
                    onChange={() => setConfig({ ...config, encoding_strategy: opt.value })}
                  />
                  {opt.label}
                </label>
              ))}
            </div>

            <div style={s.configSection}>
              <h3 style={s.configSectionTitle}>Feature Scaling</h3>
              {[
                { value: "standard", label: "Standard Scaler (mean=0, std=1)" },
                { value: "minmax", label: "MinMax Scaler (0 to 1)" },
                { value: "none", label: "No Scaling" },
              ].map((opt) => (
                <label key={opt.value} style={s.radioLabel}>
                  <input
                    type="radio"
                    name="scaling"
                    value={opt.value}
                    checked={config.scaling_method === opt.value}
                    onChange={() => setConfig({ ...config, scaling_method: opt.value })}
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </div>

          <div style={s.dropThresholdRow}>
            <label style={s.label}>Column Drop Threshold: {(config.drop_threshold * 100).toFixed(0)}%</label>
            <p style={s.hint}>Columns with more than this % missing will be dropped</p>
            <input
              type="range"
              min="0.2"
              max="0.9"
              step="0.1"
              value={config.drop_threshold}
              onChange={(e) => setConfig({ ...config, drop_threshold: parseFloat(e.target.value) })}
              style={s.slider}
            />
          </div>

          <button style={s.btn} onClick={runPreprocessing} disabled={loading}>
            {loading ? "Processing..." : "🚀 Run Preprocessing →"}
          </button>
        </div>
      )}

      {/* Step 4: Results */}
      {currentStep === 4 && preprocessingResult && (
        <div>
          <div style={{ ...s.card, borderLeft: "4px solid #10b981" }}>
            <h2 style={{ ...s.cardTitle, color: "#059669" }}>✅ Preprocessing Complete!</h2>
            <div style={s.statsRow}>
              <div style={s.statCard}>
                <div style={s.statNum}>{preprocessingResult.processed_shape?.[0]}</div>
                <div style={s.statLbl}>Final Rows</div>
              </div>
              <div style={s.statCard}>
                <div style={s.statNum}>{preprocessingResult.processed_shape?.[1]}</div>
                <div style={s.statLbl}>Final Columns</div>
              </div>
              <div style={s.statCard}>
                <div style={{ ...s.statNum, color: "#7c3aed" }}>
                  {preprocessingResult.problem_type?.problem_type}
                </div>
                <div style={s.statLbl}>Problem Type</div>
              </div>
            </div>
          </div>

          {preprocessingResult.preprocessing_report?.steps?.map((step, idx) => (
            <div key={idx} style={s.stepResult}>
              <div style={s.stepResultTitle}>
                {idx + 1}. {step.step.replace(/_/g, " ").toUpperCase()}
              </div>
              <div style={s.stepResultShape}>
                Shape after: {step.shape_after?.[0]} × {step.shape_after?.[1]}
              </div>
            </div>
          ))}

          <div style={s.actionRow}>
            <button style={s.btn} onClick={() => window.location.href = "/feature-engineering"}>
              🔧 Go to Feature Engineering →
            </button>
            <button style={{ ...s.btn, background: "#6b7280" }} onClick={() => setCurrentStep(1)}>
              ← Start Over
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

const s = {
  page: { padding: "24px", maxWidth: "1100px", margin: "0 auto", fontFamily: "system-ui, sans-serif" },
  title: { margin: 0, fontSize: "26px", fontWeight: 700, color: "#111827" },
  subtitle: { margin: "4px 0 24px", color: "#6b7280", fontSize: "14px" },
  stepBar: { display: "flex", alignItems: "center", marginBottom: "32px" },
  step: { display: "flex", flexDirection: "column", alignItems: "center", gap: "6px", opacity: 0.4 },
  stepActive: { opacity: 1 },
  stepCircle: { width: "44px", height: "44px", borderRadius: "50%", background: "#e5e7eb", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "18px" },
  stepCircleActive: { background: "#7c3aed", color: "#fff" },
  stepLabel: { fontSize: "12px", fontWeight: 500, color: "#374151", whiteSpace: "nowrap" },
  stepLine: { flex: 1, height: "2px", background: "#e5e7eb", margin: "0 8px", marginBottom: "20px" },
  stepLineActive: { background: "#7c3aed" },
  card: { background: "#fff", borderRadius: "12px", padding: "24px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", marginBottom: "20px" },
  cardTitle: { margin: "0 0 16px", fontSize: "18px", fontWeight: 600, color: "#111827" },
  datasetGrid: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px", marginBottom: "20px" },
  datasetCard: { border: "2px solid #e5e7eb", borderRadius: "10px", padding: "16px", cursor: "pointer", transition: "all 0.2s" },
  datasetCardSelected: { border: "2px solid #7c3aed", background: "#faf5ff" },
  datasetIcon: { fontSize: "28px", marginBottom: "8px" },
  datasetName: { fontWeight: 600, fontSize: "14px", color: "#111827", marginBottom: "4px" },
  datasetMeta: { fontSize: "12px", color: "#6b7280" },
  datasetDate: { marginTop: "8px" },
  versionBadge: { background: "#dbeafe", color: "#1d4ed8", padding: "2px 8px", borderRadius: "10px", fontSize: "11px" },
  btn: { padding: "12px 24px", background: "linear-gradient(135deg, #7c3aed, #4f46e5)", color: "#fff", border: "none", borderRadius: "8px", cursor: "pointer", fontWeight: 600, fontSize: "14px" },
  statsRow: { display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: "12px", marginBottom: "20px" },
  statCard: { background: "#fff", border: "1px solid #e5e7eb", borderRadius: "10px", padding: "16px", textAlign: "center" },
  statNum: { fontSize: "20px", fontWeight: 700, color: "#111827" },
  statLbl: { fontSize: "11px", color: "#6b7280", marginTop: "4px" },
  colTable: { display: "flex", flexDirection: "column", gap: "1px" },
  colHeader: { display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr 1.5fr", gap: "10px", padding: "8px 12px", background: "#f3f4f6", borderRadius: "6px", fontSize: "12px", fontWeight: 600, color: "#374151" },
  colRow: { display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr 1.5fr", gap: "10px", alignItems: "center", padding: "8px 12px", background: "#fff", borderRadius: "6px", fontSize: "13px", border: "1px solid #f3f4f6" },
  colName: { fontFamily: "monospace", fontWeight: 500 },
  typeBadge: { padding: "2px 8px", borderRadius: "10px", fontSize: "11px", fontWeight: 500, textAlign: "center" },
  missingBar: { height: "6px", background: "#e5e7eb", borderRadius: "3px", overflow: "hidden", display: "inline-block", width: "60px", verticalAlign: "middle", marginRight: "6px" },
  missingBarFill: { height: "100%", borderRadius: "3px" },
  targetRow: { display: "flex", gap: "12px", alignItems: "center" },
  select: { flex: 1, padding: "10px 12px", border: "1px solid #d1d5db", borderRadius: "8px", fontSize: "14px" },
  detectBtn: { padding: "10px 16px", background: "#ede9fe", color: "#5b21b6", border: "none", borderRadius: "8px", cursor: "pointer", fontWeight: 500, whiteSpace: "nowrap" },
  problemTypeBadge: { marginTop: "12px", padding: "12px 16px", borderRadius: "8px", fontSize: "14px" },
  confidenceBadge: { fontSize: "12px", opacity: 0.7 },
  configGrid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "20px" },
  configSection: { padding: "16px", background: "#f9fafb", borderRadius: "8px", display: "flex", flexDirection: "column", gap: "10px" },
  configSectionTitle: { margin: "0 0 4px", fontSize: "14px", fontWeight: 600, color: "#374151" },
  checkboxLabel: { display: "flex", alignItems: "center", gap: "8px", cursor: "pointer", fontSize: "14px" },
  radioLabel: { display: "flex", alignItems: "flex-start", gap: "8px", cursor: "pointer", fontSize: "13px", color: "#374151" },
  dropThresholdRow: { padding: "16px", background: "#f9fafb", borderRadius: "8px", marginBottom: "20px" },
  label: { fontSize: "14px", fontWeight: 600, color: "#374151" },
  hint: { margin: "4px 0 8px", fontSize: "12px", color: "#6b7280" },
  slider: { width: "100%", accentColor: "#7c3aed" },
  stepResult: { background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: "8px", padding: "12px 16px", marginBottom: "10px" },
  stepResultTitle: { fontWeight: 600, color: "#065f46", fontSize: "13px" },
  stepResultShape: { fontSize: "12px", color: "#059669", marginTop: "4px" },
  actionRow: { display: "flex", gap: "12px" },
};
