"use client";
import type { Dataset } from "@/types";
import { formatNumber } from "@/utils";
import { AlertCircle, CheckCircle2, Hash } from "lucide-react";

interface ColumnInfoProps {
  dataset: Dataset;
}

export default function ColumnInfo({ dataset }: ColumnInfoProps) {
  const columns = dataset.column_names || [];
  const dtypes = dataset.dtypes_info || {};
  const missing = dataset.missing_values_info || {};
  const totalRows = dataset.row_count || 1;

  const getDtypeColor = (dtype: string) => {
    if (dtype.includes("int") || dtype.includes("float")) return "text-blue-400 bg-blue-400/10";
    if (dtype.includes("object") || dtype.includes("str")) return "text-purple-400 bg-purple-400/10";
    if (dtype.includes("bool")) return "text-yellow-400 bg-yellow-400/10";
    if (dtype.includes("date")) return "text-green-400 bg-green-400/10";
    return "text-slate-400 bg-slate-400/10";
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <Hash size={16} className="text-sky-400" />
          Column Information
          <span className="text-slate-500 text-xs font-normal">
            ({columns.length} columns)
          </span>
        </h3>
      </div>

      <div className="space-y-2">
        {columns.map((col, idx) => {
          const missingCount = missing[col] || 0;
          const missingPct = totalRows > 0 ? ((missingCount / totalRows) * 100).toFixed(1) : "0";
          const hasMissing = missingCount > 0;
          const dtype = dtypes[col] || "unknown";

          return (
            <div
              key={col}
              className="flex items-center justify-between gap-4 px-4 py-3 rounded-xl bg-slate-800/50 hover:bg-slate-800 transition-colors"
            >
              {/* Column name + index */}
              <div className="flex items-center gap-3 min-w-0 flex-1">
                <span className="text-slate-600 text-xs font-mono w-6 text-right flex-shrink-0">
                  {idx + 1}
                </span>
                <span className="font-medium text-slate-200 truncate">{col}</span>
              </div>

              {/* Dtype badge */}
              <span
                className={`text-xs px-2 py-0.5 rounded-md font-mono flex-shrink-0 ${getDtypeColor(dtype)}`}
              >
                {dtype}
              </span>

              {/* Missing values */}
              <div className="flex items-center gap-1.5 flex-shrink-0 min-w-[100px] justify-end">
                {hasMissing ? (
                  <>
                    <AlertCircle size={13} className="text-yellow-400" />
                    <span className="text-yellow-400 text-xs">
                      {formatNumber(missingCount)} ({missingPct}%)
                    </span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 size={13} className="text-green-400" />
                    <span className="text-green-400 text-xs">Complete</span>
                  </>
                )}
              </div>

              {/* Fill rate bar */}
              <div className="w-20 flex-shrink-0">
                <div className="w-full bg-slate-700 rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full transition-all ${
                      hasMissing ? "bg-yellow-500" : "bg-green-500"
                    }`}
                    style={{
                      width: `${100 - parseFloat(missingPct)}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
