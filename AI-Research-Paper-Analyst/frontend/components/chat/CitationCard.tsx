import { pdfUrl } from "@/lib/api";
import { pages } from "@/lib/utils";
import type { Citation } from "@/types";

export default function CitationCard({ c }: { c: Citation }) {
  return (
    <a href={pdfUrl(c.paper_id, c.page_start)} target="_blank" rel="noreferrer"
       className="block rounded border border-[#ecd9a6] bg-note px-3 py-2 text-xs text-noteink hover:brightness-95">
      <span className="font-semibold">{c.label}</span> · {c.paper_title} · {pages(c.page_start, c.page_end)} · {c.section}
      <span className="mt-1 block text-[11px] opacity-80">{c.snippet.slice(0, 160)}…</span>
    </a>
  );
}
