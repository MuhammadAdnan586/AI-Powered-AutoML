"use client";
import { useState } from "react";
import type { DatasetVersion } from "@/types";
import { formatBytes, formatDateTime } from "@/utils";
import { GitBranch, Upload, Download, CheckCircle2, Clock, Loader2 } from "lucide-react";
import { datasetService } from "@/services/dataset.service";
import toast from "react-hot-toast";

interface VersionHistoryProps {
  datasetId: number;
  versions: DatasetVersion[];
  onNewVersion: () => void;
}

export default function VersionHistory({
  datasetId,
  versions,
  onNewVersion,
}: VersionHistoryProps) {
  const [uploading, setUploading] = useState(false);

  const handleUploadVersion = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      await datasetService.createVersion(
        datasetId,
        file,
        `Version ${versions.length + 1}`,
        "Manually uploaded new version"
      );
      toast.success(`Version ${versions.length + 1} uploaded!`);
      onNewVersion();
    } catch {
      toast.error("Failed to upload new version");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleDownload = (version: DatasetVersion) => {
    const url = datasetService.getDownloadUrl(datasetId, version.version_number);
    const token = localStorage.getItem("access_token");
    // Trigger download with auth header via fetch
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.blob())
      .then((blob) => {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `dataset_v${version.version_number}.${version.version_label || "csv"}`;
        a.click();
      })
      .catch(() => toast.error("Download failed"));
  };

  const sorted = [...versions].sort((a, b) => b.version_number - a.version_number);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-5">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <GitBranch size={16} className="text-sky-400" />
          Version History
        </h3>

        <label className="btn-secondary cursor-pointer text-xs px-3 py-2">
          {uploading ? (
            <>
              <Loader2 size={13} className="animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Upload size={13} />
              New Version
            </>
          )}
          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            className="hidden"
            onChange={handleUploadVersion}
            disabled={uploading}
          />
        </label>
      </div>

      <div className="space-y-3">
        {sorted.map((version) => (
          <div
            key={version.id}
            className={`flex items-center justify-between gap-4 p-4 rounded-xl border transition-all ${
              version.is_active
                ? "border-sky-500/30 bg-sky-500/5"
                : "border-slate-800 bg-slate-800/30"
            }`}
          >
            {/* Version badge + info */}
            <div className="flex items-center gap-3 min-w-0">
              <div
                className={`w-9 h-9 rounded-xl flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                  version.is_active
                    ? "bg-sky-500 text-white"
                    : "bg-slate-700 text-slate-300"
                }`}
              >
                v{version.version_number}
              </div>

              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <p className="font-medium text-white text-sm">
                    {version.version_label || `Version ${version.version_number}`}
                  </p>
                  {version.is_active && (
                    <span className="inline-flex items-center gap-1 text-xs text-sky-400 bg-sky-400/10 px-2 py-0.5 rounded-full border border-sky-400/20">
                      <CheckCircle2 size={10} />
                      Active
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-3 mt-0.5">
                  <span className="text-slate-500 text-xs flex items-center gap-1">
                    <Clock size={10} />
                    {formatDateTime(version.created_at)}
                  </span>
                  {version.row_count && (
                    <span className="text-slate-500 text-xs">
                      {version.row_count.toLocaleString()} rows
                    </span>
                  )}
                  {version.file_size_bytes && (
                    <span className="text-slate-500 text-xs">
                      {formatBytes(version.file_size_bytes)}
                    </span>
                  )}
                </div>
                {version.notes && (
                  <p className="text-slate-500 text-xs mt-1 italic">{version.notes}</p>
                )}
              </div>
            </div>

            {/* Actions */}
            <button
              onClick={() => handleDownload(version)}
              className="p-2 rounded-lg text-slate-400 hover:text-sky-400 hover:bg-sky-500/10 transition-all flex-shrink-0"
              title="Download this version"
            >
              <Download size={15} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
