import type { Citation } from "@/types";

export default function CitationPanel({ citations }: { citations: Citation[] }) {
  return (
    <aside className="w-80 shrink-0 border-l border-border flex flex-col">
      <div className="p-4 border-b border-border">
        <h2 className="font-display font-semibold text-sm tracking-wide text-text-dim uppercase">
          Citations
        </h2>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {citations.length === 0 && (
          <p className="text-text-dim text-sm font-mono">
            Citations will appear here.
          </p>
        )}
        {citations.map((c, i) => (
          <div key={i} className="border border-border rounded-sm p-3">
            <p className="text-xs font-mono text-accent mb-1">[{i + 1}] {c.label}</p>
            <p className="text-xs text-text-dim leading-relaxed">{c.text}...</p>
          </div>
        ))}
      </div>
    </aside>
  );
}