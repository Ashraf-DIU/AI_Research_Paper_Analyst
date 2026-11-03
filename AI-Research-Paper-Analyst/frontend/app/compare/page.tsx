"use client";
import { useState } from "react";
import ComparisonTable from "@/components/comparison/ComparisonTable";
import { ErrorMessage, Loading } from "@/components/common/Status";
import PaperPicker from "@/components/papers/PaperPicker";
import { comparePapers } from "@/lib/api";
import { usePapers } from "@/lib/usePapers";
import { useWorkspace } from "@/lib/useWorkspace";
import type { CompareResult } from "@/types";

export default function ComparePage() {
  const { workspaceId, error } = useWorkspace();
  const { papers } = usePapers(workspaceId);
  const [sel, setSel] = useState<string[]>([]);
  const [data, setData] = useState<CompareResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  async function run() {
    if (!workspaceId) return;
    setBusy(true); setErr(null);
    try { setData(await comparePapers(workspaceId, sel)); } catch (e) { setErr((e as Error).message); } finally { setBusy(false); }
  }
  return (
    <div className="space-y-4">
      <h1 className="text-3xl">Compare papers</h1>
      <ErrorMessage message={error || err} />
      <PaperPicker papers={papers} selected={sel} onChange={setSel} />
      <button className="btn" disabled={busy || sel.length < 2} onClick={run}>Compare (2–6 papers)</button>
      {busy && <Loading text="Analyzing papers (first run extracts each paper, which takes a while)…" />}
      {data && <ComparisonTable data={data} />}
    </div>
  );
}
