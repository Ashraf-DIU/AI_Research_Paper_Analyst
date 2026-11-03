import type { Analysis, ChatMessage, CompareResult, Gap, Paper } from "@/types";

export const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, init);
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail ?? detail; } catch {}
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return res.json();
}
const post = <T,>(path: string, body: unknown) =>
  req<T>(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });

export const listWorkspaces = () => req<{ id: string; name: string }[]>("/api/workspaces");
export const listPapers = (ws: string) => req<Paper[]>(`/api/papers?workspace_id=${ws}`);
export const getPaper = (id: string) => req<Paper & { analysis: Analysis | null; chunk_count: number }>(`/api/papers/${id}`);
export const deletePaper = (id: string) => req(`/api/papers/${id}`, { method: "DELETE" });
export const analyzePaper = (id: string) => req<Analysis>(`/api/papers/${id}/analyze`, { method: "POST" });
export const pdfUrl = (id: string, page?: number) => `${API_URL}/api/papers/${id}/file${page ? `#page=${page}` : ""}`;

export async function uploadPapers(files: File[], workspaceId: string) {
  const fd = new FormData();
  fd.append("workspace_id", workspaceId);
  files.forEach((f) => fd.append("files", f));
  return req<Paper[]>("/api/papers/upload", { method: "POST", body: fd });
}
export const askQuestion = (question: string, workspace_id: string, conversation_id?: string, paper_ids?: string[]) =>
  post<{ conversation_id: string; answer: string; citations: ChatMessage["citations"]; warning: string | null }>(
    "/api/chat", { question, workspace_id, conversation_id, paper_ids });
export const comparePapers = (workspace_id: string, paper_ids: string[]) => post<CompareResult>("/api/compare", { workspace_id, paper_ids });
export const findGaps = (workspace_id: string, paper_ids: string[]) => post<{ gaps: Gap[] }>("/api/research-gaps", { workspace_id, paper_ids });
export const generateReview = (body: { workspace_id: string; topic: string; paper_ids?: string[]; citation_style: string; word_count: number }) =>
  post<{ markdown: string }>("/api/literature-review", body);
