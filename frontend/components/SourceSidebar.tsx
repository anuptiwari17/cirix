"use client";

import { useState } from "react";
import type { SourceInfo } from "@/types";
import SourceUploadModal from "./SourceUploadModal";

interface Props {
  sources: SourceInfo[];
  loading: boolean;
  error: string | null;
  onAddPdf: (file: File) => Promise<void>;
  onAddWebsite: (url: string) => Promise<void>;
  onAddYoutube: (url: string) => Promise<void>;
  onRemove: (sourceId: string) => Promise<void>;
  onReset: () => Promise<void>;
}

const TYPE_ICON: Record<string, string> = {
  pdf: "PDF",
  website: "WEB",
  youtube: "YT",
};

export default function SourceSidebar({
  sources,
  loading,
  error,
  onAddPdf,
  onAddWebsite,
  onAddYoutube,
  onRemove,
  onReset,
}: Props) {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <aside className="w-64 shrink-0 border-r border-border flex flex-col">
      <div className="p-4 border-b border-border flex items-center justify-between">
        <h2 className="font-display font-semibold text-sm tracking-wide text-text-dim uppercase">
          Sources
        </h2>
        <button
          onClick={() => setModalOpen(true)}
          className="text-accent text-sm font-mono hover:opacity-80 transition-opacity"
        >
          + Add
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {error && (
          <p className="text-red-400 text-xs font-mono">{error}</p>
        )}
        {sources.length === 0 && !loading && (
          <p className="text-text-dim text-sm font-mono">No sources yet.</p>
        )}
        {sources.map((source) => (
          <div
            key={source.source_id}
            className="group flex items-center justify-between gap-2 px-2 py-1.5 rounded-sm hover:bg-surface transition-colors"
          >
            <div className="flex items-center gap-2 min-w-0">
              <span className="text-[10px] font-mono text-accent shrink-0">
                {TYPE_ICON[source.type] ?? "?"}
              </span>
              <span className="text-sm truncate" title={source.label}>
                {source.label}
              </span>
            </div>
            <button
              onClick={() => onRemove(source.source_id)}
              className="opacity-0 group-hover:opacity-100 text-text-dim hover:text-red-400 text-xs transition-all shrink-0"
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-border">
        <button
          onClick={onReset}
          className="w-full text-xs font-mono text-text-dim hover:text-accent transition-colors"
        >
          start new session
        </button>
      </div>

      {modalOpen && (
        <SourceUploadModal
          onClose={() => setModalOpen(false)}
          onAddPdf={onAddPdf}
          onAddWebsite={onAddWebsite}
          onAddYoutube={onAddYoutube}
          loading={loading}
        />
      )}
    </aside>
  );
}