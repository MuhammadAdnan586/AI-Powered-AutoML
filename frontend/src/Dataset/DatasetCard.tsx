"use client";
import Link from "next/link";
import { formatBytes, formatDate, formatNumber, getFileIcon } from "@/utils";
import StatusBadge from "@/components/UI/StatusBadge";
import type { DatasetListItem } from "@/types";
import { Rows, Columns, HardDrive, Trash2, Eye, GitBranch } from "lucide-react";

interface DatasetCardProps {
  dataset: DatasetListItem;
  onDelete: (id: number) => void;
}

export default function DatasetCard({ dataset, onDelete }: DatasetCardProps) {
  return (
    <div className="card hover:border-slate-700 transition-all duration-200 group">
      {/* Header row */}
      <div className="flex items-start justify-between gap-3 mb-4">
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-xl flex-shrink-0">
            {getFileIcon(dataset.file_extension)}
          </div>
          <div className="min-w-0">
            <h3 className="font-semibold text-white truncate group-hover:text-sky-300 transition-colors">
              {dataset.name}
            </h3>
            <p className="text-slate-500 text-xs mt-0.5 truncate">{dataset.original_filename}</p>
          </div>
        </div>
        <StatusBadge status={dataset.status} />
      </div>

      {/* Description */}
      {dataset.description && (
        <p className="text-slate-400 text-sm mb-4 line-clamp-2">{dataset.description}</p>
      )}

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-slate-800/60 rounded-lg px-3 py-2 text-center">
          <div className="flex items-center justify-center gap-1 text-slate-400 mb-0.5">
            <Rows size={11} />
            <span className="text-xs">Rows</span>
          </div>
          <p className="text-sm font-semibold text-white">
            {dataset.row_count ? formatNumber(dataset.row_count) : "—"}
          </p>
        </div>
        <div className="bg-slate-800/60 rounded-lg px-3 py-2 text-center">
          <div className="flex items-center justify-center gap-1 text-slate-400 mb-0.5">
            <Columns size={11} />
            <span className="text-xs">Columns</span>
          </div>
          <p className="text-sm font-semibold text-white">
            {dataset.column_count ?? "—"}
          </p>
        </div>
        <div className="bg-slate-800/60 rounded-lg px-3 py-2 text-center">
          <div className="flex items-center justify-center gap-1 text-slate-400 mb-0.5">
            <HardDrive size={11} />
            <span className="text-xs">Size</span>
          </div>
          <p className="text-sm font-semibold text-white">
            {formatBytes(dataset.file_size_bytes)}
          </p>
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-slate-800">
        <p className="text-slate-500 text-xs">Uploaded {formatDate(dataset.created_at)}</p>

        <div className="flex items-center gap-1">
          <Link
            href={`/datasets/${dataset.id}`}
            className="p-2 rounded-lg text-slate-400 hover:text-sky-400 hover:bg-sky-500/10 transition-all"
            title="View details"
          >
            <Eye size={15} />
          </Link>
          <button
            onClick={() => onDelete(dataset.id)}
            className="p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-all"
            title="Delete dataset"
          >
            <Trash2 size={15} />
          </button>
        </div>
      </div>
    </div>
  );
}
