import { cn, getStatusColor } from "@/utils";
import type { DatasetStatus } from "@/types";

const statusLabels: Record<DatasetStatus, string> = {
  ready: "Ready",
  processing: "Processing",
  uploading: "Uploading",
  error: "Error",
};

const statusDots: Record<DatasetStatus, string> = {
  ready: "bg-green-400",
  processing: "bg-yellow-400 animate-pulse",
  uploading: "bg-blue-400 animate-pulse",
  error: "bg-red-400",
};

export default function StatusBadge({ status }: { status: DatasetStatus }) {
  return (
    <span className={cn("badge", getStatusColor(status))}>
      <span className={cn("w-1.5 h-1.5 rounded-full", statusDots[status])} />
      {statusLabels[status]}
    </span>
  );
}
