import React, { useState } from "react";
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NAV_SECTIONS = [
  {
    label: "Module 1 – Foundation",
    items: [
      { path: "/dashboard", icon: "🏠", label: "Dashboard" },
      { path: "/datasets", icon: "📁", label: "Datasets" },
    ],
  },
  {
    label: "Module 2 – AutoML Engine",
    items: [
      { path: "/preprocessing", icon: "🧹", label: "Preprocessing" },
      { path: "/feature-engineering", icon: "🔧", label: "Feature Engineering" },
      { path: "/automl", icon: "🤖", label: "AutoML Training" },
    ],
  },
  {
    label: "Module 3 – AI Intelligence",
    items: [
      { path: "/explainability", icon: "💡", label: "Explainability (XAI)", disabled: true },
      { path: "/data-quality", icon: "📋", label: "Data Quality", disabled: true },
      { path: "/reports", icon: "📄", label: "Reports", disabled: true },
      { path: "/chatbot", icon: "💬", label: "AI Chat Assistant", disabled: true },
    ],
  },
  {
    label: "Module 4 – Production",
    items: [
      { path: "/api-generator", icon: "🔌", label: "API Generator", disabled: true },
      { path: "/retraining", icon: "🔄", label: "Scheduled Retraining", disabled: true },
      { path: "/monitoring", icon: "📡", label: "Monitoring", disabled: true },
    ],
  },
];

export default function MainLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div style={s.shell}>
      {/* Sidebar */}
      <aside style={{ ...s.sidebar, width: collapsed ? "64px" : "240px" }}>
        {/* Logo */}
        <div style={s.logo}>
          <span style={s.logoIcon}>🤖</span>
          {!collapsed && <span style={s.logoText}>AutoML Platform</span>}
        </div>

        {/* Collapse toggle */}
        <button style={s.collapseBtn} onClick={() => setCollapsed(!collapsed)}>
          {collapsed ? "▶" : "◀"}
        </button>

        {/* Nav sections */}
        <nav style={s.nav}>
          {NAV_SECTIONS.map((section) => (
            <div key={section.label} style={s.navSection}>
              {!collapsed && (
                <div style={s.sectionLabel}>{section.label}</div>
              )}
              {section.items.map((item) =>
                item.disabled ? (
                  <div
                    key={item.path}
                    style={s.navItemDisabled}
                    title={collapsed ? item.label : undefined}
                  >
                    <span style={s.navIcon}>{item.icon}</span>
                    {!collapsed && (
                      <>
                        <span style={s.navLabel}>{item.label}</span>
                        <span style={s.comingSoon}>Soon</span>
                      </>
                    )}
                  </div>
                ) : (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    title={collapsed ? item.label : undefined}
                    style={({ isActive }) => ({
                      ...s.navItem,
                      ...(isActive ? s.navItemActive : {}),
                    })}
                  >
                    <span style={s.navIcon}>{item.icon}</span>
                    {!collapsed && <span style={s.navLabel}>{item.label}</span>}
                  </NavLink>
                )
              )}
            </div>
          ))}
        </nav>

        {/* User footer */}
        <div style={s.userFooter}>
          {!collapsed && (
            <div style={s.userInfo}>
              <div style={s.userAvatar}>{user?.username?.[0]?.toUpperCase() || "U"}</div>
              <div>
                <div style={s.userName}>{user?.username || "User"}</div>
                <div style={s.userEmail}>{user?.email || ""}</div>
              </div>
            </div>
          )}
          <button style={s.logoutBtn} onClick={handleLogout} title="Logout">
            🚪{!collapsed && " Logout"}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main style={s.main}>
        <Outlet />
      </main>
    </div>
  );
}

const s = {
  shell: { display: "flex", height: "100vh", background: "#f3f4f6", fontFamily: "system-ui, sans-serif" },
  sidebar: {
    background: "#1e1b4b",
    display: "flex",
    flexDirection: "column",
    transition: "width 0.2s ease",
    overflow: "hidden",
    flexShrink: 0,
    position: "relative",
  },
  logo: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    padding: "20px 16px",
    borderBottom: "1px solid rgba(255,255,255,0.1)",
  },
  logoIcon: { fontSize: "24px", flexShrink: 0 },
  logoText: { color: "#fff", fontWeight: 700, fontSize: "16px", whiteSpace: "nowrap" },
  collapseBtn: {
    position: "absolute",
    top: "20px",
    right: "-12px",
    width: "24px",
    height: "24px",
    background: "#7c3aed",
    color: "#fff",
    border: "none",
    borderRadius: "50%",
    cursor: "pointer",
    fontSize: "10px",
    zIndex: 10,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  nav: { flex: 1, overflowY: "auto", padding: "8px 0", overflowX: "hidden" },
  navSection: { marginBottom: "8px" },
  sectionLabel: {
    fontSize: "10px",
    fontWeight: 700,
    color: "#a78bfa",
    padding: "12px 16px 4px",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
    whiteSpace: "nowrap",
  },
  navItem: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    padding: "9px 16px",
    color: "rgba(255,255,255,0.7)",
    textDecoration: "none",
    fontSize: "13px",
    fontWeight: 500,
    borderRadius: "0",
    transition: "all 0.15s",
    whiteSpace: "nowrap",
  },
  navItemActive: {
    background: "rgba(124,58,237,0.3)",
    color: "#fff",
    borderRight: "3px solid #7c3aed",
  },
  navItemDisabled: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    padding: "9px 16px",
    color: "rgba(255,255,255,0.3)",
    fontSize: "13px",
    cursor: "not-allowed",
    whiteSpace: "nowrap",
  },
  navIcon: { fontSize: "16px", flexShrink: 0, width: "20px", textAlign: "center" },
  navLabel: { flex: 1 },
  comingSoon: {
    fontSize: "9px",
    background: "rgba(255,255,255,0.1)",
    color: "rgba(255,255,255,0.4)",
    padding: "1px 5px",
    borderRadius: "8px",
  },
  userFooter: {
    padding: "12px",
    borderTop: "1px solid rgba(255,255,255,0.1)",
  },
  userInfo: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    marginBottom: "8px",
  },
  userAvatar: {
    width: "32px",
    height: "32px",
    background: "#7c3aed",
    borderRadius: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#fff",
    fontWeight: 700,
    fontSize: "14px",
    flexShrink: 0,
  },
  userName: { color: "#fff", fontSize: "13px", fontWeight: 600 },
  userEmail: { color: "rgba(255,255,255,0.4)", fontSize: "11px" },
  logoutBtn: {
    width: "100%",
    padding: "7px",
    background: "rgba(239,68,68,0.15)",
    color: "#fca5a5",
    border: "1px solid rgba(239,68,68,0.2)",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "13px",
    fontWeight: 500,
  },
  main: { flex: 1, overflowY: "auto", padding: "0" },
};
