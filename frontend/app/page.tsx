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
      <div className="flex flex-1 overflow-hidden">
        <SourceSidebar
          sources={sources}
          loading={sourcesLoading}
          error={error}
          onAddPdf={addPdf}
          onAddWebsite={addWebsite}
          onAddYoutube={addYoutube}
          onRemove={remove}
          onReset={reset}
        />
        <ChatPanel messages={messages} loading={chatLoading} onSend={ask} />
        <CitationPanel citations={latestCitations} />
      </div>
    </div>
  );
}