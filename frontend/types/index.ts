export interface UploadResponse {
  source_id: string;
  filename: string;
  chunk_count: number;
  message: string;
}

export interface SourceInfo {
  source_id: string;
  type: "pdf" | "website" | "youtube";
  label: string;
}

export interface Citation {
  label: string;
  text: string;
  metadata: Record<string, string | number>;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
}