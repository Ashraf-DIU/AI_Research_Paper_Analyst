"use client";
import { useCallback, useEffect, useState } from "react";
import { listPapers } from "./api";
import type { Paper } from "@/types";

/** Loads papers for a workspace and polls every 3s while any paper is still processing. */
export function usePapers(workspaceId: string | null) {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [error, setError] = useState<string | null>(null);
  const refresh = useCallback(async () => {
    if (!workspaceId) return;
    try { setPapers(await listPapers(workspaceId)); setError(null); }
    catch (e) { setError((e as Error).message); }
  }, [workspaceId]);
  useEffect(() => { refresh(); }, [refresh]);
  useEffect(() => {
    if (!papers.some((p) => p.status === "processing")) return;
    const t = setInterval(refresh, 3000);
    return () => clearInterval(t);
  }, [papers, refresh]);
  return { papers, error, refresh };
}
