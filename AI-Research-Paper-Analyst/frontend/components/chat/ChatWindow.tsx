"use client";
import { useState } from "react";
import { askQuestion } from "@/lib/api";
import type { ChatMessage, Paper } from "@/types";
import { ErrorMessage, Loading } from "../common/Status";
import PaperPicker from "../papers/PaperPicker";
import CitationCard from "./CitationCard";

export default function ChatWindow({ workspaceId, papers }: { workspaceId: string; papers: Paper[] }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [q, setQ] = useState("");
  const [convo, setConvo] = useState<string>();
  const [selected, setSelected] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function send() {
    const question = q.trim();
    if (!question || busy) return;
    setQ(""); setErr(null); setBusy(true);
    setMessages((m) => [...m, { role: "user", content: question }]);
    try {
      const r = await askQuestion(question, workspaceId, convo, selected.length ? selected : undefined);
      setConvo(r.conversation_id);
      setMessages((m) => [...m, { role: "assistant", content: r.answer, citations: r.citations, warning: r.warning }]);
    } catch (e) { setErr((e as Error).message); } finally { setBusy(false); }
  }

  return (
    <div className="space-y-4">
      <PaperPicker papers={papers} selected={selected} onChange={setSelected} />
      <p className="text-xs text-slate2">{selected.length ? `Searching ${selected.length} selected paper(s)` : "Searching all papers in the workspace"}</p>
      <div className="space-y-4" aria-live="polite">
        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "ml-10 rounded-md bg-accent p-3 text-sm text-white" : "card"}>
            <p className="whitespace-pre-wrap text-sm leading-relaxed">{m.content}</p>
            {m.warning && <p className="mt-2 text-xs text-amber-700">{m.warning}</p>}
            {!!m.citations?.length && <div className="mt-3 grid gap-2 sm:grid-cols-2">{m.citations.map((c) => <CitationCard key={c.label} c={c} />)}</div>}
          </div>
        ))}
        {busy && <Loading text="Searching the papers and drafting an answer…" />}
      </div>
      <ErrorMessage message={err} />
      <div className="flex gap-2">
        <input className="input" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Ask a question across your papers…"
          onKeyDown={(e) => e.key === "Enter" && send()} aria-label="Question" />
        <button className="btn" onClick={send} disabled={busy}>Ask</button>
      </div>
    </div>
  );
}
