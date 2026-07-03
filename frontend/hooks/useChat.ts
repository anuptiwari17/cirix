"use client";

import { useState, useRef } from "react";
import type { ChatMessage, Citation } from "@/types";
import { sendChatMessage } from "@/services/api";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [latestCitations, setLatestCitations] = useState<Citation[]>([]);
  const sessionId = useRef(crypto.randomUUID());

  const ask = async (question: string) => {
    if (!question.trim()) return;

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      const response = await sendChatMessage(sessionId.current, question);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.answer, citations: response.citations },
      ]);
      setLatestCitations(response.citations);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Something went wrong reaching the server. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return { messages, loading, latestCitations, ask };
}