"use client";
import { useState } from "react";
import { ErrorMessage, Loading } from "@/components/common/Status";
import PaperPicker from "@/components/papers/PaperPicker";
import { findGaps, pdfUrl } from "@/lib/api";
import { pages } from "@/lib/utils";
import { usePapers } from "@/lib/usePapers";
import { useWorkspace } from "@/lib/useWorkspace";
import type { Gap } from "@/types";

export default function GapsPage() {
  const { workspaceId, error } = useWorkspace();
  const { papers } = usePapers(workspaceId);
  const [sel, setSel] = useState<string[]>([]);
  const [gaps, setGaps] = useState<Gap[] | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  async function run() {
    if (!workspaceId) return;
    setBusy(true); setErr(null);
    try { setGaps((await findGaps(workspaceId, sel)).gaps); } catch (e) { setErr((e as Error).message); } finally { setBusy(false); }
  }
  return (
    <div className="space-y-4">
      <h1 className="text-3xl">Research gaps</h1>
      <ErrorMessage message={error || err} />
      <PaperPicker papers={papers} selected={sel} onChange={setSel} />
      <button className="btn" disabled={busy || sel.length < 2} onClick={run}>Find potential gaps</button>
      {busy && <Loading text="Evaluating coverage across the selected papers…" />}
      {gaps && !gaps.length && <p className="text-sm text-slate2">No evidence-backed gaps were found in this collection.</p>}
      {gaps?.map((g, i) => (
        <article key={i} className="card space-y-2">
          <h2 className="text-lg">{g.dimension}: {g.gap}</h2>
          <p className="text-sm"><b>Possible direction:</b> {g.possible_direction}</p>
          <p className="text-sm"><b>Confidence:</b> {g.confidence}</p>
          <ul className="flex flex-wrap gap-2">
            {g.evidence.map((e, j) => (
              <li key={j}><a className="rounded bg-note px-2 py-1 text-xs text-noteink" target="_blank" rel="noreferrer" href={pdfUrl(e.paper_id, e.page_start)}>{e.paper_title} · {pages(e.page_start, e.page_end)}</a></li>
            ))}
          </ul>
          <p className="text-xs italic text-slate2">{g.qualification}</p>
        </article>
      ))}
    </div>
  );
}
