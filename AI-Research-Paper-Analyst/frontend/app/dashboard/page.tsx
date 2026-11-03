"use client";
import Link from "next/link";
import { ErrorMessage, Loading } from "@/components/common/Status";
import { useWorkspace } from "@/lib/useWorkspace";
import { usePapers } from "@/lib/usePapers";

export default function Dashboard() {
  const { workspaceId, error } = useWorkspace();
  const { papers } = usePapers(workspaceId);
  const ready = papers.filter((p) => p.status === "ready").length;
  const steps = [["/papers", "Upload papers", "PDFs are parsed page by page and indexed."],
    ["/chat", "Ask questions", "Answers carry paper and page citations."],
    ["/compare", "Compare", "Methods, datasets, metrics and limitations side by side."],
    ["/research-gaps", "Find gaps", "Evidence-backed, never invented."],
    ["/literature-review", "Draft a review", "Cited sections with a verified reference list."]];
  return (
    <div>
      <h1 className="mb-1 text-3xl">Your research collection</h1>
      <p className="mb-6 text-slate2">Every claim links back to a page of a paper you uploaded.</p>
      <ErrorMessage message={error} />
      {!workspaceId && !error && <Loading text="Connecting to backend… (a sleeping server can take ~1 minute)" />}
      <p className="mb-6 font-serif text-xl">{papers.length} papers · {ready} ready</p>
      <ul className="grid gap-3 sm:grid-cols-2">
        {steps.map(([href, t, d]) => (
          <li key={href}><Link href={href} className="card block hover:border-accent"><span className="font-serif text-lg">{t}</span><span className="block text-sm text-slate2">{d}</span></Link></li>
        ))}
      </ul>
    </div>
  );
}
