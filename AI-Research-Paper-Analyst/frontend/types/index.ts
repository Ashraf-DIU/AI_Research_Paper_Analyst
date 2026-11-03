export type Paper = {
  id: string; workspace_id: string; filename: string; title: string | null; doi: string | null;
  num_pages: number; status: "processing" | "ready" | "failed"; error_message: string | null;
  created_at: string; duplicate?: boolean;
};
export type Finding = { value: string; evidence: string; page: number | null; verified: boolean };
export type Analysis = {
  title: Finding | null; research_objective: Finding | null; methodology: Finding | null;
  datasets: Finding[]; models: Finding[]; evaluation_metrics: Finding[]; key_results: Finding[];
  limitations: Finding[]; future_work: Finding[];
};
export type Citation = {
  label: string; paper_id: string; paper_title: string; filename: string;
  page_start: number; page_end: number; section: string; snippet: string;
};
export type ChatMessage = { role: "user" | "assistant"; content: string; citations?: Citation[]; warning?: string | null };
export type CompareResult = {
  papers: { id: string; title: string }[];
  rows: { dimension: string; cells: { paper_id: string; values: { value: string; page: number | null }[]; reported: boolean }[] }[];
  summary: string | null;
};
export type Gap = {
  dimension: string; gap: string; possible_direction: string; confidence: string; qualification: string;
  evidence: { paper_id: string; paper_title: string; page_start: number; page_end: number; snippet: string }[];
};
