"use client";

import { useState, useRef, useEffect } from "react";
import type { ChatMessage } from "@/types";
import MessageBubble from "./MessageBubble";

interface Props {
  messages: ChatMessage[];
  loading: boolean;
  onSend: (question: string) => void;
}

export default function ChatPanel({ messages, loading, onSend }: Props) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = () => {
    if (!input.trim() || loading) return;
    onSend(input);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex-1 flex flex-col min-w-0">
      <div className="flex-1 overflow-y-auto p-3 md:p-6 space-y-4">
        {messages.length === 0 && (
          <p className="text-text-dim text-sm font-mono">
            Add a source, then ask a question.
          </p>
        )}
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-surface border border-border rounded-sm px-4 py-2.5 text-sm text-text-dim font-mono">
              thinking...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-border p-3 md:p-4 shrink-0">
        <div className="flex items-center gap-3 max-w-4xl mx-auto">
          <span className="text-accent font-mono">&gt;</span>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="type your question here..."
            disabled={loading}
            className="flex-1 bg-transparent outline-none font-mono text-sm placeholder:text-text-dim disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-4 py-1.5 bg-accent text-bg font-mono text-sm rounded-sm hover:opacity-90 transition-opacity disabled:opacity-40"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}