import axios from "axios";
import type { UploadResponse, SourceInfo, ChatResponse } from "@/types";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

export async function uploadPdf(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<UploadResponse>("/upload/pdf", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function uploadWebsite(url: string): Promise<UploadResponse> {
  const { data } = await api.post<UploadResponse>("/upload/website", { url });
  return data;
}

export async function uploadYoutube(url: string): Promise<UploadResponse> {
  const { data } = await api.post<UploadResponse>("/upload/youtube", { url });
  return data;
}

export async function listSources(): Promise<SourceInfo[]> {
  const { data } = await api.get<SourceInfo[]>("/sources");
  return data;
}

export async function deleteSource(sourceId: string): Promise<void> {
  await api.delete(`/sources/${sourceId}`);
}

export async function startNewSession(): Promise<void> {
  await api.delete("/sources");
}

export async function sendChatMessage(
  sessionId: string,
  question: string
): Promise<ChatResponse> {
  const { data } = await api.post<ChatResponse>("/chat", {
    session_id: sessionId,
    question,
  });
  return data;
}

export default api;