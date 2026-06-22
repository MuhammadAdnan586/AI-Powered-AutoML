"use client";
import { useState, useEffect, useCallback, useRef } from "react";
import { datasetService } from "@/services/dataset.service";
import { automlService } from "@/services/automl.service";
import { intelligenceService } from "@/services/intelligence.service";
import type { DatasetListItem } from "@/types";
import LoadingSpinner from "@/components/UI/LoadingSpinner";
import { getErrorMessage } from "@/utils";
import toast from "react-hot-toast";
import {
  Database, Settings2, Cpu, Trophy, ChevronRight, ChevronDown, CheckCircle2,
  Loader2, Play, ArrowLeft, ArrowRight, Sparkles, AlertTriangle, AlertCircle,
Clock, Target, Layers, Eye, Gauge, Zap, BarChart2, Brain, TrendingUp, Download,
} from "lucide-react";
import Link from "next/link";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  LineChart, Line, Legend,
} from "recharts";

type Step = "select" | "preprocess" | "feature" | "train" | "results";

const tooltipStyle = {
  contentStyle: { backgroundColor: "#0f172a", border: "1px solid #1e293b", borderRadius: 8, fontSize: 12 },
  labelStyle: { color: "#94a3b8" },
  itemStyle: { color: "#e2e8f0" },
};

const MODEL_COLORS: Record<number, string> = {
  0: "#6366f1",
  1: "#8b5cf6",
  2: "#a78bfa",
  3: "#c4b5fd",
  4: "#ddd6fe",
  5: "#ede9fe",
  6: "#f5f3ff",
};

function gradeColor(grade?: string) {
  if (!grade) return "border-slate-600 text-slate-300";
  if (grade.startsWith("A")) return "border-emerald-500 text-emerald-400";
  if (grade.startsWith("B")) return "border-indigo-500 text-indigo-400";
  if (grade.startsWith("C")) return "border-amber-500 text-amber-400";
  if (grade.startsWith("D")) return "border-orange-500 text-orange-400";
  return "border-red-500 text-red-400";
}

function RawDataTable({ rows }: { rows: Record<string, any>[] }) {
  if (!rows || rows.length === 0) {
    return <div className="p-6 text-center text-slate-500 text-sm">No preview data available</div>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead>
          <tr className="bg-slate-900/80">
            {Object.keys(rows[0]).map((col) => (
              <th key={col} className="px-3 py-2.5 text-left text-indigo-300/70 font-medium whitespace-nowrap border-b border-slate-700/50 tracking-wide uppercase text-[10px]">{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-b border-slate-800/40 hover:bg-indigo-500/5 transition-colors">
              {Object.values(row).map((val, j) => (
                <td key={j} className="px-3 py-2 text-slate-300 whitespace-nowrap max-w-[140px] truncate font-mono text-[11px]">
                  {val === null || val === undefined ? <span className="text-slate-600 italic">null</span> : String(val)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function TrainingPage() {
  const [step, setStep] = useState<Step>("select");
  const [datasets, setDatasets] = useState<DatasetListItem[]>([]);
  const [loadingDatasets, setLoadingDatasets] = useState(true);
  const [selectedDataset, setSelectedDataset] = useState<DatasetListItem | null>(null);
  const [targetColumn, setTargetColumn] = useState("");
  const [columns, setColumns] = useState<string[]>([]);
  const [datasetDetail, setDatasetDetail] = useState<any>(null);
  const [qualityReport, setQualityReport] = useState<any>(null);
  const [loadingQuality, setLoadingQuality] = useState(false);
  const [preprocessing, setPreprocessing] = useState(false);
  const [processedId, setProcessedId] = useState<number | null>(null);
  const [problemType, setProblemType] = useState<string>("classification");
  const [engineering, setEngineering] = useState(false);
  const [engineeredId, setEngineeredId] = useState<number | null>(null);
  const [engineeredPreview, setEngineeredPreview] = useState<any>(null);
  const [loadingEngineeredPreview, setLoadingEngineeredPreview] = useState(false);
  const [training, setTraining] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [trainingStatus, setTrainingStatus] = useState<string>("");
  const [trainingProgress, setTrainingProgress] = useState(0);
  const pollRef = useRef<NodeJS.Timeout | null>(null);
  const [report, setReport] = useState<any>(null);
  const [loadingReport, setLoadingReport] = useState(false);
  const [expandedModel, setExpandedModel] = useState<string | null>(null);
  const [downloadingModel, setDownloadingModel] = useState(false);
  const [downloadingDataset, setDownloadingDataset] = useState(false);

  useEffect(() => {
    datasetService
      .list(0, 50)
      .then((data) => setDatasets(data.filter((d) => d.status === "ready")))
      .catch((err) => toast.error(getErrorMessage(err)))
      .finally(() => setLoadingDatasets(false));
  }, []);

  useEffect(() => {
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, []);

  useEffect(() => {
    if (step === "preprocess" && selectedDataset && !qualityReport && !loadingQuality) {
      setLoadingQuality(true);
      intelligenceService
        .getQualityReport(selectedDataset.id)
        .then((res) => setQualityReport(res.report))
        .catch((err) => toast.error(getErrorMessage(err)))
        .finally(() => setLoadingQuality(false));
    }
  }, [step, selectedDataset, qualityReport, loadingQuality]);

  useEffect(() => {
    if (step === "train" && engineeredId && !engineeredPreview && !loadingEngineeredPreview) {
      setLoadingEngineeredPreview(true);
      automlService
        .getEngineeredPreview(engineeredId)
        .then((res) => setEngineeredPreview(res.info))
        .catch((err) => toast.error(getErrorMessage(err)))
        .finally(() => setLoadingEngineeredPreview(false));
    }
  }, [step, engineeredId, engineeredPreview, loadingEngineeredPreview]);

  const loadFullReport = async (sid: string) => {
    setLoadingReport(true);
    try {
      const result = await automlService.getFullReport(sid);
      setReport(result);
      setSessionId(sid);
      setStep("results");
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setLoadingReport(false);
    }
  };

  const handleSelectDataset = async (ds: DatasetListItem) => {
    setSelectedDataset(ds);
    setQualityReport(null);
    setDatasetDetail(null);
    try {
      const full = await datasetService.getById(ds.id);
      setColumns(full.column_names ?? []);
      setDatasetDetail(full);
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  const handleStartPreprocessing = async () => {
    if (!selectedDataset || !targetColumn) { toast.error("Please select a dataset and target column"); return; }
    setPreprocessing(true);
    try {
      const result = await automlService.runPreprocessing({
        dataset_id: selectedDataset.id,
        target_column: targetColumn,
        remove_duplicates: true,
        missing_strategy: "auto",
        encoding_strategy: "auto",
        scaling_method: "standard",
      });
      setProcessedId(result.processed_dataset_id);
      if (result.problem_type?.problem_type) setProblemType(result.problem_type.problem_type);
      toast.success("Preprocessing complete!");
      setStep("feature");
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setPreprocessing(false);
    }
  };

  const handleRunFeatureEngineering = async () => {
    if (!processedId) return;
    setEngineering(true);
    try {
      const result = await automlService.runFeatureEngineering({
        processed_dataset_id: processedId,
        target_column: targetColumn,
        problem_type: problemType,
        auto_generate: false,
        remove_low_variance: false,
        remove_correlated: false,
        select_best: false,
        k_best: 50,
      });
      setEngineeredId(result.engineered_dataset_id);
      toast.success("Feature engineering complete!");
      setStep("train");
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setEngineering(false);
    }
  };

  const pollStatus = useCallback((sid: string) => {
    pollRef.current = setInterval(async () => {
      try {
        const status = await automlService.getTrainingStatus(sid);
        setTrainingStatus(status.status);
        setTrainingProgress(status.progress ?? 0);
        if (status.status === "completed") {
          if (pollRef.current) clearInterval(pollRef.current);
          setTraining(false);
          toast.success("Training complete!");
          await loadFullReport(sid);
        } else if (status.status === "failed") {
          if (pollRef.current) clearInterval(pollRef.current);
          setTraining(false);
          toast.error(status.error || "Training failed");
        }
      } catch (err) {
        if (pollRef.current) clearInterval(pollRef.current);
        setTraining(false);
        toast.error(getErrorMessage(err));
      }
    }, 2000);
  }, []);

  const handleStartTraining = async () => {
    if (!engineeredId) return;
    setTraining(true);
    setTrainingProgress(0);
    setTrainingStatus("starting");
    try {
      const result = await automlService.startTraining({
        engineered_dataset_id: engineeredId,
        target_column: targetColumn,
        problem_type: problemType,
        test_size: 0.2,
        hyperparameter_tuning: false,
      });
      setSessionId(result.session_id);
      pollStatus(result.session_id);
    } catch (err) {
      toast.error(getErrorMessage(err));
      setTraining(false);
    }
  };

  const handleDownloadModel = async () => {
    if (!sessionId) return;
    setDownloadingModel(true);
    try {
      await automlService.downloadTrainedModel(sessionId);
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setDownloadingModel(false);
    }
  };

  const handleDownloadDataset = async () => {
    if (!sessionId) return;
    setDownloadingDataset(true);
    try {
      await automlService.downloadEngineeredDataset(sessionId);
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setDownloadingDataset(false);
    }
  };

  const resetWizard = () => {
    setStep("select");
    setSelectedDataset(null);
    setTargetColumn("");
    setDatasetDetail(null);
    setQualityReport(null);
    setProcessedId(null);
    setEngineeredId(null);
    setEngineeredPreview(null);
    setSessionId(null);
    setReport(null);
    setExpandedModel(null);
  };

  const steps: { key: Step; label: string; icon: any }[] = [
    { key: "select", label: "Select Dataset", icon: Database },
    { key: "preprocess", label: "Preprocessing", icon: Settings2 },
    { key: "feature", label: "Feature Engineering", icon: Sparkles },
    { key: "train", label: "Train Models", icon: Cpu },
    { key: "results", label: "Results", icon: Trophy },
  ];
  const stepIndex = steps.findIndex((s) => s.key === step);

  const renderStepDetail = (s: any) => {
    if (!s.details) return null;
    return (
      <div className="mt-2 space-y-1">
        {Object.entries(s.details).map(([key, val]: [string, any]) => (
          <div key={key} className="text-xs text-slate-400 flex items-start gap-2">
            <span className="text-slate-500 min-w-[120px]">{key}:</span>
            <span className="text-slate-300">{typeof val === "object" ? (val.action ?? JSON.stringify(val)) : String(val)}</span>
          </div>
        ))}
      </div>
    );
  };

  const missingChartData = qualityReport?.missing_values?.columns
    ? Object.entries(qualityReport.missing_values.columns)
        .map(([name, v]: [string, any]) => ({ name, missing: v.missing_count }))
        .sort((a, b) => b.missing - a.missing).slice(0, 8)
    : [];

  const outlierChartData = qualityReport?.outliers
    ? Object.entries(qualityReport.outliers)
        .map(([name, v]: [string, any]) => ({ name, outliers: v.outlier_count }))
        .sort((a, b) => b.outliers - a.outliers).slice(0, 8)
    : [];

  const leaderboardChartData = report?.leaderboard
    ? report.leaderboard.map((e: any) => ({
        name: e.display_name ?? e.model_name,
        score: e.metrics?.accuracy ?? e.metrics?.r2_score ?? 0,
      }))
    : [];

  return (
    <div className="min-h-screen" style={{ background: "linear-gradient(135deg, #0a0e1a 0%, #0f1629 50%, #0a0e1a 100%)" }}>
      <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">

        {/* Header */}
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/5 transition-all border border-white/5">
            <ArrowLeft size={18} />
          </Link>
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: "linear-gradient(135deg, #6366f1, #8b5cf6)" }}>
                <Brain size={18} className="text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white tracking-tight">AutoML Engine</h1>
                <p className="text-slate-500 text-xs">Train and compare multiple models automatically</p>
              </div>
            </div>
          </div>
        </div>

        {/* Step Indicator */}
        <div className="relative">
          <div className="flex items-center gap-0 overflow-x-auto">
            {steps.map((s, i) => (
              <div key={s.key} className="flex items-center flex-shrink-0">
                <div className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold transition-all rounded-xl ${
                  i === stepIndex
                    ? "text-white shadow-lg shadow-indigo-500/20"
                    : i < stepIndex
                    ? "text-emerald-400"
                    : "text-slate-600"
                }`}
                style={i === stepIndex ? { background: "linear-gradient(135deg, #6366f1, #8b5cf6)" } : {}}>
                  <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold flex-shrink-0 ${
                    i === stepIndex ? "bg-white/20" :
                    i < stepIndex ? "bg-emerald-500/20 border border-emerald-500/40" :
                    "bg-slate-800 border border-slate-700"
                  }`}>
                    {i < stepIndex ? <CheckCircle2 size={12} className="text-emerald-400" /> : i + 1}
                  </span>
                  <span className="hidden sm:block">{s.label}</span>
                </div>
                {i < steps.length - 1 && (
                  <div className={`w-6 h-px mx-1 ${i < stepIndex ? "bg-emerald-500/40" : "bg-slate-700/50"}`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* â”€â”€ STEP 1: Select Dataset â”€â”€ */}
        {step === "select" && (
          <div className="rounded-2xl border border-white/5 overflow-hidden" style={{ background: "rgba(15,23,42,0.8)", backdropFilter: "blur(12px)" }}>
            <div className="px-6 py-5 border-b border-white/5">
              <h2 className="text-base font-semibold text-white">Select a Dataset</h2>
              <p className="text-slate-500 text-xs mt-1">Choose a ready dataset to train models on</p>
            </div>
            <div className="p-6">
              {loadingDatasets ? (
                <LoadingSpinner size="md" text="Loading datasets..." />
              ) : datasets.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-14 h-14 rounded-2xl bg-slate-800/50 flex items-center justify-center mx-auto mb-3">
                    <Database size={24} className="text-slate-600" />
                  </div>
                  <p className="text-slate-500 text-sm">No ready datasets found.</p>
                  <p className="text-slate-600 text-xs mt-1">Upload a dataset first to get started.</p>
                </div>
              ) : (
                <div className="grid sm:grid-cols-2 gap-3">
                  {datasets.map((ds) => (
                    <button
                      key={ds.id}
                      onClick={() => handleSelectDataset(ds)}
                      className={`text-left p-4 rounded-xl border transition-all group ${
                        selectedDataset?.id === ds.id
                          ? "border-indigo-500/60 bg-indigo-500/10 shadow-lg shadow-indigo-500/10"
                          : "border-white/5 bg-white/2 hover:border-indigo-500/30 hover:bg-indigo-500/5"
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 ${
                          selectedDataset?.id === ds.id ? "bg-indigo-500/20" : "bg-slate-800 group-hover:bg-indigo-500/10"
                        }`}>
                          <Database size={15} className={selectedDataset?.id === ds.id ? "text-indigo-400" : "text-slate-500"} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-semibold text-slate-200 text-sm truncate">{ds.name}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-slate-500 text-xs">{ds.row_count?.toLocaleString()} rows</span>
                            <span className="text-slate-700">Â·</span>
                            <span className="text-slate-500 text-xs">{ds.column_count} columns</span>
                          </div>
                        </div>
                        {selectedDataset?.id === ds.id && (
                          <CheckCircle2 size={16} className="text-indigo-400 flex-shrink-0 mt-1" />
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {selectedDataset && columns.length > 0 && (
                <div className="mt-6 pt-6 border-t border-white/5">
                  <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">
                    Target Column â€” what you want to predict
                  </label>
                  <select
                    value={targetColumn}
                    onChange={(e) => setTargetColumn(e.target.value)}
                    className="w-full bg-slate-900/80 border border-white/10 text-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/30 transition-all"
                  >
                    <option value="">Select a column...</option>
                    {columns.map((col) => (
                      <option key={col} value={col}>{col}</option>
                    ))}
                  </select>

                  <button
                    disabled={!targetColumn}
                    onClick={() => setStep("preprocess")}
                    className="mt-4 flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold text-white transition-all disabled:opacity-30 disabled:cursor-not-allowed shadow-lg shadow-indigo-500/20"
                    style={{ background: "linear-gradient(135deg, #6366f1, #8b5cf6)" }}
                  >
                    Continue <ChevronRight size={16} />
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* â”€â”€ STEP 2: Preprocessing â”€â”€ */}
        {step === "preprocess" && (
          <div className="space-y-4">
            {/* Dataset preview */}
            <div className="rounded-2xl border border-white/5 overflow-hidden" style={{ background: "rgba(15,23,42,0.8)" }}>
              <div className="px-5 py-3.5 border-b border-white/5 flex items-center gap-2">
                <Eye size={14} className="text-indigo-400" />
                <span className="text-sm font-medium text-slate-300">Dataset Preview â€” {selectedDataset?.name}</span>
              </div>
              <RawDataTable rows={datasetDetail?.preview_data ?? []} />
            </div>

            {/* Quality report */}
            <div className="rounded-2xl border border-white/5 p-6" style={{ background: "rgba(15,23,42,0.8)" }}>
              <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                <Gauge size={14} className="text-violet-400" />
                Data Quality Report
              </h3>
              {loadingQuality ? (
                <LoadingSpinner size="sm" text="Analyzing dataset..." />
              ) : qualityReport ? (
                <div className="space-y-5">
                  <div className="flex items-center gap-5">
                    <div className={`w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-black border-2 ${gradeColor(qualityReport.quality_grade)}`}>
                      {qualityReport.quality_grade?.charAt(0) ?? "-"}
                    </div>
                    <div>
                      <p className="text-3xl font-black text-white">{qualityReport.quality_score}<span className="text-slate-600 text-base font-normal"> / 100</span></p>
                      <p className="text-slate-500 text-xs mt-0.5">{qualityReport.quality_grade} â€” Overall quality score</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { label: "Missing Cells", value: `${qualityReport.missing_values?.total_missing ?? 0}`, sub: `${qualityReport.missing_values?.missing_percentage ?? 0}%`, color: "text-red-400" },
                      { label: "Duplicate Rows", value: `${qualityReport.duplicates?.total_duplicates ?? 0}`, sub: `${qualityReport.duplicates?.duplicate_percentage ?? 0}%`, color: "text-amber-400" },
                      { label: "Outlier Columns", value: `${qualityReport.outliers ? Object.keys(qualityReport.outliers).length : 0}`, sub: "columns", color: "text-orange-400" },
                    ].map((stat) => (
                      <div key={stat.label} className="bg-slate-900/60 rounded-xl p-3 border border-white/5">
                        <p className="text-slate-500 text-[10px] uppercase tracking-wider mb-1">{stat.label}</p>
                        <p className={`text-lg font-bold ${stat.color}`}>{stat.value}</p>
                        <p className="text-slate-600 text-xs">{stat.sub}</p>
                      </div>
                    ))}
                  </div>

                  {missingChartData.length > 0 && (
                    <div>
                      <p className="text-xs text-slate-500 mb-3 uppercase tracking-wider">Missing values by column</p>
                      <ResponsiveContainer width="100%" height={Math.max(100, missingChartData.length * 30)}>
                        <BarChart data={missingChartData} layout="vertical" margin={{ left: 0, right: 20 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                          <XAxis type="number" stroke="#334155" fontSize={10} allowDecimals={false} />
                          <YAxis type="category" dataKey="name" stroke="#334155" fontSize={10} width={100} />
                          <Tooltip {...tooltipStyle} />
                          <Bar dataKey="missing" radius={[0, 6, 6, 0]} fill="#ef4444" opacity={0.8} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  )}

                  {qualityReport.recommendations?.length > 0 && (
                    <div className="pt-4 border-t border-white/5 space-y-2">
                      {qualityReport.recommendations.map((rec: string, i: number) => (
                        <p key={i} className="text-xs text-slate-400 flex items-start gap-2">
                          <span className="text-amber-500 mt-0.5 flex-shrink-0">âš¡</span> {rec}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-slate-600 text-sm">No quality report available.</p>
              )}
            </div>

            {/* Run preprocessing */}
            <div className="rounded-2xl border border-white/5 p-6" style={{ background: "rgba(15,23,42,0.8)" }}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-base font-semibold text-white">Data Preprocessing</h2>
                  <p className="text-slate-500 text-xs mt-1">
                    Cleaning <span className="text-indigo-400 font-medium">{selectedDataset?.name}</span> â€” removing duplicates, handling missing values, encoding & scaling
                  </p>
                </div>
                <div className="flex-shrink-0 flex items-center gap-2">
                  <span className="text-xs bg-slate-800 text-slate-400 px-3 py-1 rounded-lg border border-white/5">Target: <span className="text-indigo-300">{targetColumn}</span></span>
                  <span className="text-xs bg-slate-800 text-slate-400 px-3 py-1 rounded-lg border border-white/5">Auto</span>
                </div>
              </div>
              <button
                onClick={handleStartPreprocessing}
                disabled={preprocessing}
                className="mt-5 flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold text-white transition-all disabled:opacity-40 shadow-lg shadow-indigo-500/20"
                style={{ background: preprocessing ? "#334155" : "linear-gradient(135deg, #6366f1, #8b5cf6)" }}
              >
                {preprocessing ? <Loader2 size={15} className="animate-spin" /> : <Zap size={15} />}
                {preprocessing ? "Processing..." : "Run Preprocessing"}
              </button>
            </div>
          </div>
        )}

        {/* â”€â”€ STEP 3: Feature Engineering â”€â”€ */}
        {step === "feature" && (
          <div className="rounded-2xl border border-white/5 p-6" style={{ background: "rgba(15,23,42,0.8)" }}>
            <div className="flex items-start gap-4 mb-6">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: "linear-gradient(135deg, #7c3aed22, #6366f122)" }}>
                <Sparkles size={18} className="text-violet-400" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-white">Feature Engineering</h2>
                <p className="text-slate-500 text-xs mt-1">Preparing features for optimal model training</p>
              </div>
            </div>

            <div className="flex items-center gap-3 bg-emerald-500/8 border border-emerald-500/20 rounded-xl px-4 py-3 mb-6">
              <CheckCircle2 size={15} className="text-emerald-400 flex-shrink-0" />
              <p className="text-sm text-emerald-300">
                Preprocessing complete â€” detected problem type: <strong className="text-emerald-200 capitalize">{problemType}</strong>
              </p>
            </div>

            <button
              onClick={handleRunFeatureEngineering}
              disabled={engineering}
              className="flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold text-white transition-all disabled:opacity-40 shadow-lg shadow-indigo-500/20"
              style={{ background: engineering ? "#334155" : "linear-gradient(135deg, #6366f1, #8b5cf6)" }}
            >
              {engineering ? <Loader2 size={15} className="animate-spin" /> : <Sparkles size={15} />}
              {engineering ? "Engineering Features..." : "Run Feature Engineering"}
            </button>
          </div>
        )}

        {/* â”€â”€ STEP 4: Train â”€â”€ */}
        {step === "train" && (
          <div className="space-y-4">
            {/* Dataset preview */}
            <div className="rounded-2xl border border-white/5 overflow-hidden" style={{ background: "rgba(15,23,42,0.8)" }}>
              <div className="px-5 py-3.5 border-b border-white/5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle2 size={14} className="text-emerald-400" />
                  <span className="text-sm font-medium text-slate-300">Dataset Ready for Training</span>
                </div>
                {engineeredPreview && (
                  <div className="flex items-center gap-3 text-xs">
                    <span className="text-slate-500">{engineeredPreview.shape?.rows?.toLocaleString()} rows Â· {engineeredPreview.shape?.columns} cols</span>
                    <span className="text-emerald-400/80 bg-emerald-500/10 px-2 py-0.5 rounded-lg">0 missing</span>
                    <span className="text-emerald-400/80 bg-emerald-500/10 px-2 py-0.5 rounded-lg">all numeric</span>
                  </div>
                )}
              </div>
              {loadingEngineeredPreview ? (
                <div className="p-6"><LoadingSpinner size="sm" text="Loading dataset..." /></div>
              ) : (
                <RawDataTable rows={engineeredPreview?.sample_data ?? []} />
              )}
            </div>

            {/* Train card */}
            <div className="rounded-2xl border border-white/5 p-6" style={{ background: "rgba(15,23,42,0.8)" }}>
              <div className="flex items-start gap-4 mb-6">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: "linear-gradient(135deg, #6366f122, #8b5cf622)" }}>
                  <Cpu size={18} className="text-indigo-400" />
                </div>
                <div>
                  <h2 className="text-base font-semibold text-white">Train Models</h2>
                  <p className="text-slate-500 text-xs mt-1">Multiple algorithms trained simultaneously â€” best model selected automatically</p>
                </div>
              </div>

              <div className="flex items-center gap-3 bg-emerald-500/8 border border-emerald-500/20 rounded-xl px-4 py-3 mb-6">
                <CheckCircle2 size={15} className="text-emerald-400 flex-shrink-0" />
                <p className="text-sm text-emerald-300">Feature engineering complete â€” ready to train</p>
              </div>

              {training ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span className="flex items-center gap-1.5"><Loader2 size={11} className="animate-spin" /> {trainingStatus || "Training models..."}</span>
                    <span className="font-mono">{trainingProgress}%</span>
                  </div>
                  <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full rounded-full transition-all duration-500" style={{ width: `${trainingProgress || 30}%`, background: "linear-gradient(90deg, #6366f1, #8b5cf6, #a78bfa)" }} />
                  </div>
                  <p className="text-slate-600 text-xs">This may take a minute depending on dataset size...</p>
                </div>
              ) : (
                <button
                  onClick={handleStartTraining}
                  className="flex items-center gap-2 px-8 py-3.5 rounded-xl text-sm font-bold text-white transition-all shadow-xl shadow-indigo-500/30 hover:shadow-indigo-500/50 hover:scale-[1.02] active:scale-[0.98]"
                  style={{ background: "linear-gradient(135deg, #6366f1, #8b5cf6)" }}
                >
                  <Play size={16} />
                  Start Training
                </button>
              )}
            </div>
          </div>
        )}

        {/* â”€â”€ STEP 5: Results â”€â”€ */}
        {step === "results" && (
          <div className="space-y-5">
            {loadingReport ? (
              <LoadingSpinner size="lg" text="Loading results..." />
            ) : report ? (
              <>
                {/* â”€â”€ Best Model Hero â”€â”€ */}
                <div className="rounded-2xl overflow-hidden relative" style={{ background: "linear-gradient(135deg, #1e1b4b 0%, #1a1035 50%, #0f0a2e 100%)" }}>
                  <div className="absolute inset-0" style={{ backgroundImage: "radial-gradient(circle at 20% 50%, #6366f125, transparent 55%), radial-gradient(circle at 80% 30%, #8b5cf620, transparent 55%)" }} />
                  <div className="relative px-6 py-7">
                    <div className="flex items-center gap-5">
                      <div className="w-16 h-16 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-xl" style={{ background: "linear-gradient(135deg, #f59e0b, #d97706)" }}>
                        <Trophy size={28} className="text-white" />
                      </div>
                      <div className="flex-1">
                        <p className="text-[10px] text-indigo-300/50 uppercase tracking-widest mb-1">Best Performing Model</p>
                        <h2 className="text-2xl font-black text-white">{report.best_model}</h2>
                        <div className="flex items-center flex-wrap gap-3 mt-2">
                          <span className="text-emerald-400 font-bold text-lg">{(report.best_score * 100)?.toFixed(2)}%</span>
                          <span className="text-xs bg-indigo-500/20 text-indigo-300 px-2.5 py-1 rounded-lg border border-indigo-500/20 capitalize">{report.problem_type}</span>
                          <span className="text-xs text-slate-500">Target: <span className="text-slate-300">{report.target_column}</span></span>
                          <span className="text-xs text-slate-500">{report.train_samples?.toLocaleString()} train Â· {report.test_samples?.toLocaleString()} test</span>
                        </div>
                      </div>
                    </div>

                    {/* Quick stats row */}
                    <div className="grid grid-cols-4 gap-3 mt-6">
                      {[
                        { label: "Models Trained", value: report.models_trained ?? report.leaderboard?.length ?? 0, color: "text-indigo-400" },
                        { label: "Best Score", value: `${(report.best_score * 100)?.toFixed(1)}%`, color: "text-emerald-400" },
                        { label: "Dataset Rows", value: report.dataset_shape?.[0]?.toLocaleString() ?? "-", color: "text-sky-400" },
                        { label: "Features Used", value: report.feature_count ?? "-", color: "text-violet-400" },
                      ].map((s) => (
                        <div key={s.label} className="bg-white/5 rounded-xl p-3 border border-white/8 text-center">
                          <p className={`text-lg font-black mb-0.5 ${s.color}`}>{s.value}</p>
                          <p className="text-slate-500 text-[10px]">{s.label}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* â”€â”€ Charts Grid â”€â”€ */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

                  {/* Accuracy Bar Chart */}
                  {leaderboardChartData.length > 0 && (
                    <div className="rounded-2xl border border-white/5 p-5" style={{ background: "rgba(15,23,42,0.9)" }}>
                      <h3 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
                        <BarChart2 size={14} className="text-indigo-400" />
                        Model Accuracy Comparison
                      </h3>
                      <p className="text-slate-600 text-xs mb-4">All models ranked by {report.problem_type === "regression" ? "RÂ² score" : "accuracy"}</p>
                      <ResponsiveContainer width="100%" height={Math.max(180, leaderboardChartData.length * 38)}>
                        <BarChart data={leaderboardChartData} layout="vertical" margin={{ left: 0, right: 50, top: 4, bottom: 4 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                          <XAxis type="number" stroke="#334155" fontSize={10} domain={[0, 1]} tickFormatter={(v) => `${(v*100).toFixed(0)}%`} />
                          <YAxis type="category" dataKey="name" stroke="#334155" fontSize={10} width={120} />
                          <Tooltip {...tooltipStyle} formatter={(v: number) => [`${(v*100).toFixed(2)}%`, "Score"]} />
                          <Bar dataKey="score" radius={[0, 6, 6, 0]}>
                            {leaderboardChartData.map((_: any, idx: number) => (
                              <Cell key={idx}
                                fill={idx === 0 ? "#6366f1" : idx === 1 ? "#8b5cf6" : idx === 2 ? "#a78bfa" : "#c4b5fd"}
                                opacity={idx === 0 ? 1 : 0.65}
                              />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  )}

                  {/* Radar Chart â€” multi-metric for classification */}
                  {report.problem_type === "classification" && report.leaderboard?.length > 0 && (() => {
                    const top3 = report.leaderboard.slice(0, 3);
                    const radarData = ["accuracy", "f1_score", "precision", "recall"].map((metric) => ({
                      metric: metric.replace(/_/g, " ").replace(/\b\w/g, (l: string) => l.toUpperCase()),
                      ...Object.fromEntries(top3.map((m: any) => [m.model_name, m.metrics?.[metric] ?? 0])),
                    }));
                    const radarColors = ["#6366f1", "#10b981", "#f59e0b"];
                    return (
                      <div className="rounded-2xl border border-white/5 p-5" style={{ background: "rgba(15,23,42,0.9)" }}>
                        <h3 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
                          <Target size={14} className="text-violet-400" />
                          Top 3 Models - Multi-Metric Radar
                        </h3>
                        <p className="text-slate-600 text-xs mb-2">Accuracy, F1, Precision and Recall comparison</p>
                        <ResponsiveContainer width="100%" height={240}>
                          <RadarChart data={radarData}>
                            <PolarGrid stroke="#1e293b" />
                            <PolarAngleAxis dataKey="metric" tick={{ fill: "#64748b", fontSize: 10 }} />
                            <PolarRadiusAxis angle={90} domain={[0, 1]} tick={{ fill: "#475569", fontSize: 9 }} />
                            {top3.map((m: any, i: number) => (
                              <Radar key={m.model_name} name={m.model_name} dataKey={m.model_name}
                                stroke={radarColors[i]} fill={radarColors[i]} fillOpacity={0.1} strokeWidth={2} />
                            ))}
                            <Legend iconSize={8} iconType="circle" wrapperStyle={{ fontSize: 10, color: "#94a3b8" }} />
                            <Tooltip {...tooltipStyle} formatter={(v: number) => v.toFixed(4)} />
                          </RadarChart>
                        </ResponsiveContainer>
                      </div>
                    );
                  })()}

                  {/* Regression metrics chart */}
                  {report.problem_type === "regression" && report.leaderboard?.length > 0 && (() => {
                    const rmseData = report.leaderboard.map((m: any) => ({
                      name: m.model_name,
                      RMSE: m.metrics?.rmse ?? 0,
                      MAE: m.metrics?.mae ?? 0,
                    }));
                    return (
                      <div className="rounded-2xl border border-white/5 p-5" style={{ background: "rgba(15,23,42,0.9)" }}>
                        <h3 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
                          <TrendingUp size={14} className="text-violet-400" />
                          Error Comparison (Lower is Better)
                        </h3>
                        <p className="text-slate-600 text-xs mb-4">RMSE and MAE across all models</p>
                        <ResponsiveContainer width="100%" height={200}>
                          <BarChart data={rmseData} margin={{ left: 0, right: 10, top: 4, bottom: 4 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                            <XAxis dataKey="name" stroke="#334155" fontSize={9} tick={{ fill: "#64748b" }} />
                            <YAxis stroke="#334155" fontSize={10} />
                            <Tooltip {...tooltipStyle} />
                            <Legend iconSize={8} wrapperStyle={{ fontSize: 10, color: "#94a3b8" }} />
                            <Bar dataKey="RMSE" fill="#6366f1" radius={[4, 4, 0, 0]} opacity={0.85} />
                            <Bar dataKey="MAE" fill="#10b981" radius={[4, 4, 0, 0]} opacity={0.85} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    );
                  })()}

                  {/* Score progress bar visual */}
                  <div className="rounded-2xl border border-white/5 p-5" style={{ background: "rgba(15,23,42,0.9)" }}>
                    <h3 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
                      <Gauge size={14} className="text-sky-400" />
                      Score Distribution
                    </h3>
                    <p className="text-slate-600 text-xs mb-4">Visual ranking of all trained models</p>
                    <div className="space-y-3">
                      {report.leaderboard?.map((entry: any, i: number) => {
                        const score = entry.metrics?.accuracy ?? entry.metrics?.r2_score ?? 0;
                        const medals = ["1st", "2nd", "3rd"];
                        const barColors = ["#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd", "#7c3aed", "#4f46e5", "#818cf8"];
                        return (
                          <div key={i} className="space-y-1">
                            <div className="flex items-center justify-between text-xs">
                              <span className="text-slate-300 flex items-center gap-1.5">
                                <span>{medals[i] ?? `#${i+1}`}</span>
                                <span className="font-medium">{entry.display_name ?? entry.model_name}</span>
                              </span>
                              <span className="text-indigo-300 font-bold font-mono">{(score * 100).toFixed(2)}%</span>
                            </div>
                            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                              <div
                                className="h-full rounded-full transition-all duration-700"
                                style={{ width: `${score * 100}%`, background: barColors[i] ?? "#6366f1", opacity: i === 0 ? 1 : 0.6 }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>

                {/* â”€â”€ Leaderboard Table â”€â”€ */}
                <div className="rounded-2xl border border-white/5 overflow-hidden" style={{ background: "rgba(15,23,42,0.9)" }}>
                  <div className="px-5 py-4 border-b border-white/5 flex items-center gap-2">
                    <Trophy size={14} className="text-indigo-400" />
                    <h3 className="text-sm font-semibold text-white">Model Leaderboard</h3>
                    <span className="ml-auto text-xs text-slate-600 bg-slate-800 px-2.5 py-1 rounded-lg">{report.leaderboard?.length} models</span>
                  </div>
                  <div className="divide-y divide-white/5">
                    {report.leaderboard?.map((entry: any, i: number) => {
                      const isOpen = expandedModel === entry.model_name;
                      const score = entry.metrics?.accuracy ?? entry.metrics?.r2_score ?? 0;
                      const medals = ["1st", "2nd", "3rd"];
                      return (
                        <div key={i} className={i === 0 ? "bg-indigo-500/5" : ""}>
                          <button
                            onClick={() => setExpandedModel(isOpen ? null : entry.model_name)}
                            className="w-full flex items-center gap-4 px-5 py-4 text-left hover:bg-white/3 transition-colors"
                          >
                            <span className="text-xl w-8 flex-shrink-0">{medals[i] ?? <span className="text-xs text-slate-600 font-mono">#{i+1}</span>}</span>
                            <div className="flex-1 min-w-0">
                              <p className="text-slate-200 font-semibold text-sm">{entry.display_name ?? entry.model_name}</p>
                              <p className="text-slate-600 text-xs">{entry.category}</p>
                            </div>
                            {/* Mini bar */}
                            <div className="hidden sm:flex items-center gap-2 w-32">
                              <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                <div className="h-full rounded-full" style={{ width: `${score * 100}%`, background: i === 0 ? "#6366f1" : "#475569" }} />
                              </div>
                            </div>
                            <div className="flex items-center gap-3 flex-shrink-0">
                              <div className="text-right">
                                <p className="text-indigo-300 font-bold">{(score * 100).toFixed(1)}%</p>
                                <p className="text-slate-600 text-[10px]">{report.problem_type === "regression" ? "RÂ²" : "Accuracy"}</p>
                              </div>
                              <ChevronDown size={14} className={`text-slate-600 transition-transform ${isOpen ? "rotate-180" : ""}`} />
                            </div>
                          </button>

                          {isOpen && (
                            <div className="px-5 pb-5">
                              <div className="bg-slate-900/60 rounded-xl p-4 space-y-4 border border-white/5">
                                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                                  {Object.entries(entry.metrics ?? {}).map(([key, val]: [string, any]) => {
                                    if (key === "confusion_matrix" || typeof val === "object") return null;
                                    return (
                                      <div key={key} className="bg-slate-800/60 rounded-xl px-3 py-3 border border-white/5 text-center">
                                        <p className="text-[10px] text-slate-500 uppercase tracking-wider capitalize mb-1.5">{key.replace(/_/g, " ")}</p>
                                        <p className="text-base text-white font-black">{typeof val === "number" ? (val * 100).toFixed(1) + "%" : String(val)}</p>
                                      </div>
                                    );
                                  })}
                                </div>
                                <div className="flex flex-wrap gap-4 text-xs text-slate-500 pt-3 border-t border-white/5">
                                  <span className="flex items-center gap-1.5 bg-slate-800/50 px-3 py-1.5 rounded-lg">
                                    <Clock size={11} /> {entry.training_time_seconds}s training time
                                  </span>
                                  <span className="flex items-center gap-1.5 bg-slate-800/50 px-3 py-1.5 rounded-lg">
                                    <Target size={11} /> CV {entry.cv_mean?.toFixed(3)} Â±{entry.cv_std?.toFixed(3)}
                                  </span>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* â”€â”€ Preprocessing Pipeline â”€â”€ */}
                {report.preprocessing_report && (
                  <div className="rounded-2xl border border-white/5 p-5" style={{ background: "rgba(15,23,42,0.9)" }}>
                    <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                      <Layers size={14} className="text-sky-400" />
                      Preprocessing Pipeline
                      <span className="ml-auto text-xs text-slate-600">{report.preprocessing_report.original_shape?.join("Ã—")} â†’ {report.preprocessing_report.final_shape?.join("Ã—")}</span>
                    </h3>
                    <div className="flex items-center gap-2 overflow-x-auto pb-2">
                      {report.preprocessing_report.steps?.map((s: any, i: number) => (
                        <div key={i} className="flex items-center gap-2 flex-shrink-0">
                          <div className="bg-slate-900/60 rounded-xl px-4 py-3 border border-white/5 text-center min-w-[110px]">
                            <span className="w-5 h-5 rounded-full bg-indigo-500/20 flex items-center justify-center text-[10px] text-indigo-400 font-bold mx-auto mb-1.5">{i+1}</span>
                            <p className="text-xs font-medium text-slate-300 capitalize">{s.step?.replace(/_/g, " ")}</p>
                            <p className="text-[10px] text-slate-600 mt-0.5">{s.shape_after?.[1]} cols</p>
                          </div>
                          {i < (report.preprocessing_report.steps?.length - 1) && (
                            <ChevronRight size={14} className="text-slate-700 flex-shrink-0" />
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Failed models */}
                {report.failed_models?.length > 0 && (
                  <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-4">
                    <p className="text-sm text-red-300 flex items-center gap-2 mb-2">
                      <AlertTriangle size={14} /> {report.failed_models.length} model(s) failed to train
                    </p>
                    {report.failed_models.map((f: any, i: number) => (
                      <p key={i} className="text-xs text-slate-500">{f.display_name ?? f.model_name}: {f.error}</p>
                    ))}
                  </div>
                )}

                {/* Downloads */}
                <div className="rounded-2xl border border-white/5 p-5 flex flex-wrap items-center gap-3" style={{ background: "rgba(15,23,42,0.9)" }}>
                  <span className="text-xs text-slate-500 uppercase tracking-wider mr-1">Download:</span>
                  <button
                    onClick={handleDownloadModel}
                    disabled={downloadingModel}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold text-indigo-300 border border-indigo-500/30 bg-indigo-500/10 hover:bg-indigo-500/20 transition-all disabled:opacity-50"
                  >
                    {downloadingModel ? <Loader2 size={13} className="animate-spin" /> : <Download size={13} />}
                    Trained Model (.pkl)
                  </button>
                  <button
                    onClick={handleDownloadDataset}
                    disabled={downloadingDataset}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold text-violet-300 border border-violet-500/30 bg-violet-500/10 hover:bg-violet-500/20 transition-all disabled:opacity-50"
                  >
                    {downloadingDataset ? <Loader2 size={13} className="animate-spin" /> : <Download size={13} />}
                    Feature-Engineered Dataset (.csv)
                  </button>
                </div>

 {/* Actions */}
                <div className="flex items-center gap-3 pt-2">
                  <button
                    onClick={resetWizard}
                    className="px-5 py-2.5 rounded-xl text-sm font-medium text-slate-300 border border-white/10 bg-white/5 hover:bg-white/8 transition-all"
                  >
                    Train Another Model
                  </button>
                  <Link
                    href="/intelligence"
                    className="flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-bold text-white shadow-lg shadow-indigo-500/20 transition-all hover:shadow-indigo-500/40 hover:scale-[1.02]"
                    style={{ background: "linear-gradient(135deg, #6366f1, #8b5cf6)" }}
                  >
                    AI Intelligence <ArrowRight size={15} />
                  </Link>
                </div>
              </>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
}
