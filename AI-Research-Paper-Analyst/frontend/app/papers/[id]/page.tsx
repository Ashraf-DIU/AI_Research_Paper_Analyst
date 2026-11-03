"use client";
import { use, useEffect, useState } from "react";
import { ErrorMessage, Loading } from "@/components/common/Status";
import { analyzePaper, getPaper, pdfUrl } from "@/lib/api";
import type { Analysis, Finding } from "@/types";

const FIELDS: [keyof Analysis, string][] = [
  ["research_objective", "Objective"], ["methodology", "Methodology"], ["datasets", "Datasets"], ["models", "Models"],
  ["evaluation_metrics", "Evaluation metrics"], ["key_results", "Key results"], ["limitations", "Limitations"], ["future_work", "Future work"],
];

function FindingView({ id, f }: { id: string; f: Finding }) {
  return (
    <li className="mb-2">
      {f.value}
      {f.page && <a className="ml-2 rounded bg-note px-1.5 py-0.5 text-xs text-noteink" target="_blank" rel="noreferrer" href={pdfUrl(id, f.page)}>p.{f.page}</a>}
      {f.evidence && <blockquote className="mt-1 border-l-2 border-rule pl-3 text-xs text-slate2">“{f.evidence}” {f.verified ? "" : "(quote not verified)"}</blockquote>}
    </li>
  );
}

export default function PaperDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [paper, setPaper] = useState<Awaited<ReturnType<typeof getPaper>> | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => { getPaper(id).then(setPaper).catch((e) => setErr(e.message)); }, [id]);

  async function run() {
    setBusy(true); setErr(null);
    try { const a = await analyzePaper(id); setPaper((p) => (p ? { ...p, analysis: a } : p)); }
    catch (e) { setErr((e as Error).message); } finally { setBusy(false); }
  }
  if (!paper) return err ? <ErrorMessage message={err} /> : <Loading text="Loading…" />;
  const a = paper.analysis;
  return (
    <div className="space-y-4">
      <h1 className="text-3xl">{paper.title || paper.filename}</h1>
      <p className="text-sm text-slate2">{paper.num_pages} pages · {paper.chunk_count} chunks · {paper.status} · <a className="underline" href={pdfUrl(id)} target="_blank" rel="noreferrer">open PDF</a></p>
      <ErrorMessage message={err} />
      <button className="btn" onClick={run} disabled={busy || paper.status !== "ready"}>{a ? "Re-run analysis" : "Analyze paper"}</button>
      {busy && <Loading text="Extracting structured information… this can take up to a minute." />}
      {a && FIELDS.map(([key, label]) => {
        const v = a[key] as Finding | Finding[] | null;
        const items = Array.isArray(v) ? v : v ? [v] : [];
        return (
          <section key={key} className="card">
            <h2 className="mb-2 text-lg">{label}</h2>
            {items.length ? <ul>{items.map((f, i) => <FindingView key={i} id={id} f={f} />)}</ul> : <p className="text-sm italic text-slate2">Not reported in extracted text</p>}
          </section>
        );
      })}
    </div>
  );
}
