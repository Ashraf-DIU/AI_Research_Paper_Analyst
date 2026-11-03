"use client";
import { ErrorMessage, Loading } from "@/components/common/Status";
import PDFUploader from "@/components/papers/PDFUploader";
import PaperCard from "@/components/papers/PaperCard";
import { deletePaper } from "@/lib/api";
import { usePapers } from "@/lib/usePapers";
import { useWorkspace } from "@/lib/useWorkspace";

export default function Papers() {
  const { workspaceId, error } = useWorkspace();
  const { papers, refresh, error: e2 } = usePapers(workspaceId);
  return (
    <div className="space-y-4">
      <h1 className="text-3xl">Papers</h1>
      <ErrorMessage message={error || e2} />
      {workspaceId ? <PDFUploader workspaceId={workspaceId} onDone={refresh} /> : !error && <Loading text="Connecting to backend…" />}
      <div className="space-y-3">
        {papers.map((p) => <PaperCard key={p.id} paper={p} onDelete={async (id) => { await deletePaper(id); refresh(); }} />)}
      </div>
    </div>
  );
}
