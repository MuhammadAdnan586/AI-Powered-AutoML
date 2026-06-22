"use client";
import { useState, useEffect } from "react";
import { datasetService } from "@/services/dataset.service";
import { intelligenceService } from "@/services/intelligence.service";
import type { DatasetListItem, Dataset } from "@/types";
import LoadingSpinner from "@/components/UI/LoadingSpinner";
import { getErrorMessage } from "@/utils";
import toast from "react-hot-toast";
import {
  Database, Brain, MessageSquare, FileText, BarChart3,
  Loader2, Send, Download, Sparkles, ChevronRight, Trophy,
  TrendingUp, AlertCircle, ArrowLeft, Wand2, Target,
} from "lucide-react";
import Link from "next/link";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";

type Tab = "quality" | "explain" | "predict" | "chat" | "reports";

const tooltipStyle = {
  contentStyle: { backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: 8, fontSize: 12 },
  labelStyle: { color: "#cbd5e1" },
  itemStyle: { color: "#e2e8f0" },
};

export default function IntelligencePage() {
  const [datasets, setDatasets] = useState<DatasetListItem[]>([]);
  const [loadingDatasets, setLoadingDatasets] = useState(true);
  const [selectedDataset, setSelectedDataset] = useState<DatasetListItem | null>(null);
  const [datasetDetail, setDatasetDetail] = useState<Dataset | null>(null);

  // Best/recommended session for the selected dataset (only one — no list)
  const [selectedSession, setSelectedSession] = useState<any | null>(null);
  const [loadingBestSession, setLoadingBestSession] = useState(false);

  const [activeTab, setActiveTab] = useState<Tab>("quality");

  // Data Quality
  const [qualityLoading, setQualityLoading] = useState(false);
  const [qualityReport, setQualityReport] = useState<any>(null);

  // Explainability
  const [explainLoading, setExplainLoading] = useState(false);
  const [explanation, setExplanation] = useState<any>(null);

  // Predict (raw form)
  const [formValues, setFormValues] = useState<Record<string, string>>({});
  const [predicting, setPredicting] = useState(false);
  const [predictionResult, setPredictionResult] = useState<any>(null);

  // Chat
  const [chatMessages, setChatMessages] = useState<{ role: string; text: string }[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  // Reports
  const [reportLoading, setReportLoading] = useState<string | null>(null);

  useEffect(() => {
    datasetService
      .list(0, 50)
      .then(setDatasets)
      .catch((e) => toast.error(getErrorMessage(e)))
      .finally(() => setLoadingDatasets(false));
  }, []);

  // Fetch only the single best/recommended session whenever the dataset changes
  useEffect(() => {
    if (!selectedDataset) {
      setSelectedSession(null);
      setDatasetDetail(null);
      return;
    }
    setLoadingBestSession(true);
    setSelectedSession(null);
    intelligenceService
      .getBestSession(selectedDataset.id)
      .then((res) => setSelectedSession(res.session))
      .catch(() => setSelectedSession(null))
      .finally(() => setLoadingBestSession(false));

    datasetService
      .getById(selectedDataset.id)
      .then(setDatasetDetail)
      .catch(() => setDatasetDetail(null));
  }, [selectedDataset]);

  // Build empty form values whenever the dataset/target is known
  useEffect(() => {
    if (!datasetDetail?.column_names || !selectedSession?.target_column) {
      setFormValues({});
      return;
    }
    const initial: Record<string, string> = {};
    datasetDetail.column_names
      .filter((col) => col !== selectedSession.target_column)
      .forEach((col) => { initial[col] = ""; });
    setFormValues(initial);
    setPredictionResult(null);
  }, [datasetDetail, selectedSession]);

  const handleSelectDataset = (ds: DatasetListItem) => {
    setSelectedDataset(ds);
    setQualityReport(null);
    setExplanation(null);
    setChatMessages([]);
    setPredictionResult(null);
  };

  const loadQualityReport = async () => {
    if (!selectedDataset) return;
    setQualityLoading(true);
    try {
      const res = await intelligenceService.getQualityReport(selectedDataset.id);
      setQualityReport(res.report);
    } catch (e) {
      toast.error(getErrorMessage(e));
    } finally {
      setQualityLoading(false);
    }
  };

  const loadExplanation = async () => {
    if (!selectedSession) {
      toast.error("No trained model found for this dataset yet.");
      return;
    }
    setExplainLoading(true);
    try {
      const res = await intelligenceService.explainModel(selectedSession.session_id, 50);
      setExplanation(res.explanation);
    } catch (e) {
      toast.error(getErrorMessage(e));
    } finally {
      setExplainLoading(false);
    }
  };

  const handlePredict = async () => {
    if (!selectedSession) {
      toast.error("No trained model found for this dataset yet.");
      return;
    }
    setPredicting(true);
    setPredictionResult(null);
    try {
      const res = await intelligenceService.predictFromForm(selectedSession.session_id, formValues);
      setPredictionResult(res);
    } catch (e) {
      toast.error(getErrorMessage(e));
    } finally {
      setPredicting(false);
    }
  };

  const sendMessage = async () => {
    if (!selectedDataset || !chatInput.trim()) return;
    const userMsg = chatInput.trim();
    setChatMessages((prev) => [...prev, { role: "user", text: userMsg }]);
    setChatInput("");
    setChatLoading(true);
    try {
      const res = await intelligenceService.sendChatMessage(selectedDataset.id, userMsg);
      setChatMessages((prev) => [...prev, { role: "assistant", text: res.assistant_response }]);
    } catch (e) {
      toast.error(getErrorMessage(e));
    } finally {
      setChatLoading(false);
    }
  };

  const handleReport = async (type: "pdf" | "excel") => {
    if (!selectedDataset) return;
    setReportLoading(type);
    try {
      const modelName = selectedSession?.best_model;
      const res =
        type === "pdf"
          ? await intelligenceService.generatePdfReport(selectedDataset.id, modelName)
          : await intelligenceService.exportExcelReport(selectedDataset.id, modelName);
toast.success(res.message || "Report generated!");
      const filename = (res.download_url as string)?.split("/").pop();
      if (filename) {
        await intelligenceService.downloadReport(filename);
      }
    } catch (e) {
      toast.error(getErrorMessage(e));
    } finally {
      setReportLoading(null);
    }
  };

  if (loadingDatasets) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" text="Loading datasets..." />
      </div>
    );
  }

  // ── Chart data prep ────────────────────────────────────────────────────────

  const missingChartData = qualityReport?.missing_values?.columns
    ? Object.entries(qualityReport.missing_values.columns)
        .map(([name, v]: [string, any]) => ({ name, missing: v.missing_count }))
        .sort((a, b) => b.missing - a.missing)
        .slice(0, 8)
    : [];

  const outlierChartData = qualityReport?.outliers
    ? Object.entries(qualityReport.outliers)
        .map(([name, v]: [string, any]) => ({ name, outliers: v.outlier_count }))
        .sort((a, b) => b.outliers - a.outliers)
        .slice(0, 8)
    : [];

  const featureImportanceChartData = explanation?.feature_importance
    ? explanation.feature_importance.slice(0, 15).map((f: any) => ({
        name: f.feature,
        importance: f.importance,
      }))
    : [];

  const probabilityChartData = predictionResult?.probabilities?.[0]
    ? predictionResult.probabilities[0].map((p: number, i: number) => ({
        name: `Class ${i}`,
        probability: p,
      }))
    : [];

  const formColumns = datasetDetail?.column_names?.filter(
    (col) => col !== selectedSession?.target_column
  ) ?? [];

  const isNumericColumn = (col: string) => {
    const dtype = datasetDetail?.dtypes_info?.[col] ?? "";
    return dtype.includes("int") || dtype.includes("float");
  };

  return (
    <div className="space-y-6 max-w-7xl">
      <div className="flex items-center gap-3">
        <Link href="/dashboard" className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition-all">
          <ArrowLeft size={18} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Brain size={22} className="text-sky-400" />
            AI Intelligence Layer
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Explainability, data quality, AI chat assistant, and reports
          </p>
        </div>
      </div>

      {!selectedDataset ? (
        <div className="card">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
            <Database size={16} className="text-sky-400" />
            Select a Dataset
          </h3>
          {datasets.length === 0 ? (
            <p className="text-slate-500 text-sm">No datasets found. Upload one first.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {datasets.map((ds) => (
                <button
                  key={ds.id}
                  onClick={() => handleSelectDataset(ds)}
                  className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 transition-all text-left"
                >
                  <div>
                    <p className="text-slate-200 font-medium text-sm">{ds.name}</p>
                    <p className="text-slate-500 text-xs mt-0.5">
                      {ds.row_count} rows · {ds.column_count} cols
                    </p>
                  </div>
                  <ChevronRight size={16} className="text-slate-500" />
                </button>
              ))}
            </div>
          )}
        </div>
      ) : (
        <>
          {/* Dataset header */}
          <div className="card space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-xs">Selected Dataset</p>
                <p className="text-white font-semibold">{selectedDataset.name}</p>
                <p className="text-slate-500 text-xs">{selectedDataset.row_count} rows · {selectedDataset.column_count} cols</p>
              </div>
              <button onClick={() => setSelectedDataset(null)} className="btn-secondary text-xs px-3 py-2">
                Change
              </button>
            </div>

            {/* Recommended (best) model — only one, no list */}
            <div>
              <p className="text-slate-400 text-xs mb-2">Recommended Model</p>
              {loadingBestSession ? (
                <LoadingSpinner size="sm" text="Finding best model..." />
              ) : selectedSession ? (
                <div className="bg-sky-500/10 border border-sky-500/20 rounded-xl p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <Trophy size={14} className="text-yellow-400" />
                    <p className="text-sky-300 font-medium text-sm">
                      {selectedSession.best_model?.replace(/_/g, " ")}
                    </p>
                  </div>
                  <p className="text-slate-400 text-xs">
                    Score: {selectedSession.best_score?.toFixed(4)} · {selectedSession.target_column} · {selectedSession.problem_type} · {selectedSession.created_at?.slice(0, 10)}
                  </p>
                </div>
              ) : (
                <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-3 text-sm text-yellow-300 flex items-center gap-2">
                  <AlertCircle size={14} />
                  No trained model found for this dataset yet. Train one first on the AutoML page.
                </div>
              )}
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 border-b border-slate-800 pb-px overflow-x-auto">
            {[
              { id: "quality", label: "Data Quality", icon: BarChart3 },
              { id: "explain", label: "Explainability", icon: Sparkles },
              { id: "predict", label: "Predict", icon: Wand2 },
              { id: "chat", label: "AI Chat", icon: MessageSquare },
              { id: "reports", label: "Reports", icon: FileText },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as Tab)}
                className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-all whitespace-nowrap ${
                  activeTab === tab.id
                    ? "border-sky-500 text-sky-400"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <tab.icon size={15} />
                {tab.label}
              </button>
            ))}
          </div>

          {/* Data Quality */}
          {activeTab === "quality" && (
            <div className="card">
              {!qualityReport ? (
                <button onClick={loadQualityReport} disabled={qualityLoading} className="btn-primary">
                  {qualityLoading ? <Loader2 size={14} className="animate-spin" /> : <BarChart3 size={14} />}
                  Generate Quality Report
                </button>
              ) : (
                <div className="space-y-5">
                  <div className="flex items-center gap-5 p-4 bg-sky-500/10 border border-sky-500/20 rounded-xl">
                    <div className="text-4xl font-bold text-sky-400">{qualityReport.quality_score}</div>
                    <div>
                      <p className="text-white font-semibold text-lg">Grade: {qualityReport.quality_grade}</p>
                      <p className="text-slate-400 text-sm">Overall data quality score</p>
                    </div>
                  </div>

                  <div className="grid sm:grid-cols-3 gap-3">
                    <div className="bg-slate-900/50 rounded-lg p-3">
                      <p className="text-xs text-slate-500">Missing Values</p>
                      <p className="text-sm text-slate-200 font-semibold">
                        {qualityReport.missing_values?.total_missing ?? 0} cells ({qualityReport.missing_values?.missing_percentage ?? 0}%)
                      </p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-3">
                      <p className="text-xs text-slate-500">Duplicate Rows</p>
                      <p className="text-sm text-slate-200 font-semibold">
                        {qualityReport.duplicates?.total_duplicates ?? 0} ({qualityReport.duplicates?.duplicate_percentage ?? 0}%)
                      </p>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-3">
                      <p className="text-xs text-slate-500">Columns with Outliers</p>
                      <p className="text-sm text-slate-200 font-semibold">
                        {qualityReport.outliers ? Object.keys(qualityReport.outliers).length : 0}
                      </p>
                    </div>
                  </div>

                  {missingChartData.length > 0 && (
                    <div>
                      <p className="text-xs text-slate-500 mb-2">Missing values by column</p>
                      <ResponsiveContainer width="100%" height={Math.max(120, missingChartData.length * 32)}>
                        <BarChart data={missingChartData} layout="vertical" margin={{ left: 10, right: 20 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                          <XAxis type="number" stroke="#64748b" fontSize={11} allowDecimals={false} />
                          <YAxis type="category" dataKey="name" stroke="#64748b" fontSize={11} width={110} />
                          <Tooltip {...tooltipStyle} />
                          <Bar dataKey="missing" radius={[0, 4, 4, 0]}>
                            {missingChartData.map((_, idx) => <Cell key={idx} fill="#f87171" />)}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  )}

                  {outlierChartData.length > 0 && (
                    <div>
                      <p className="text-xs text-slate-500 mb-2">Outliers by column</p>
                      <ResponsiveContainer width="100%" height={Math.max(120, outlierChartData.length * 32)}>
                        <BarChart data={outlierChartData} layout="vertical" margin={{ left: 10, right: 20 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                          <XAxis type="number" stroke="#64748b" fontSize={11} allowDecimals={false} />
                          <YAxis type="category" dataKey="name" stroke="#64748b" fontSize={11} width={110} />
                          <Tooltip {...tooltipStyle} />
                          <Bar dataKey="outliers" radius={[0, 4, 4, 0]}>
                            {outlierChartData.map((_, idx) => <Cell key={idx} fill="#fb923c" />)}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  )}

                  {qualityReport.recommendations?.length > 0 && (
                    <div>
                      <p className="text-slate-300 text-sm font-medium mb-2 flex items-center gap-2">
                        <AlertCircle size={14} className="text-yellow-400" /> Recommendations
                      </p>
                      <ul className="space-y-1.5">
                        {qualityReport.recommendations.map((r: string, i: number) => (
                          <li key={i} className="text-slate-400 text-sm flex items-start gap-2">
                            <span className="text-yellow-400 mt-0.5">•</span> {r}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <button onClick={() => setQualityReport(null)} className="btn-secondary text-xs">Regenerate</button>
                </div>
              )}
            </div>
          )}

          {/* Explainability */}
          {activeTab === "explain" && (
            <div className="card space-y-4">
              {!selectedSession && !loadingBestSession && (
                <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3 text-sm text-yellow-300 flex items-center gap-2">
                  <AlertCircle size={14} />
                  No trained model found for this dataset yet. Train one first.
                </div>
              )}

              {selectedSession && !explanation && (
                <div className="bg-slate-800/50 rounded-lg p-3 text-xs text-slate-400 mb-2">
                  Generate SHAP (SHapley Additive exPlanations) for <span className="text-slate-200">{selectedSession.best_model?.replace(/_/g, " ")}</span> model trained on <span className="text-slate-200">{selectedDataset.name}</span>.
                  <br/>
                  <span className="text-yellow-400">Note: Tree-based models (XGBoost, Random Forest, LightGBM) are fast. Gradient Boosting may take 1-2 minutes.</span>
                </div>
              )}

              {!explanation ? (
                <button onClick={loadExplanation} disabled={explainLoading || !selectedSession} className="btn-primary disabled:opacity-50">
                  {explainLoading ? (
                    <>
                      <Loader2 size={14} className="animate-spin" />
                      Computing SHAP values... (may take 1-2 min)
                    </>
                  ) : (
                    <>
                      <Sparkles size={14} />
                      Generate SHAP Explanation
                    </>
                  )}
                </button>
              ) : (
                <div className="space-y-4">
                  <p className="text-slate-300 text-sm font-medium flex items-center gap-2">
                    <TrendingUp size={14} className="text-sky-400" />
                    Feature Importance (SHAP) — Top 15
                  </p>

                  <ResponsiveContainer width="100%" height={Math.max(160, featureImportanceChartData.length * 32)}>
                    <BarChart data={featureImportanceChartData} layout="vertical" margin={{ left: 10, right: 30 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                      <XAxis type="number" stroke="#64748b" fontSize={11} />
                      <YAxis type="category" dataKey="name" stroke="#64748b" fontSize={11} width={130} />
                      <Tooltip {...tooltipStyle} formatter={(v: number) => v.toFixed(4)} />
                      <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
                        {featureImportanceChartData.map((_, idx) => (
                          <Cell key={idx} fill={idx === 0 ? "#4ade80" : "#38bdf8"} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>

                  <p className="text-xs text-slate-500 border-t border-slate-800 pt-2">
                    Explainer: {explanation.explainer_type} · Top features: {explanation.top_features?.join(", ")}
                  </p>
                  <button onClick={() => setExplanation(null)} className="btn-secondary text-xs">Regenerate</button>
                </div>
              )}
            </div>
          )}

          {/* Predict */}
          {activeTab === "predict" && (
            <div className="card space-y-5">
              {!selectedSession && !loadingBestSession ? (
                <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3 text-sm text-yellow-300 flex items-center gap-2">
                  <AlertCircle size={14} />
                  No trained model found for this dataset yet. Train one first on the AutoML page.
                </div>
              ) : (
                <>
                  <div className="flex items-center gap-2">
                    <Target size={16} className="text-sky-400" />
                    <p className="text-white font-semibold text-sm">
                      Predict <span className="text-sky-400">{selectedSession?.target_column}</span> for a new entry
                    </p>
                  </div>
                  <p className="text-slate-500 text-xs">
                    Fill in the values below — these are the original columns from your dataset
                    (the target column is excluded since that's what gets predicted).
                  </p>

                  {!datasetDetail ? (
                    <LoadingSpinner size="sm" text="Loading form..." />
                  ) : (
                    <div className="grid sm:grid-cols-2 gap-4">
                      {formColumns.map((col) => (
                        <div key={col}>
                          <label className="block text-xs font-medium text-slate-400 mb-1.5">{col}</label>
                          <input
                            type={isNumericColumn(col) ? "number" : "text"}
                            step="any"
                            value={formValues[col] ?? ""}
                            onChange={(e) => setFormValues((prev) => ({ ...prev, [col]: e.target.value }))}
                            placeholder={isNumericColumn(col) ? "0" : "value"}
                            className="input"
                          />
                        </div>
                      ))}
                    </div>
                  )}

                  <button
                    onClick={handlePredict}
                    disabled={predicting || !selectedSession || !datasetDetail}
                    className="btn-primary disabled:opacity-50"
                  >
                    {predicting ? <Loader2 size={14} className="animate-spin" /> : <Wand2 size={14} />}
                    {predicting ? "Predicting..." : "Predict"}
                  </button>

                  {predictionResult && (
                    <div className="bg-gradient-to-r from-sky-500/10 to-green-500/10 border border-sky-500/20 rounded-xl p-5">
                      <p className="text-xs text-slate-400 mb-1">
                        Predicted {predictionResult.target_column}
                      </p>
                      <p className="text-3xl font-bold text-white">
                        {String(predictionResult.prediction?.[0])}
                      </p>
                      <p className="text-xs text-slate-500 mt-1">
                        Model: {predictionResult.model_used?.replace(/_/g, " ")} · {predictionResult.problem_type}
                      </p>

                      {probabilityChartData.length > 0 && (
                        <div className="mt-4">
                          <p className="text-xs text-slate-500 mb-2">Class probabilities</p>
                          <ResponsiveContainer width="100%" height={Math.max(100, probabilityChartData.length * 32)}>
                            <BarChart data={probabilityChartData} layout="vertical" margin={{ left: 10, right: 30 }}>
                              <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                              <XAxis type="number" stroke="#64748b" fontSize={11} domain={[0, 1]} />
                              <YAxis type="category" dataKey="name" stroke="#64748b" fontSize={11} width={70} />
                              <Tooltip {...tooltipStyle} formatter={(v: number) => v.toFixed(4)} />
                              <Bar dataKey="probability" radius={[0, 4, 4, 0]}>
                                {probabilityChartData.map((_, idx) => <Cell key={idx} fill="#38bdf8" />)}
                              </Bar>
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          {/* AI Chat */}
          {activeTab === "chat" && (
            <div className="card flex flex-col h-[500px]">
              <div className="flex-1 overflow-y-auto space-y-3 mb-4 pr-1">
                {chatMessages.length === 0 && (
                  <div className="text-center mt-10 space-y-2">
                    <MessageSquare size={28} className="text-slate-700 mx-auto" />
                    <p className="text-slate-500 text-sm">Ask anything about your dataset</p>
                    <div className="flex flex-wrap justify-center gap-2 mt-3">
                      {["What are the top features?", "Show missing values summary", "What is the data distribution?"].map((hint) => (
                        <button key={hint} onClick={() => setChatInput(hint)}
                          className="text-xs bg-slate-800 text-slate-400 px-3 py-1.5 rounded-lg hover:bg-slate-700">
                          {hint}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                {chatMessages.map((msg, i) => (
                  <div key={i} className={`p-3 rounded-xl text-sm max-w-[80%] whitespace-pre-wrap ${
                    msg.role === "user" ? "bg-sky-600 text-white ml-auto" : "bg-slate-800 text-slate-200"
                  }`}>
                    {msg.text}
                  </div>
                ))}
                {chatLoading && (
                  <div className="bg-slate-800 text-slate-400 text-sm p-3 rounded-xl max-w-[80%] flex items-center gap-2">
                    <Loader2 size={12} className="animate-spin" /> Thinking...
                  </div>
                )}
              </div>
              <div className="flex gap-2">
                <input value={chatInput} onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
                  placeholder="Ask about your dataset..." className="input flex-1" disabled={chatLoading} />
                <button onClick={sendMessage} disabled={chatLoading || !chatInput.trim()} className="btn-primary px-4">
                  {chatLoading ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
                </button>
              </div>
            </div>
          )}

          {/* Reports */}
          {activeTab === "reports" && (
            <div className="card space-y-4">
              {!selectedSession && (
                <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3 text-sm text-yellow-300 flex items-center gap-2">
                  <AlertCircle size={14} /> No trained model found — report will use dataset-level info only.
                </div>
              )}
              <p className="text-slate-400 text-sm">
                Generate report for <span className="text-slate-200 font-medium">{selectedDataset.name}</span>
                {selectedSession && <> · model: <span className="text-sky-400">{selectedSession.best_model?.replace(/_/g, " ")}</span></>}
              </p>
              <div className="flex gap-3 flex-wrap">
                <button onClick={() => handleReport("pdf")} disabled={reportLoading === "pdf"} className="btn-primary">
                  {reportLoading === "pdf" ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
                  Generate PDF Report
                </button>
                <button onClick={() => handleReport("excel")} disabled={reportLoading === "excel"} className="btn-secondary">
                  {reportLoading === "excel" ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
                  Export Excel Report
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}