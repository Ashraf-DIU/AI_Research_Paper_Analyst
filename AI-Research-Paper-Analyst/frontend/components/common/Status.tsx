export function Loading({ text = "Working…" }: { text?: string }) {
  return <p className="text-sm text-slate2" role="status">{text}</p>;
}
export function ErrorMessage({ message }: { message: string | null }) {
  return message ? <p className="my-2 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-800" role="alert">{message}</p> : null;
}
