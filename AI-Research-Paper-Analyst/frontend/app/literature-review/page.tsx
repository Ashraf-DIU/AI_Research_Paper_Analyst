"use client";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { ErrorMessage, Loading } from "@/components/common/Status";
import PaperPicker from "@/components/papers/PaperPicker";
import { generateReview } from "@/lib/api";
import { usePapers } from "@/lib/usePapers";
import { useWorkspace } from "@/lib/useWorkspace";

export default function ReviewPage() {
  const { workspaceId, error } = useWorkspace();
  const { papers } = usePapers(workspaceId);
  const [sel, setSel] = useState<string[]>([]);
  const [topic, setTopic] = useState("");
  const [style, setStyle] = useState("numeric");
  const [words, setWords] = useState(900);
  const [md, setMd] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  async function run() {
    if (!workspaceId) return;
    setBusy(true); setErr(null);
    try { setMd((await generateReview({ workspace_id: workspaceId, topic, paper_ids: sel.length ? sel : undefined, citation_style: style, word_count: words })).markdown); }
    catch (e) { setErr((e as Error).message); } finally { setBusy(false); }
  }
  return (
    <div className="space-y-4">
      <h1 className="text-3xl">Literature review</h1>
      <ErrorMessage message={error || err} />
      <PaperPicker papers={papers} selected={sel} onChange={setSel} />
      <input className="input" placeholder="Research topic" value={topic} onChange={(e) => setTopic(e.target.value)} aria-label="Topic" />
      <div className="flex gap-3">
        <select className="input" value={style} onChange={(e) => setStyle(e.target.value)} aria-label="Citation style">
          <option value="numeric">Numeric [1]</option><option value="numeric-page">Numeric with page [1, p. 5]</option>
        </select>
        <input className="input" type="number" min={300} max={4000} step={100} value={words} onChange={(e) => setWords(+e.target.value)} aria-label="Word count" />
      </div>
      <button className="btn" disabled={busy || topic.length < 3} onClick={run}>Generate draft</button>
      {busy && <Loading text="Writing each section from retrieved evidence…" />}
      {md && (
        <>
          <button className="btn-ghost" onClick={() => navigator.clipboard.writeText(md)}>Copy markdown</button>
          <article className="card prose-lite"><ReactMarkdown>{md}</ReactMarkdown></article>
        </>
      )}
    </div>
  );
}
