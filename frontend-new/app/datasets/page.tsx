"use client";
import { useEffect, useState, useCallback } from "react";
import { datasetService } from "@/services/dataset.service";
import type { DatasetListItem } from "@/types";
import DatasetCard from "@/components/Dataset/DatasetCard";
import UploadModal from "@/components/Dataset/UploadModal";
import ConfirmModal from "@/components/UI/ConfirmModal";
import EmptyState from "@/components/UI/EmptyState";
import LoadingSpinner from "@/components/UI/LoadingSpinner";
import { getErrorMessage } from "@/utils";
import toast from "react-hot-toast";
import { Plus, Database, Search, LayoutGrid, List } from "lucide-react";
import Link from "next/link";

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<DatasetListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [search, setSearch] = useState("");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  const fetchDatasets = useCallback(async () => {
    try {
      const data = await datasetService.list(0, 50);
      setDatasets(data);
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDatasets();
  }, [fetchDatasets]);

  const handleDelete = async () => {
    if (deleteId === null) return;
    await datasetService.delete(deleteId);
    toast.success("Dataset deleted");
    setDatasets((prev) => prev.filter((d) => d.id !== deleteId));
    setDeleteId(null);
  };

  const filtered = datasets.filter(
    (d) =>
      d.name.toLowerCase().includes(search.toLowerCase()) ||
      d.original_filename.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" text="Loading datasets..." />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Datasets</h1>
          <p className="text-slate-400 text-sm mt-1">
            {datasets.length} dataset{datasets.length !== 1 ? "s" : ""} in your workspace
          </p>
        </div>
        <button
          onClick={() => setShowUpload(true)}
          className="btn-primary self-start sm:self-auto"
        >
          <Plus size={16} />
          Upload Dataset
        </button>
      </div>

      {/* Search + view toggle */}
      {datasets.length > 0 && (
        <div className="flex items-center gap-3">
          <div className="relative flex-1 max-w-md">
            <Search
              size={15}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
            />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search datasets..."
              className="input pl-9"
            />
          </div>
          <div className="flex items-center gap-1 bg-slate-800 border border-slate-700 rounded-xl p-1">
            <button
              onClick={() => setViewMode("grid")}
              className={`p-2 rounded-lg transition-all ${
                viewMode === "grid"
                  ? "bg-slate-700 text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <LayoutGrid size={15} />
            </button>
            <button
              onClick={() => setViewMode("list")}
              className={`p-2 rounded-lg transition-all ${
                viewMode === "list"
                  ? "bg-slate-700 text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <List size={15} />
            </button>
          </div>
        </div>
      )}

      {/* Content */}
      {datasets.length === 0 ? (
        <EmptyState
          icon={Database}
          title="No datasets yet"
          description="Upload your first CSV or Excel file to get started with AutoML."
          action={
            <button onClick={() => setShowUpload(true)} className="btn-primary">
              <Plus size={16} />
              Upload your first dataset
            </button>
          }
        />
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={Search}
          title="No results found"
          description={`No datasets match "${search}". Try a different search term.`}
        />
      ) : viewMode === "grid" ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map((dataset) => (
            <DatasetCard
              key={dataset.id}
              dataset={dataset}
              onDelete={(id) => setDeleteId(id)}
            />
          ))}
        </div>
      ) : (
        /* List view */
        <div className="card p-0 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-800/80 border-b border-slate-700">
                <th className="px-5 py-3 text-left text-xs font-semibold text-slate-400">Name</th>
                <th className="px-5 py-3 text-left text-xs font-semibold text-slate-400">Status</th>
                <th className="px-5 py-3 text-left text-xs font-semibold text-slate-400">Rows</th>
                <th className="px-5 py-3 text-left text-xs font-semibold text-slate-400">Cols</th>
                <th className="px-5 py-3 text-left text-xs font-semibold text-slate-400">Size</th>
                <th className="px-5 py-3 text-right text-xs font-semibold text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((ds) => (
                <tr
                  key={ds.id}
                  className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors"
                >
                  <td className="px-5 py-3">
                    <Link
                      href={`/datasets/${ds.id}`}
                      className="font-medium text-slate-200 hover:text-sky-400 transition-colors"
                    >
                      {ds.name}
                    </Link>
                    <p className="text-slate-500 text-xs mt-0.5">{ds.original_filename}</p>
                  </td>
                  <td className="px-5 py-3">
                    <span className={`badge ${ds.status === "ready" ? "text-green-400 bg-green-400/10 border-green-400/20" : ds.status === "error" ? "text-red-400 bg-red-400/10 border-red-400/20" : "text-yellow-400 bg-yellow-400/10 border-yellow-400/20"}`}>
                      {ds.status}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-slate-300">{ds.row_count?.toLocaleString() ?? "—"}</td>
                  <td className="px-5 py-3 text-slate-300">{ds.column_count ?? "—"}</td>
                  <td className="px-5 py-3 text-slate-300">{ds.file_size_bytes ? `${(ds.file_size_bytes / 1024).toFixed(1)} KB` : "—"}</td>
                  <td className="px-5 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Link
                        href={`/datasets/${ds.id}`}
                        className="text-xs text-sky-400 hover:text-sky-300 transition-colors"
                      >
                        View
                      </Link>
                      <button
                        onClick={() => setDeleteId(ds.id)}
                        className="text-xs text-red-400 hover:text-red-300 transition-colors"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modals */}
      <UploadModal
        isOpen={showUpload}
        onClose={() => setShowUpload(false)}
        onSuccess={fetchDatasets}
      />

      <ConfirmModal
        isOpen={deleteId !== null}
        onClose={() => setDeleteId(null)}
        onConfirm={handleDelete}
        title="Delete Dataset"
        message="This will permanently delete the dataset and all its versions. This action cannot be undone."
        confirmLabel="Delete Dataset"
      />
    </div>
  );
}
