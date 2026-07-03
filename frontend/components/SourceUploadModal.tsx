"use client";

import { useState } from "react";

type SourceKind = "pdf" | "website" | "youtube";

interface Props {
  onClose: () => void;
  onAddPdf: (file: File) => Promise<void>;
  onAddWebsite: (url: string) => Promise<void>;
  onAddYoutube: (url: string) => Promise<void>;
  loading: boolean;
}

export default function SourceUploadModal({
  onClose,
  onAddPdf,
  onAddWebsite,
  onAddYoutube,
  loading,
}: Props) {
  const [kind, setKind] = useState<SourceKind>("pdf");
  const [url, setUrl] = useState("");

  const handleSubmit = async () => {
    if (kind === "website") {
      await onAddWebsite(url);
    } else if (kind === "youtube") {
      await onAddYoutube(url);
    }
    if (!loading) onClose();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      await onAddPdf(file);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-surface border border-border rounded-sm w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-display font-semibold text-lg">Add source</h3>
          <button
            onClick={onClose}
            className="text-text-dim hover:text-text transition-colors"
          >
            ✕
          </button>
        </div>

        <div className="flex gap-2 mb-4">
          {(["pdf", "website", "youtube"] as SourceKind[]).map((k) => (
            <button
              key={k}
              onClick={() => setKind(k)}
              className={`px-3 py-1.5 text-xs font-mono rounded-sm border transition-colors ${
                kind === k
                  ? "border-accent text-accent"
                  : "border-border text-text-dim hover:text-text"
              }`}
            >
              {k}
            </button>
          ))}
        </div>

        {kind === "pdf" && (
          <label className="block border border-dashed border-border rounded-sm p-6 text-center cursor-pointer hover:border-accent transition-colors">
            <span className="text-sm text-text-dim font-mono">
              {loading ? "processing..." : "click to choose a PDF"}
            </span>
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              disabled={loading}
              onChange={handleFileChange}
            />
          </label>
        )}

        {(kind === "website" || kind === "youtube") && (
          <div className="flex flex-col gap-3">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder={
                kind === "website"
                  ? "https://example.com/article"
                  : "https://youtube.com/watch?v=..."
              }
              className="bg-bg border border-border rounded-sm px-3 py-2 text-sm font-mono outline-none focus:border-accent transition-colors"
            />
            <button
              onClick={handleSubmit}
              disabled={loading || !url}
              className="bg-accent text-bg font-mono text-sm py-2 rounded-sm hover:opacity-90 transition-opacity disabled:opacity-40"
            >
              {loading ? "processing..." : "add source"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}