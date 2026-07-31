"use client";
import { useState } from "react";
import { projectChatService } from "@/services/projectChat.service";
import { getErrorMessage } from "@/utils";
import toast from "react-hot-toast";
import { MessageSquare, Loader2, Send, ArrowLeft, FileText, RotateCcw } from "lucide-react";
import Link from "next/link";

type Message = {
  role: "user" | "assistant";
  text: string;
  sources?: { file: string; type: string }[];
};

const SUGGESTED_QUESTIONS = [
  "Ye project kya karta hai?",
  "AutoML SaaS Platform ke features kya hain?",
  "Data quality kaise check hoti hai?",
  "Explainability (SHAP) kaise kaam karta hai?",
];

export default function ProjectChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [resetting, setResetting] = useState(false);

  const sendMessage = async (text?: string) => {
    const userMsg = (text ?? input).trim();
    if (!userMsg) return;

    setMessages((prev) => [...prev, { role: "user", text: userMsg }]);
    setInput("");
    setLoading(true);

    try {
      const res = await projectChatService.sendMessage(userMsg);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: res.assistant_response,
          sources: res.sources,
        },
      ]);
    } catch (e) {
      toast.error(getErrorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    setResetting(true);
    try {
      await projectChatService.resetChat();
      setMessages([]);
      toast.success("Conversation reset ho gayi");
    } catch (e) {
      toast.error(getErrorMessage(e));
    } finally {
      setResetting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition-all"
          >
            <ArrowLeft size={18} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <MessageSquare size={22} className="text-sky-400" />
              Project Docs Assistant
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Ask anything about this AutoML project — README, architecture, features
            </p>
          </div>
        </div>
        <button
          onClick={handleReset}
          disabled={resetting || messages.length === 0}
          className="btn-secondary text-xs px-3 py-2 disabled:opacity-50"
        >
          {resetting ? (
            <Loader2 size={14} className="animate-spin" />
          ) : (
            <RotateCcw size={14} />
          )}
          Reset
        </button>
      </div>

      {/* Chat card */}
      <div className="card flex flex-col h-[600px]">
        <div className="flex-1 overflow-y-auto space-y-3 mb-4 pr-1">
          {messages.length === 0 && (
            <div className="text-center mt-10 space-y-2">
              <MessageSquare size={28} className="text-slate-700 mx-auto" />
              <p className="text-slate-500 text-sm">
                Ask anything about how this project works
              </p>
              <div className="flex flex-wrap justify-center gap-2 mt-3">
                {SUGGESTED_QUESTIONS.map((hint) => (
                  <button
                    key={hint}
                    onClick={() => sendMessage(hint)}
                    className="text-xs bg-slate-800 text-slate-400 px-3 py-1.5 rounded-lg hover:bg-slate-700"
                  >
                    {hint}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={msg.role === "user" ? "ml-auto max-w-[80%]" : "max-w-[80%]"}>
              <div
                className={`p-3 rounded-xl text-sm whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-sky-600 text-white"
                    : "bg-slate-800 text-slate-200"
                }`}
              >
                {msg.text}
              </div>

              {/* Sources — sirf assistant messages ke liye, transparency ke liye */}
              {msg.role === "assistant" && msg.sources && msg.sources.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-1.5">
                  {[...new Set(msg.sources.map((s) => s.file))].map((file) => (
                    <span
                      key={file}
                      className="flex items-center gap-1 text-[11px] text-slate-500 bg-slate-900/60 border border-slate-800 rounded-md px-2 py-0.5"
                    >
                      <FileText size={10} />
                      {file}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="bg-slate-800 text-slate-400 text-sm p-3 rounded-xl max-w-[80%] flex items-center gap-2">
              <Loader2 size={12} className="animate-spin" /> Docs padh raha hoon...
            </div>
          )}
        </div>

        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
            placeholder="Project ke bare mein poochein..."
            className="input flex-1"
            disabled={loading}
          />
          <button
            onClick={() => sendMessage()}
            disabled={loading || !input.trim()}
            className="btn-primary px-4"
          >
            {loading ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
          </button>
        </div>
      </div>
    </div>
  );
}
