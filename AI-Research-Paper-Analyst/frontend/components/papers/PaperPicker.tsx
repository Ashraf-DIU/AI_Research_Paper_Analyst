"use client";
import type { Paper } from "@/types";

export default function PaperPicker({ papers, selected, onChange }: { papers: Paper[]; selected: string[]; onChange: (ids: string[]) => void }) {
  const ready = papers.filter((p) => p.status === "ready");
  if (!ready.length) return <p className="text-sm text-slate2">No processed papers yet. Upload some on the Papers page.</p>;
  return (
    <fieldset className="card">
      <legend className="px-1 text-sm font-medium">Select papers</legend>
      {ready.map((p) => (
        <label key={p.id} className="flex items-start gap-2 py-1 text-sm">
          <input type="checkbox" className="mt-1" checked={selected.includes(p.id)}
            onChange={(e) => onChange(e.target.checked ? [...selected, p.id] : selected.filter((x) => x !== p.id))} />
          <span>{p.title || p.filename}</span>
        </label>
      ))}
    </fieldset>
  );
}
