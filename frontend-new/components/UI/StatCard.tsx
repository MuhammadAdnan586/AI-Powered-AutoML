import { cn } from "@/utils";
import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  iconColor?: string;
  iconBg?: string;
  trend?: string;
  trendUp?: boolean;
  subtitle?: string;
}

export default function StatCard({
  label,
  value,
  icon: Icon,
  iconColor = "text-sky-400",
  iconBg = "bg-sky-500/15 border-sky-500/20",
  trend,
  trendUp,
  subtitle,
}: StatCardProps) {
  return (
    <div className="card hover:border-slate-700 transition-colors">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-slate-400 text-sm font-medium">{label}</p>
          <p className="text-3xl font-bold text-white mt-1">{value}</p>
          {subtitle && <p className="text-slate-500 text-xs mt-1">{subtitle}</p>}
          {trend && (
            <p
              className={cn(
                "text-xs mt-2 font-medium",
                trendUp ? "text-green-400" : "text-red-400"
              )}
            >
              {trendUp ? "↑" : "↓"} {trend}
            </p>
          )}
        </div>
        <div
          className={cn(
            "w-11 h-11 rounded-xl border flex items-center justify-center flex-shrink-0",
            iconBg
          )}
        >
          <Icon size={20} className={iconColor} />
        </div>
      </div>
    </div>
  );
}
