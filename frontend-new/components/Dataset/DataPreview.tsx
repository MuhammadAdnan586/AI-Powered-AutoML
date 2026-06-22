"use client";
import { useState } from "react";
import type { Dataset } from "@/types";
import { Table, ChevronLeft, ChevronRight } from "lucide-react";

interface DataPreviewProps {
  dataset: Dataset;
}

export default function DataPreview({ dataset }: DataPreviewProps) {
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 5;

  const rows = dataset.preview_data || [];
  const columns = dataset.column_names || [];

  if (!rows.length || !columns.length) {
    return (
      <div className="card text-center py-10">
        <Table size={28} className="text-slate-600 mx-auto mb-2" />
        <p className="text-slate-500 text-sm">No preview available</p>
      </div>
    );
  }

  const totalPages = Math.ceil(rows.length / PAGE_SIZE);
  const pageRows = rows.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <Table size={16} className="text-sky-400" />
          Data Preview
          <span className="text-slate-500 text-xs font-normal ml-1">
            (first {rows.length} rows)
          </span>
        </h3>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-slate-800">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-800/80">
              {columns.map((col) => (
                <th
                  key={col}
                  className="px-4 py-3 text-left text-xs font-semibold text-slate-300 whitespace-nowrap border-b border-slate-700"
                >
                  <div className="flex flex-col gap-0.5">
                    <span>{col}</span>
                    {dataset.dtypes_info?.[col] && (
                      <span className="text-slate-500 font-normal text-xs">
                        {dataset.dtypes_info[col]}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {pageRows.map((row, rowIdx) => (
              <tr
                key={rowIdx}
                className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors"
              >
                {columns.map((col) => {
                  const val = row[col];
                  const isNull = val === null || val === undefined || val === "";
                  return (
                    <td
                      key={col}
                      className={`px-4 py-2.5 whitespace-nowrap max-w-[180px] truncate ${
                        isNull ? "text-slate-600 italic" : "text-slate-300"
                      }`}
                    >
                      {isNull ? "null" : String(val)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-3">
          <p className="text-xs text-slate-500">
            Page {page + 1} of {totalPages}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => p - 1)}
              disabled={page === 0}
              className="btn-ghost p-1.5 disabled:opacity-30"
            >
              <ChevronLeft size={14} />
            </button>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={page >= totalPages - 1}
              className="btn-ghost p-1.5 disabled:opacity-30"
            >
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
