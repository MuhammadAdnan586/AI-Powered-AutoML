"use client";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { Bell, Search } from "lucide-react";

const pageTitles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/datasets": "Datasets",
  "/settings": "Settings",
};

function getTitle(pathname: string): string {
  if (pageTitles[pathname]) return pageTitles[pathname];
  if (pathname.startsWith("/datasets/")) return "Dataset Details";
  return "AutoML SaaS";
}

export default function Header() {
  const pathname = usePathname();
  const { user } = useAuth();

  return (
    <header className="h-16 bg-slate-900/80 backdrop-blur border-b border-slate-800 flex items-center justify-between px-6 sticky top-0 z-30">
      {/* Page title */}
      <div>
        <h2 className="text-lg font-semibold text-white">{getTitle(pathname)}</h2>
      </div>

      {/* Right actions */}
      <div className="flex items-center gap-3">
        {/* Notification bell */}
        <button className="relative w-9 h-9 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 hover:text-slate-200 hover:bg-slate-700 transition-all">
          <Bell size={16} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-sky-500 rounded-full" />
        </button>

        {/* User avatar */}
        <div className="flex items-center gap-2 pl-3 border-l border-slate-700">
          <div className="w-8 h-8 rounded-full bg-sky-500/20 border border-sky-500/30 flex items-center justify-center text-sky-400 text-xs font-bold">
            {user?.full_name?.charAt(0).toUpperCase() || "U"}
          </div>
          <div className="hidden sm:block">
            <p className="text-xs font-medium text-slate-200 leading-none">{user?.full_name}</p>
            <p className="text-xs text-slate-500 mt-0.5 capitalize">{user?.role}</p>
          </div>
        </div>
      </div>
    </header>
  );
}
