
"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { datasetService } from "@/services/dataset.service";
import type { Dataset, DatasetVersion } from "@/types";
import LoadingSpinner from "@/components/UI/LoadingSpinner";
import { getErrorMessage } from "@/utils";
import toast from "react-hot-toast";
import { ArrowLeft, Calendar, HardDrive, Rows, Columns, Eye, Download, Clock, CheckCircle, AlertCircle, GitBranch } from "lucide-react";
import Link from "next/link";

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { color: string; icon: React.ReactNode }> = {
    ready:      { color: "text-green-400 bg-green-400/10 border-green-400/20",    icon: <CheckCircle size={12} /> },
    error:      { color: "text-red-400 bg-red-400/10 border-red-400/20",          icon: <AlertCircle size={12} /> },
    processing: { color: "text-yellow-400 bg-yellow-400/10 border-yellow-400/20", icon: <Clock size={12} /> },
    uploading:  { color: "text-blue-400 bg-blue-400/10 border-blue-400/20",       icon: <Clock size={12} /> },
  };
  const s = map[status] ?? map.processing;
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${s.color}`}>
      {s.icon}{status}
    </span>
  );
}

function InfoCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 flex items-center gap-3">
      <div className="text-sky-400">{icon}</div>
      <div>
        <p className="text-xs text-slate-500">{label}</p>
        <p className="text-sm font-semibold text-slate-200">{value}</p>
      </div>
    </div>
  );
}

export default function DatasetDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [versions, setVersions] = useState<DatasetVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "preview" | "versions">("overview");

  useEffect(() => {
    const load = async () => {
      try {
        const [ds, vers] = await Promise.all([
          datasetService.getById(Number(id)),
          datasetService.getVersions(Number(id)),
        ]);
        setDataset(ds);
        setVersions(vers);
      } catch (err) {
        toast.error(getErrorMessage(err));
        router.push("/datasets");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id, router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" text="Loading dataset..." />
      </div>
    );
  }

  if (!dataset) return null;

  const fmt = (n?: number) => n?.toLocaleString() ?? "-";
  const fmtDate = (s: string) => new Date(s).toLocaleString();
  const fmtSize = (b?: number) => b ? `${(b / 1024).toFixed(1)} KB` : "-";

  return (
    <div className="space-y-6 max-w-6xl">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <Link href="/datasets" className="mt-1 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition-all">
            <ArrowLeft size={18} />
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-white">{dataset.name}</h1>
              <StatusBadge status={dataset.status} />
            </div>
            <p className="text-slate-400 text-sm mt-1">{dataset.original_filename}</p>
            {dataset.description && <p className="text-slate-500 text-sm mt-1">{dataset.description}</p>}
          </div>
        </div>
        <a href={datasetService.getDownloadUrl(dataset.id)} className="flex items-center gap-2 px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-sm font-medium rounded-xl transition-all">
          <Download size={15} /> Download
        </a>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <InfoCard icon={<Rows size={18} />}      label="Total Rows" value={fmt(dataset.row_count)} />
        <InfoCard icon={<Columns size={18} />}   label="Columns"    value={fmt(dataset.column_count)} />
        <InfoCard icon={<HardDrive size={18} />} label="File Size"  value={fmtSize(dataset.file_size_bytes)} />
        <InfoCard icon={<Calendar size={18} />}  label="Uploaded"   value={fmtDate(dataset.created_at)} />
      </div>

      <div className="flex gap-1 bg-slate-800/50 border border-slate-700/50 rounded-xl p-1 w-fit">
        {(["overview", "preview", "versions"] as const).map((tab) => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-all ${activeTab === tab ? "bg-sky-600 text-white" : "text-slate-400 hover:text-white"}`}>
            {tab === "versions" ? `Versions (${versions.length})` : tab}
          </button>
        ))}
      </div>

      {activeTab === "overview" && (
        <div className="grid md:grid-cols-2 gap-6">
          {dataset.column_names && dataset.column_names.length > 0 && (
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
              <h2 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                <Columns size={15} className="text-sky-400" /> Columns
              </h2>
              <div className="flex flex-wrap gap-2">
                {dataset.column_names.map((col) => (
                  <span key={col} className="px-2.5 py-1 bg-slate-700 text-slate-300 text-xs rounded-lg">
                    {col}{dataset.dtypes_info?.[col] && <span className="ml-1.5 text-slate-500">{dataset.dtypes_info[col]}</span>}
                  </span>
                ))}
              </div>
            </div>
          )}
          {dataset.missing_values_info && Object.keys(dataset.missing_values_info).length > 0 && (
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
              <h2 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                <AlertCircle size={15} className="text-yellow-400" /> Missing Values
              </h2>
              <div className="space-y-2">
                {Object.values(dataset.missing_values_info).every((v) => v === 0) ? (
                  <p className="text-green-400 text-sm flex items-center gap-2"><CheckCircle size={14} /> No missing values!</p>
                ) : (
                  Object.entries(dataset.missing_values_info).filter(([, v]) => v > 0).sort(([, a], [, b]) => b - a).map(([col, count]) => {
                    const pct = dataset.row_count ? Math.round((count / dataset.row_count) * 100) : 0;
                    return (
                      <div key={col} className="flex items-center gap-3">
                        <span className="text-xs text-slate-400 w-28 truncate">{col}</span>
                        <div className="flex-1 bg-slate-700 rounded-full h-1.5">
                          <div className="bg-yellow-400 h-1.5 rounded-full" style={{ width: `${pct}%` }} />
                        </div>
                        <span className="text-xs text-slate-400 w-16 text-right">{count} ({pct}%)</span>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === "preview" && (
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-slate-700/50 flex items-center gap-2">
            <Eye size={15} className="text-sky-400" />
            <span className="text-sm font-medium text-slate-300">Data Preview (first {dataset.preview_data?.length ?? 0} rows)</span>
          </div>
          {dataset.preview_data && dataset.preview_data.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-slate-900/50">
                    {Object.keys(dataset.preview_data[0]).map((col) => (
                      <th key={col} className="px-4 py-2.5 text-left text-slate-400 font-medium whitespace-nowrap border-b border-slate-700/50">{col}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {dataset.preview_data.map((row, i) => (
                    <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                      {Object.values(row).map((val, j) => (
                        <td key={j} className="px-4 py-2 text-slate-300 whitespace-nowrap max-w-[150px] truncate">
                          {val === null || val === undefined ? <span className="text-slate-600 italic">null</span> : String(val)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center text-slate-500">No preview data available</div>
          )}
        </div>
      )}

      {activeTab === "versions" && (
        <div className="space-y-3">
          {versions.length === 0 ? (
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-8 text-center text-slate-500">
              <GitBranch size={32} className="mx-auto mb-2 opacity-40" />
              No additional versions yet.
            </div>
          ) : versions.map((v) => (
            <div key={v.id} className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-sky-600/20 border border-sky-600/30 flex items-center justify-center text-sky-400 text-xs font-bold">
                  v{v.version_number}
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-200">
                    {v.version_label ?? `Version ${v.version_number}`}
                    {v.is_active && <span className="ml-2 text-xs text-green-400 bg-green-400/10 border border-green-400/20 px-1.5 py-0.5 rounded-full">active</span>}
                  </p>
                  <p className="text-xs text-slate-500">{fmt(v.row_count)} rows · {fmt(v.column_count)} cols · {fmtSize(v.file_size_bytes)} · {fmtDate(v.created_at)}</p>
                  {v.notes && <p className="text-xs text-slate-400 mt-0.5">{v.notes}</p>}
                </div>
              </div>
              <a href={datasetService.getDownloadUrl(dataset.id, v.version_number)} className="flex items-center gap-1.5 text-xs text-sky-400 hover:text-sky-300 transition-colors">
                <Download size={13} /> Download
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
