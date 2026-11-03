"use client";
import { useEffect, useState } from "react";
import { listWorkspaces } from "./api";

export function useWorkspace() {
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    listWorkspaces()
      .then((ws) => setWorkspaceId(ws[0]?.id ?? null))
      .catch((e) => setError(`Cannot reach the backend: ${e.message}`));
  }, []);
  return { workspaceId, error };
}
