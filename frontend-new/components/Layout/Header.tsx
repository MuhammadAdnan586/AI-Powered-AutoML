"use client";
import { usePathname } from "next/navigation";

export default function Header() {
  const pathname = usePathname();
  const title = pathname === "/dashboard" ? "Dashboard" : pathname === "/datasets" ? "Datasets" : "AutoML SaaS";

  return (
    <header style={{height:"64px", background:"#1e293b", borderBottom:"1px solid #334155", display:"flex", alignItems:"center", padding:"0 24px", position:"sticky", top:0, zIndex:30}}>
      <h2 style={{color:"white", fontWeight:"600", fontSize:"18px"}}>{title}</h2>
    </header>
  );
}