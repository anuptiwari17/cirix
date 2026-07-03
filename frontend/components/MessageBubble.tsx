import type { ChatMessage } from "@/types";

export default function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-2xl rounded-sm px-4 py-2.5 text-sm ${
          isUser
            ? "bg-accent text-bg font-mono"
            : "bg-surface border border-border"
        }`}
      >
        {isUser ? (
          message.content
        ) : (
          <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
        )}
      </div>
    </div>
  );
}