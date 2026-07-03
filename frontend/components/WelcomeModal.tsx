"use client";

import { useState } from "react";

interface Props {
  onStart: () => Promise<void>;
}

export default function WelcomeModal({ onStart }: Props) {
  const [loading, setLoading] = useState(false);

  const handleStart = async () => {
    setLoading(true);
    await onStart();
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 bg-bg flex items-center justify-center z-50">
      <div className="max-w-md text-center px-6">
        <h1 className="font-display font-semibold text-3xl mb-3">
          Welcome to <span className="text-accent">Cirix</span>
        </h1>
        <p className="text-text-dim text-sm font-mono mb-8 leading-relaxed">
          Chat with PDFs, websites, and YouTube videos from one place.
        </p>
        <button
          onClick={handleStart}
          disabled={loading}
          className="px-6 py-2.5 bg-accent text-bg font-mono text-sm rounded-sm hover:opacity-90 transition-opacity disabled:opacity-50"
        >
          {loading ? "starting..." : "start new session"}
        </button>
        <p className="text-text-dim text-xs font-mono mt-4">
          this clears any existing sources first
        </p>
      </div>
    </div>
  );
}