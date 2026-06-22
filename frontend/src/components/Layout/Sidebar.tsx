"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside style={{width:"240px", background:"#1e293b", borderRight:"1px solid #334155", height:"100vh", position:"fixed", left:0, top:0, display:"flex", flexDirection:"column", padding:"24px 16px"}}>
      <div style={{marginBottom:"32px"}}>
        <h1 style={{color:"#38bdf8", fontWeight:"bold", fontSize:"18px"}}>🤖 AutoML</h1>
        <p style={{color:"#64748b", fontSize:"12px"}}>SaaS Platform</p>
      </div>

      <nav style={{flex:1}}>
        <Link href="/dashboard" style={{display:"block", padding:"10px 12px", borderRadius:"8px", color: pathname === "/dashboard" ? "#38bdf8" : "#94a3b8", background: pathname === "/dashboard" ? "#0ea5e920" : "transparent", marginBottom:"4px", textDecoration:"none"}}>
          📊 Dashboard
        </Link>
        <Link href="/datasets" style={{display:"block", padding:"10px 12px", borderRadius:"8px", color: pathname === "/datasets" ? "#38bdf8" : "#94a3b8", background: pathname === "/datasets" ? "#0ea5e920" : "transparent", marginBottom:"4px", textDecoration:"none"}}>
          🗄️ Datasets
        </Link>
      </nav>

      <div style={{borderTop:"1px solid #334155", paddingTop:"16px"}}>
        <p style={{color:"#94a3b8", fontSize:"13px", marginBottom:"8px"}}>{user?.full_name}</p>
        <p style={{color:"#64748b", fontSize:"11px", marginBottom:"12px"}}>{user?.email}</p>
        <button onClick={logout} style={{width:"100%", padding:"8px", background:"#dc262620", color:"#f87171", border:"1px solid #dc262640", borderRadius:"8px", cursor:"pointer"}}>
          Logout
        </button>
      </div>
    </aside>
  );
}