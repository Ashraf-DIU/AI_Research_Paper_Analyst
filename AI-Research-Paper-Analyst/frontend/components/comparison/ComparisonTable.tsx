import type { CompareResult } from "@/types";

export default function ComparisonTable({ data }: { data: CompareResult }) {
  return (
    <div className="space-y-4">
      {data.summary && <p className="card whitespace-pre-wrap text-sm leading-relaxed">{data.summary}</p>}
      <div className="overflow-x-auto">
        <table className="w-full min-w-[640px] border-collapse bg-white text-sm">
          <thead>
            <tr><th className="border border-rule p-2 text-left">Dimension</th>
              {data.papers.map((p) => <th key={p.id} className="border border-rule p-2 text-left font-serif">{p.title}</th>)}</tr>
          </thead>
          <tbody>
            {data.rows.map((r) => (
              <tr key={r.dimension} className="align-top">
                <th scope="row" className="border border-rule p-2 text-left font-medium">{r.dimension}</th>
                {r.cells.map((c) => (
                  <td key={c.paper_id} className="border border-rule p-2">
                    {c.reported ? <ul className="space-y-1">{c.values.map((v, i) => <li key={i}>{v.value}{v.page ? <span className="ml-1 text-xs text-noteink">p.{v.page}</span> : null}</li>)}</ul>
                      : <span className="text-slate2 italic">Not reported in extracted text</span>}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
