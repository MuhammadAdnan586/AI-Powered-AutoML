"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { datasetService } from "@/services/dataset.service";
import type { Dataset } from "@/types";
import LoadingSpinner from "@/components/UI/LoadingSpinner";
import StatusBadge from "@/components/UI/StatusBadge";
import DataPreview from "@/components/Dataset/DataPreview";
import ColumnInfo from "@/components/Dataset/ColumnInfo";
import VersionHistory from "@/components/Dataset/VersionHistory";
import ConfirmModal from "@/components/UI/ConfirmModal";
import { formatBytes, formatDateTime, formatNumber, getFileIcon, getErrorMessage } from "@/utils";
import toast from "react-hot-toast";
import Link from "next/link";
import {
  ArrowLeft,
  Rows,
  Columns,
  HardDrive,
  Calendar,
  Download,
  Trash2,
  Edit2,
  Check,
  X,
} from "lucide-react";

export default function DatasetDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [loading, setLoading] = useState(true);
  const [showDelete, setShowDelete] = useState(false);

  // Inline edit state
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [editDesc, setEditDesc] = useState("");
  const [saving, setSaving] = useState(false);

  const fetchDataset = async () => {
    try {
      const data = await datasetService.getById(Number(id));
      setDataset(data);
      setEditName(data.name);
      setEditDesc(data.description || "");
    } catch {
      toast.error("Dataset not found");
      router.push("/datasets");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDataset();
  }, [id]);

  const handleSaveEdit = async () => {
    if (!dataset) return;
    setSaving(true);
    try {
      const updated = await datasetService.update(dataset.id, {
        name: editName,
        description: editDesc,
      });
      setDataset(updated);
      setEditing(false);
      toast.success("Dataset updated");
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!dataset) return;
    await datasetService.delete(dataset.id);
    toast.success("Dataset deleted");
    router.push("/datasets");
  };

  const handleDownload = () => {
    if (!dataset) return;
    const url = datasetService.getDownloadUrl(dataset.id);
    const token = localStorage.getItem("access_token");
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.blob())
      .then((blob) => {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = dataset.original_filename;
        a.click();
      })
      .catch(() => toast.error("Download failed"));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" text="Loading dataset..." />
      </div>
    );
  }

  if (!dataset) return null;

  return (
    <div className="space-y-6 max-w-7xl animate-fade-in">
      {/* Breadcrumb + Back */}
      <div className="flex items-center gap-2 text-sm text-slate-400">
        <Link href="/datasets" className="hover:text-sky-400 transition-colors flex items-center gap-1">
          <ArrowLeft size={14} />
          Datasets
        </Link>
        <span>/</span>
        <span className="text-slate-200 truncate">{dataset.name}</span>
      </div>

      {/* Header card */}
      <div className="card">
        <div className="flex flex-col sm:flex-row sm:items-start gap-4">
          {/* Icon + info */}
          <div className="flex items-start gap-4 flex-1 min-w-0">
            <div className="w-14 h-14 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center text-3xl flex-shrink-0">
              {getFileIcon(dataset.file_extension)}
            </div>
            <div className="min-w-0 flex-1">
              {editing ? (
                <div className="space-y-2">
                  <input
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    className="input text-lg font-bold"
                    placeholder="Dataset name"
                  />
                  <textarea
                    value={editDesc}
                    onChange={(e) => setEditDesc(e.target.value)}
                    rows={2}
                    className="input text-sm resize-none"
                    placeholder="Description (optional)"
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={handleSaveEdit}
                      disabled={saving}
                      className="btn-primary text-xs px-3 py-1.5"
                    >
                      <Check size={13} />
                      Save
                    </button>
                    <button
                      onClick={() => setEditing(false)}
                      className="btn-secondary text-xs px-3 py-1.5"
                    >
                      <X size={13} />
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <h1 className="text-xl font-bold text-white leading-tight">{dataset.name}</h1>
                  <p className="text-slate-400 text-sm mt-0.5">{dataset.original_filename}</p>
                  {dataset.description && (
                    <p className="text-slate-400 text-sm mt-2">{dataset.description}</p>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Action buttons */}
          {!editing && (
            <div className="flex items-center gap-2 flex-shrink-0">
              <StatusBadge status={dataset.status} />
              <button
                onClick={() => setEditing(true)}
                className="btn-ghost p-2"
                title="Edit"
              >
                <Edit2 size={15} />
              </button>
              <button
                onClick={handleDownload}
                className="btn-secondary text-xs px-3 py-2"
              >
                <Download size={14} />
                Download
              </button>
              <button
                onClick={() => setShowDelete(true)}
                className="btn-danger text-xs px-3 py-2"
              >
                <Trash2 size={14} />
                Delete
              </button>
            </div>
          )}
        </div>

        {/* Meta stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-5 border-t border-slate-800">
          {[
            { icon: Rows, label: "Rows", value: formatNumber(dataset.row_count) },
            { icon: Columns, label: "Columns", value: dataset.column_count ?? "—" },
            { icon: HardDrive, label: "File Size", value: formatBytes(dataset.file_size_bytes) },
            { icon: Calendar, label: "Uploaded", value: formatDateTime(dataset.created_at) },
          ].map(({ icon: Icon, label, value }) => (
            <div key={label} className="text-center">
              <Icon size={16} className="text-slate-500 mx-auto mb-1" />
              <p className="text-xs text-slate-500">{label}</p>
              <p className="text-sm font-semibold text-white mt-0.5">{value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Tabs content */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 space-y-6">
          <DataPreview dataset={dataset} />
          <ColumnInfo dataset={dataset} />
        </div>
        <div>
          <VersionHistory
            datasetId={dataset.id}
            versions={dataset.versions || []}
            onNewVersion={fetchDataset}
          />
        </div>
      </div>

      {/* Delete modal */}
      <ConfirmModal
        isOpen={showDelete}
        onClose={() => setShowDelete(false)}
        onConfirm={handleDelete}
        title="Delete Dataset"
        message={`Are you sure you want to delete "${dataset.name}"? All versions will be permanently deleted.`}
        confirmLabel="Delete Dataset"
      />
    </div>
  );
}
