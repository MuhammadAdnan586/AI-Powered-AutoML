import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Merge Tailwind classes safely */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Format bytes to human-readable size */
export function formatBytes(bytes?: number): string {
  if (!bytes || bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

/** Format number with commas */
export function formatNumber(n?: number): string {
  if (n === undefined || n === null) return "—";
  return n.toLocaleString();
}

/** Format date to readable string */
export function formatDate(dateStr?: string): string {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/** Format datetime */
export function formatDateTime(dateStr?: string): string {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** Get status color classes */
export function getStatusColor(status: string): string {
  const map: Record<string, string> = {
    ready: "text-green-400 bg-green-400/10 border-green-400/20",
    processing: "text-yellow-400 bg-yellow-400/10 border-yellow-400/20",
    uploading: "text-blue-400 bg-blue-400/10 border-blue-400/20",
    error: "text-red-400 bg-red-400/10 border-red-400/20",
  };
  return map[status] || "text-gray-400 bg-gray-400/10 border-gray-400/20";
}

/** Get file extension icon emoji */
export function getFileIcon(ext?: string): string {
  const map: Record<string, string> = {
    csv: "📊",
    xlsx: "📗",
    xls: "📗",
  };
  return map[ext || ""] || "📁";
}

/** Extract error message from Axios error */
export function getErrorMessage(error: unknown): string {
  if (error && typeof error === "object" && "response" in error) {
    const res = (error as any).response;
    if (res?.data?.detail) return res.data.detail;
    if (res?.data?.errors?.[0]?.message) return res.data.errors[0].message;
  }
  if (error instanceof Error) return error.message;
  return "Something went wrong. Please try again.";
}
