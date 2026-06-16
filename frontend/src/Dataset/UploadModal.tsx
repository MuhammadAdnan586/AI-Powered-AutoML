"use client";
import { useState, useCallback } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Upload, X, FileSpreadsheet, Loader2, AlertCircle } from "lucide-react";
import { datasetService } from "@/services/dataset.service";
import { formatBytes, getErrorMessage } from "@/utils";
import toast from "react-hot-toast";

const schema = z.object({
  name: z.string().min(1, "Dataset name is required").max(255),
  description: z.string().max(1000).optional(),
});
type FormData = z.infer<typeof schema>;

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function UploadModal({ isOpen, onClose, onSuccess }: UploadModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const handleClose = () => {
    if (isUploading) return;
    setFile(null);
    reset();
    onClose();
  };

  const validateFile = (f: File): boolean => {
    const allowedExts = ["csv", "xlsx", "xls"];
    const ext = f.name.split(".").pop()?.toLowerCase() || "";
    if (!allowedExts.includes(ext)) {
      toast.error("Only CSV and Excel files allowed");
      return false;
    }
    if (f.size > 100 * 1024 * 1024) {
      toast.error("File size must be under 100MB");
      return false;
    }
    return true;
  };

  const handleFileSelect = (f: File) => {
    if (validateFile(f)) setFile(f);
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFileSelect(f);
  }, []);

  const onSubmit = async (data: FormData) => {
    if (!file) {
      toast.error("Please select a file");
      return;
    }
    setIsUploading(true);
    setUploadProgress(0);

    // Simulate progress
    const interval = setInterval(() => {
      setUploadProgress((prev) => Math.min(prev + 10, 85));
    }, 200);

    try {
      await datasetService.upload(file, data.name, data.description);
      clearInterval(interval);
      setUploadProgress(100);
      toast.success("Dataset uploaded successfully! 🎉");
      onSuccess();
      handleClose();
    } catch (err) {
      clearInterval(interval);
      toast.error(getErrorMessage(err));
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={handleClose} />

      <div className="relative w-full max-w-lg bg-slate-900 border border-slate-700 rounded-2xl p-6 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-white">Upload Dataset</h3>
            <p className="text-slate-400 text-sm">Supports CSV, XLSX, XLS (max 100MB)</p>
          </div>
          <button onClick={handleClose} disabled={isUploading} className="text-slate-400 hover:text-slate-200 transition-colors">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          {/* Drop zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={onDrop}
            onClick={() => document.getElementById("file-input")?.click()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${
              isDragging
                ? "border-sky-500 bg-sky-500/10"
                : file
                ? "border-green-500/50 bg-green-500/5"
                : "border-slate-700 hover:border-slate-500 hover:bg-slate-800/50"
            }`}
          >
            <input
              id="file-input"
              type="file"
              accept=".csv,.xlsx,.xls"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
            />

            {file ? (
              <div className="flex flex-col items-center gap-2">
                <FileSpreadsheet size={32} className="text-green-400" />
                <p className="font-medium text-green-400">{file.name}</p>
                <p className="text-slate-400 text-sm">{formatBytes(file.size)}</p>
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); setFile(null); }}
                  className="text-xs text-red-400 hover:text-red-300 mt-1"
                >
                  Remove file
                </button>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2">
                <Upload size={32} className="text-slate-500" />
                <p className="text-slate-300 font-medium">Drop your file here</p>
                <p className="text-slate-500 text-sm">or click to browse</p>
              </div>
            )}
          </div>

          {/* Dataset name */}
          <div>
            <label className="label">Dataset Name *</label>
            <input
              {...register("name")}
              placeholder="e.g. Customer Churn Dataset"
              className={`input ${errors.name ? "input-error" : ""}`}
              disabled={isUploading}
            />
            {errors.name && <p className="text-red-400 text-xs mt-1">{errors.name.message}</p>}
          </div>

          {/* Description */}
          <div>
            <label className="label">Description (optional)</label>
            <textarea
              {...register("description")}
              rows={2}
              placeholder="Brief description of this dataset..."
              className="input resize-none"
              disabled={isUploading}
            />
          </div>

          {/* Progress bar */}
          {isUploading && (
            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>Uploading & processing...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2">
                <div
                  className="bg-sky-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={handleClose} disabled={isUploading} className="btn-secondary flex-1">
              Cancel
            </button>
            <button type="submit" disabled={isUploading || !file} className="btn-primary flex-1">
              {isUploading ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload size={14} />
                  Upload Dataset
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
