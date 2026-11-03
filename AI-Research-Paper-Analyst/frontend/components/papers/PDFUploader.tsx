"use client";
import { useRef, useState } from "react";
import { uploadPapers } from "@/lib/api";
import { ErrorMessage } from "../common/Status";

export default function PDFUploader({ workspaceId, onDone }: { workspaceId: string; onDone: () => void }) {
  const ref = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function send(files: FileList | null) {
    if (!files?.length) return;
    setBusy(true); setErr(null);
    try { await uploadPapers(Array.from(files), workspaceId); onDone(); }
    catch (e) { setErr((e as Error).message); }
    finally { setBusy(false); if (ref.current) ref.current.value = ""; }
  }
  return (
    <div className="card border-dashed">
      <label className="mb-2 block text-sm font-medium" htmlFor="pdfs">Upload research papers (PDF)</label>
      <input id="pdfs" ref={ref} type="file" accept="application/pdf" multiple disabled={busy}
        onChange={(e) => send(e.target.files)} className="block text-sm" />
      {busy && <p className="mt-2 text-sm text-slate2">Uploading…</p>}
      <ErrorMessage message={err} />
    </div>
  );
}
