"use client";

import { useState } from "react";
import { useSources } from "@/hooks/useSources";
import { useChat } from "@/hooks/useChat";
import SourceSidebar from "@/components/SourceSidebar";
import ChatPanel from "@/components/ChatPanel";
import CitationPanel from "@/components/CitationPanel";
import WelcomeModal from "@/components/WelcomeModal";

export default function Home() {
  const [sessionStarted, setSessionStarted] = useState(false);
  const [mobileSourcesOpen, setMobileSourcesOpen] = useState(false);
  const [mobileCitationsOpen, setMobileCitationsOpen] = useState(false);

  const { sources, loading: sourcesLoading, error, addPdf, addWebsite, addYoutube, remove, reset } =
    useSources();
  const { messages, loading: chatLoading, latestCitations, ask } = useChat();

  const handleStart = async () => {
    await reset();
    setSessionStarted(true);
  };

  if (!sessionStarted) {
    return <WelcomeModal onStart={handleStart} />;
  }

  return (
    <div className="flex h-screen flex-col">
      {/* Mobile top bar: toggles for sources + citations, hidden on desktop */}
      <div className="flex md:hidden items-center justify-between border-b border-border p-3 shrink-0">
        <button
          onClick={() => setMobileSourcesOpen(true)}
          className="text-xs font-mono text-text-dim hover:text-accent transition-colors"
        >
          ☰ sources ({sources.length})
        </button>
        <span className="font-display font-semibold text-sm">
          <span className="text-accent">Cirix</span>
        </span>
        <button
          onClick={() => setMobileCitationsOpen(true)}
          className="text-xs font-mono text-text-dim hover:text-accent transition-colors"
        >
          citations ({latestCitations.length})
        </button>
      </div>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Sources sidebar: fixed on desktop, slide-out drawer on mobile */}
        <div
          className={`
            fixed md:static inset-y-0 left-0 z-40 md:z-auto
            transform transition-transform duration-200 md:transform-none
            ${mobileSourcesOpen ? "translate-x-0" : "-translate-x-full"} md:translate-x-0
          `}
        >
          <SourceSidebar
            sources={sources}
            loading={sourcesLoading}
            error={error}
            onAddPdf={addPdf}
            onAddWebsite={addWebsite}
            onAddYoutube={addYoutube}
            onRemove={remove}
            onReset={reset}
            onCloseMobile={() => setMobileSourcesOpen(false)}
          />
        </div>
        {mobileSourcesOpen && (
          <div
            className="fixed inset-0 bg-black/50 z-30 md:hidden"
            onClick={() => setMobileSourcesOpen(false)}
          />
        )}

        <ChatPanel
          messages={messages}
          loading={chatLoading}
          hasSources={sources.length > 0}
          onSend={ask}
        />

        {/* Citations panel: fixed on desktop, slide-out drawer on mobile */}
        <div
          className={`
            fixed md:static inset-y-0 right-0 z-40 md:z-auto
            transform transition-transform duration-200 md:transform-none
            ${mobileCitationsOpen ? "translate-x-0" : "translate-x-full"} md:translate-x-0
          `}
        >
          <CitationPanel
            citations={latestCitations}
            onCloseMobile={() => setMobileCitationsOpen(false)}
          />
        </div>
        {mobileCitationsOpen && (
          <div
            className="fixed inset-0 bg-black/50 z-30 md:hidden"
            onClick={() => setMobileCitationsOpen(false)}
          />
        )}
      </div>
    </div>
  );
}