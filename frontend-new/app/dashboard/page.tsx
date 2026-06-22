"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { dashboardService } from "@/services/dashboard.service";
import type { DashboardStats } from "@/types";
import StatCard from "@/components/UI/StatCard";
import StatusBadge from "@/components/UI/StatusBadge";
import LoadingSpinner from "@/components/UI/LoadingSpinner";
import { formatBytes, formatNumber, formatDateTime } from "@/utils";
import Link from "next/link";
import {
  Database,
  CheckCircle2,
  HardDrive,
  Rows,
  Plus,
  ArrowRight,
  Zap,
  BarChart3,
  Activity,
  Clock,
} from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardService
      .getStats()
      .then(setStats)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" text="Loading dashboard..." />
      </div>
    );
  }

  const greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return "Good morning";
    if (h < 17) return "Good afternoon";
    return "Good evening";
  };

  return (
    <div className="space-y-8 max-w-7xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">
            {greeting()}, {user?.full_name?.split(" ")[0]}
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Here's an overview of your AutoML workspace
          </p>
        </div>
        <Link href="/datasets" className="btn-primary whitespace-nowrap self-start sm:self-auto">
          <Plus size={16} />
          Upload Dataset
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          label="Total Datasets"
          value={stats?.total_datasets ?? 0}
          icon={Database}
          iconColor="text-sky-400"
          iconBg="bg-sky-500/15 border-sky-500/20"
        />
        <StatCard
          label="Ready Datasets"
          value={stats?.ready_datasets ?? 0}
          icon={CheckCircle2}
          iconColor="text-green-400"
          iconBg="bg-green-500/15 border-green-500/20"
          subtitle={`${stats?.processing_datasets ?? 0} processing`}
        />
        <StatCard
          label="Total Rows"
          value={formatNumber(stats?.total_rows)}
          icon={Rows}
          iconColor="text-purple-400"
          iconBg="bg-purple-500/15 border-purple-500/20"
        />
        <StatCard
          label="Storage Used"
          value={formatBytes(stats?.total_storage_bytes)}
          icon={HardDrive}
          iconColor="text-orange-400"
          iconBg="bg-orange-500/15 border-orange-500/20"
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-5">
              <h3 className="font-semibold text-white flex items-center gap-2">
                <Activity size={16} className="text-sky-400" />
                Recent Datasets
              </h3>
              <Link
                href="/datasets"
                className="text-sky-400 text-sm hover:text-sky-300 flex items-center gap-1 transition-colors"
              >
                View all <ArrowRight size={13} />
              </Link>
            </div>

            {!stats?.recent_datasets?.length ? (
              <div className="text-center py-10">
                <Database size={32} className="text-slate-700 mx-auto mb-3" />
                <p className="text-slate-500 text-sm">No datasets yet</p>
                <Link href="/datasets" className="btn-primary mt-4 inline-flex">
                  <Plus size={14} />
                  Upload your first dataset
                </Link>
              </div>
            ) : (
              <div className="space-y-2">
                {stats.recent_datasets.map((ds) => (
                  <Link
                    key={ds.id}
                    href={`/datasets/${ds.id}`}
                    className="flex items-center justify-between gap-4 px-4 py-3 rounded-xl bg-slate-800/50 hover:bg-slate-800 transition-all group"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-8 h-8 rounded-lg bg-slate-700 flex items-center justify-center flex-shrink-0">
                        <Database size={14} className="text-slate-400" />
                      </div>
                      <div className="min-w-0">
                        <p className="font-medium text-slate-200 text-sm truncate group-hover:text-sky-300 transition-colors">
                          {ds.name}
                        </p>
                        <div className="flex items-center gap-2 mt-0.5">
                          {ds.row_count && (
                            <span className="text-slate-500 text-xs">
                              {formatNumber(ds.row_count)} rows
                            </span>
                          )}
                          {ds.column_count && (
                            <span className="text-slate-500 text-xs">
                              · {ds.column_count} cols
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 flex-shrink-0">
                      <StatusBadge status={ds.status as any} />
                      <span className="text-slate-600 text-xs flex items-center gap-1">
                        <Clock size={10} />
                        {formatDateTime(ds.created_at)}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <div className="card">
            <h3 className="font-semibold text-white flex items-center gap-2 mb-4">
              <Zap size={16} className="text-yellow-400" />
              Platform Modules
            </h3>

            <div className="space-y-3">
              {[
                {
                  label: "Foundation & Infrastructure",
                  desc: "Auth, datasets, dashboard",
                  done: true,
                  module: 1,
                  href: "/dashboard",
                },
                {
                  label: "AutoML Engine",
                  desc: "Training, benchmarking",
                  done: true,
                  module: 2,
                  href: "/training",
                },
                {
                  label: "AI Intelligence",
                  desc: "XAI, SHAP, reports",
                  done: true,
                  module: 3,
                  href: "/intelligence",
                },
                {
                  label: "Production & SaaS",
                  desc: "API generator, deployment",
                  done: true,
                  module: 4,
                  href: "/production",
                },
              ].map((item) => (
                <Link
                  key={item.module}
                  href={item.href}
                  className={`flex items-center gap-3 p-3 rounded-xl transition-all hover:scale-[1.02] cursor-pointer ${
                    item.done
                      ? "bg-green-500/10 border border-green-500/20 hover:bg-green-500/15"
                      : "bg-slate-800/50 border border-slate-700/50 hover:bg-slate-800"
                  }`}
                >
                  <div
                    className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                      item.done
                        ? "bg-green-500 text-white"
                        : "bg-slate-700 text-slate-400"
                    }`}
                  >
                    {item.module}
                  </div>
                  <div className="min-w-0">
                    <p
                      className={`text-sm font-medium truncate ${
                        item.done ? "text-green-300" : "text-slate-300"
                      }`}
                    >
                      {item.label}
                    </p>
                    <p className="text-slate-500 text-xs">{item.desc}</p>
                  </div>
                  {item.done && (
                    <CheckCircle2 size={14} className="text-green-400 ml-auto flex-shrink-0" />
                  )}
                </Link>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 className="font-semibold text-white flex items-center gap-2 mb-4">
              <BarChart3 size={16} className="text-sky-400" />
              Quick Stats
            </h3>
            <div className="space-y-3">
              {[
                {
                  label: "Member for",
                  value: `${stats?.user_since_days ?? 0} days`,
                },
                {
                  label: "Error datasets",
                  value: stats?.error_datasets ?? 0,
                },
                {
                  label: "Your role",
                  value: user?.role ?? "—",
                },
              ].map((item) => (
                <div key={item.label} className="flex items-center justify-between">
                  <span className="text-slate-400 text-sm">{item.label}</span>
                  <span className="text-white text-sm font-medium capitalize">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}