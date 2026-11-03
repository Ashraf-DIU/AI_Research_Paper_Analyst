import Link from "next/link";
import type { Paper } from "@/types";

const tone = { ready: "bg-emerald-50 text-emerald-800", processing: "bg-amber-50 text-amber-800", failed: "bg-red-50 text-red-800" };

export default function PaperCard({ paper, onDelete }: { paper: Paper; onDelete: (id: string) => void }) {
  return (
    <div className="card flex items-start justify-between gap-4">
      <div className="min-w-0">
        <Link href={`/papers/${paper.id}`} className="font-serif text-lg leading-snug hover:underline">
          {paper.title || paper.filename}
        </Link>
        <p className="mt-1 truncate text-xs text-slate2">{paper.filename}{paper.num_pages ? ` · ${paper.num_pages} pages` : ""}</p>
        {paper.error_message && <p className="mt-1 text-xs text-red-700">{paper.error_message}</p>}
      </div>
      <div className="flex shrink-0 flex-col items-end gap-2">
        <span className={`rounded px-2 py-0.5 text-xs ${tone[paper.status]}`}>{paper.status}</span>
        <button className="text-xs text-slate2 underline" onClick={() => confirm("Delete this paper?") && onDelete(paper.id)}>Delete</button>
      </div>
    </div>
  );
}
