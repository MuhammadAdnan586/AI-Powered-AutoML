"use client";
import React, { useState } from "react";

export default function ProductionPage() {
  const [activeTab, setActiveTab] = useState("api");
  const [selectedSchedule, setSelectedSchedule] = useState("");
const [metrics, setMetrics] = useState<any>(null);
const [loadingMetrics, setLoadingMetrics] = useState(false);

const fetchMetrics = async () => {
  setLoadingMetrics(true);
  try {
    const token = localStorage.getItem("token");
    const res = await fetch("http://localhost:8000/api/v1/monitoring/metrics", {
      headers: { Authorization: `Bearer ${token}` }
    });
    const data = await res.json();
    setMetrics(data);
  } catch (e) {
    console.error(e);
  }
  setLoadingMetrics(false);
};
  const tabs = [
    { id: "api", label: "API Generator" },
    { id: "retraining", label: "Retraining" },
    { id: "notifications", label: "Notifications" },
    { id: "monitoring", label: "Monitoring" },
  ];

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#0f172a", padding: "32px", color: "#f1f5f9" }}>

      <div style={{ marginBottom: "32px" }}>
        <h1 style={{ fontSize: "28px", fontWeight: "700", color: "#f1f5f9", margin: 0 }}>SaaS & Production</h1>
        <p style={{ color: "#94a3b8", marginTop: "6px", fontSize: "14px" }}>Deploy, Monitor & Automate your ML Models</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "16px", marginBottom: "32px" }}>
        {[
          { label: "APIs Deployed", value: "0", bg: "#1e3a8a", border: "#3b82f6", icon: "🔌" },
          { label: "Active Schedules", value: "0", bg: "#14532d", border: "#22c55e", icon: "⏰" },
          { label: "Notifications", value: "0", bg: "#713f12", border: "#eab308", icon: "🔔" },
          { label: "System Health", value: "OK", bg: "#4a1d96", border: "#a855f7", icon: "💚" },
        ].map((card) => (
          <div key={card.label} style={{ backgroundColor: card.bg, border: `1px solid ${card.border}`, borderRadius: "12px", padding: "20px", display: "flex", alignItems: "center", gap: "16px" }}>
            <span style={{ fontSize: "32px" }}>{card.icon}</span>
            <div>
              <p style={{ fontSize: "24px", fontWeight: "700", color: "#f1f5f9", margin: 0 }}>{card.value}</p>
              <p style={{ fontSize: "12px", color: "#cbd5e1", margin: 0 }}>{card.label}</p>
            </div>
          </div>
        ))}
      </div>

      <div style={{ backgroundColor: "#1e293b", borderRadius: "12px", overflow: "hidden" }}>
        <div style={{ display: "flex", borderBottom: "1px solid #334155" }}>
          {tabs.map((tab) => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{ padding: "14px 24px", fontSize: "14px", fontWeight: "600", border: "none", cursor: "pointer", backgroundColor: activeTab === tab.id ? "#3b82f6" : "transparent", color: activeTab === tab.id ? "#ffffff" : "#94a3b8", borderBottom: activeTab === tab.id ? "2px solid #60a5fa" : "2px solid transparent" }}>
              {tab.label}
            </button>
          ))}
        </div>

        <div style={{ padding: "28px" }}>

          {activeTab === "api" && (
            <div>
              <h2 style={{ color: "#f1f5f9", fontSize: "20px", fontWeight: "600", marginBottom: "8px" }}>No-Code REST API Generator</h2>
              <p style={{ color: "#94a3b8", marginBottom: "24px", fontSize: "14px" }}>After model training, generate a REST API with one click and integrate it directly into your application.</p>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
                <div style={{ backgroundColor: "#0f172a", borderRadius: "10px", padding: "20px", border: "1px solid #334155" }}>
                  <h3 style={{ color: "#60a5fa", marginBottom: "16px", fontSize: "15px" }}>How It Works</h3>
                  {["1. Train your ML model", "2. Click Generate API button", "3. Receive a unique API Key", "4. Integrate into your application"].map((step) => (
                    <div key={step} style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "10px" }}>
                      <span style={{ color: "#22c55e" }}>✓</span>
                      <span style={{ color: "#cbd5e1", fontSize: "14px" }}>{step}</span>
                    </div>
                  ))}
                </div>
                <div style={{ backgroundColor: "#0d1117", borderRadius: "10px", padding: "20px", border: "1px solid #334155", fontFamily: "monospace" }}>
                  <p style={{ color: "#6b7280", fontSize: "12px", marginBottom: "8px" }}># Example API Call</p>
                  <p style={{ color: "#60a5fa", fontSize: "13px" }}>POST /api/v1/predict/your-model</p>
                  <p style={{ color: "#fbbf24", fontSize: "12px", marginTop: "12px" }}>Headers:</p>
                  <p style={{ color: "#a3e635", fontSize: "12px" }}>X-API-Key: your-secret-key</p>
                  <p style={{ color: "#fbbf24", fontSize: "12px", marginTop: "8px" }}>Body:</p>
                  <p style={{ color: "#f1f5f9", fontSize: "12px" }}>{"{"} "feature1": 1.5, "feature2": 2.3 {"}"}</p>
                  <p style={{ color: "#fbbf24", fontSize: "12px", marginTop: "8px" }}>Response:</p>
                  <p style={{ color: "#22c55e", fontSize: "12px" }}>{"{"} "prediction": 1, "probability": 0.94 {"}"}</p>
                </div>
              </div>
              <a href="http://localhost:8000/docs#/API%20Generator" target="_blank" style={{ marginTop: "20px", display: "inline-block", backgroundColor: "#3b82f6", color: "#ffffff", padding: "12px 28px", borderRadius: "8px", textDecoration: "none", fontWeight: "600", fontSize: "14px" }}>
                Open API Docs →
              </a>
            </div>
          )}

          {activeTab === "retraining" && (
            <div>
              <h2 style={{ color: "#f1f5f9", fontSize: "20px", fontWeight: "600", marginBottom: "8px" }}>Scheduled Retraining (Cron Jobs)</h2>
              <p style={{ color: "#94a3b8", marginBottom: "24px", fontSize: "14px" }}>Automatically retrain your model when new data arrives. No manual intervention required.</p>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px", marginBottom: "24px" }}>
                {[
                  { label: "Daily", cron: "0 2 * * *", desc: "Every day at 2:00 AM", color: "#1e3a8a", border: "#3b82f6" },
                  { label: "Weekly", cron: "0 2 * * 1", desc: "Every Monday at 2:00 AM", color: "#14532d", border: "#22c55e" },
                  { label: "Monthly", cron: "0 2 1 * *", desc: "1st of every month at 2:00 AM", color: "#4a1d96", border: "#a855f7" },
                ].map((item) => (
                  <div key={item.label} onClick={() => setSelectedSchedule(item.cron)} style={{ backgroundColor: selectedSchedule === item.cron ? item.color : "#0f172a", border: `2px solid ${selectedSchedule === item.cron ? item.border : "#334155"}`, borderRadius: "10px", padding: "20px", cursor: "pointer" }}>
                    <h3 style={{ color: "#f1f5f9", fontWeight: "600", marginBottom: "6px" }}>{item.label}</h3>
                    <p style={{ color: "#94a3b8", fontSize: "13px", marginBottom: "10px" }}>{item.desc}</p>
                    <code style={{ backgroundColor: "#0d1117", color: "#a3e635", padding: "4px 8px", borderRadius: "4px", fontSize: "12px" }}>{item.cron}</code>
                    {selectedSchedule === item.cron && <p style={{ color: "#22c55e", fontSize: "12px", marginTop: "8px" }}>✓ Selected</p>}
                  </div>
                ))}
              </div>
              {selectedSchedule && (
                <div style={{ backgroundColor: "#0f172a", border: "1px solid #22c55e", borderRadius: "8px", padding: "16px", marginBottom: "16px" }}>
                  <p style={{ color: "#22c55e", fontSize: "14px" }}>Selected Schedule: <strong>{selectedSchedule}</strong></p>
                  <p style={{ color: "#94a3b8", fontSize: "13px", marginTop: "4px" }}>Go to API Docs to create this schedule for your model.</p>
                </div>
              )}
              <a href="http://localhost:8000/docs#/Scheduled%20Retraining" target="_blank" style={{ display: "inline-block", backgroundColor: "#16a34a", color: "#ffffff", padding: "12px 28px", borderRadius: "8px", textDecoration: "none", fontWeight: "600", fontSize: "14px" }}>
                Manage Schedules →
              </a>
            </div>
          )}

          {activeTab === "notifications" && (
            <div>
              <h2 style={{ color: "#f1f5f9", fontSize: "20px", fontWeight: "600", marginBottom: "8px" }}>Notification System</h2>
              <p style={{ color: "#94a3b8", marginBottom: "24px", fontSize: "14px" }}>Receive email and in-app notifications when model training or retraining is complete.</p>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "24px" }}>
                <div style={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "10px", padding: "20px" }}>
                  <h3 style={{ color: "#60a5fa", marginBottom: "16px" }}>Email Notifications</h3>
                  <div style={{ backgroundColor: "#1e293b", borderRadius: "8px", padding: "16px" }}>
                    <p style={{ color: "#f1f5f9", fontWeight: "600", marginBottom: "4px" }}>Your Model is Ready!</p>
                    <p style={{ color: "#94a3b8", fontSize: "13px" }}>Model: XGBoost Classifier</p>
                    <p style={{ color: "#94a3b8", fontSize: "13px" }}>Project: Customer Churn</p>
                    <p style={{ color: "#22c55e", fontWeight: "700", fontSize: "18px", marginTop: "8px" }}>Accuracy: 94.2%</p>
                    <a href="/dashboard" style={{ marginTop: "12px", backgroundColor: "#3b82f6", color: "#fff", padding: "8px 16px", borderRadius: "6px", display: "inline-block", fontSize: "13px", textDecoration: "none" }}>
                      View Dashboard
                    </a>
                  </div>
                </div>
                <div style={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "10px", padding: "20px" }}>
                  <h3 style={{ color: "#fbbf24", marginBottom: "16px" }}>In-App Notifications</h3>
                  <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                    <div style={{ backgroundColor: "#14532d", border: "1px solid #22c55e", borderRadius: "6px", padding: "12px" }}>
                      <p style={{ color: "#86efac", fontSize: "13px", margin: 0 }}>✅ Model training complete — Accuracy: 94.2%</p>
                    </div>
                    <div style={{ backgroundColor: "#1e3a8a", border: "1px solid #3b82f6", borderRadius: "6px", padding: "12px" }}>
                      <p style={{ color: "#93c5fd", fontSize: "13px", margin: 0 }}>🔄 Retraining scheduled for Monday 2:00 AM</p>
                    </div>
                    <div style={{ backgroundColor: "#713f12", border: "1px solid #eab308", borderRadius: "6px", padding: "12px" }}>
                      <p style={{ color: "#fde68a", fontSize: "13px", margin: 0 }}>⚠️ Dataset quality score dropped to 72%</p>
                    </div>
                  </div>
                </div>
              </div>
              <a href="http://localhost:8000/docs#/Notifications" target="_blank" style={{ display: "inline-block", backgroundColor: "#d97706", color: "#ffffff", padding: "12px 28px", borderRadius: "8px", textDecoration: "none", fontWeight: "600", fontSize: "14px" }}>
                Notification Settings →
              </a>
            </div>
          )}

          {activeTab === "monitoring" && (
            <div>
              <h2 style={{ color: "#f1f5f9", fontSize: "20px", fontWeight: "600", marginBottom: "8px" }}>System Monitoring</h2>
              <p style={{ color: "#94a3b8", marginBottom: "24px", fontSize: "14px" }}>Real-time system metrics, API usage statistics, and model performance tracking.</p>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px", marginBottom: "24px" }}>
                {[
{ label: "CPU Usage", value: metrics ? `${metrics.cpu.percent}%` : "—", unit: `${metrics?.cpu?.cores || "—"} cores`, color: "#3b82f6", bg: "#1e3a8a" },
{ label: "Memory", value: metrics ? `${metrics.memory.used_gb}GB` : "—", unit: `of ${metrics?.memory?.total_gb || "—"}GB`, color: "#22c55e", bg: "#14532d" },
{ label: "Total API Calls", value: "0", unit: "requests", color: "#a855f7", bg: "#4a1d96" },
                ].map((m) => (
                  <div key={m.label} style={{ backgroundColor: m.bg, borderRadius: "10px", padding: "20px", textAlign: "center", border: `1px solid ${m.color}` }}>
                    <p style={{ fontSize: "28px", fontWeight: "700", color: m.color, margin: 0 }}>{m.value}</p>
                    <p style={{ color: "#94a3b8", fontSize: "12px", margin: "4px 0" }}>{m.unit}</p>
                    <p style={{ color: "#f1f5f9", fontSize: "13px", margin: 0 }}>{m.label}</p>
                  </div>
                ))}
              </div>
              <div style={{ display: "flex", gap: "12px" }}>
                <a href="http://localhost:8000/api/v1/monitoring/health" target="_blank" style={{ display: "inline-block", backgroundColor: "#7c3aed", color: "#ffffff", padding: "12px 28px", borderRadius: "8px", textDecoration: "none", fontWeight: "600", fontSize: "14px" }}>Health Check →</a>
                <a href="http://localhost:8000/api/v1/monitoring/metrics" target="_blank" style={{ display: "inline-block", backgroundColor: "#374151", color: "#ffffff", padding: "12px 28px", borderRadius: "8px", textDecoration: "none", fontWeight: "600", fontSize: "14px" }}>System Metrics →</a>
                <a href="http://localhost:8000/api/v1/monitoring/api-stats" target="_blank" style={{ display: "inline-block", backgroundColor: "#0369a1", color: "#ffffff", padding: "12px 28px", borderRadius: "8px", textDecoration: "none", fontWeight: "600", fontSize: "14px" }}>API Stats →</a>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}