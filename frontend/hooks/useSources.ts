"use client";

import { useState, useEffect, useCallback } from "react";
import type { SourceInfo } from "@/types";
import {
  listSources,
  uploadPdf,
  uploadWebsite,
  uploadYoutube,
  deleteSource,
  startNewSession,
} from "@/services/api";

export function useSources() {
  const [sources, setSources] = useState<SourceInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const data = await listSources();
      setSources(data);
    } catch {
      setError("Failed to load sources.");
    }
  }, []);

  useEffect(() => {
  // eslint-disable-next-line react-hooks/set-state-in-effect -- standard fetch-on-mount pattern, setState happens after await, not synchronously
  refresh();
}, [refresh]);

  const addPdf = async (file: File) => {
    setLoading(true);
    setError(null);
    try {
      await uploadPdf(file);
      await refresh();
    } catch {
      setError("Failed to process PDF.");
    } finally {
      setLoading(false);
    }
  };

  const addWebsite = async (url: string) => {
    setLoading(true);
    setError(null);
    try {
      await uploadWebsite(url);
      await refresh();
    } catch {
      setError("Failed to process website.");
    } finally {
      setLoading(false);
    }
  };

  const addYoutube = async (url: string) => {
    setLoading(true);
    setError(null);
    try {
      await uploadYoutube(url);
      await refresh();
    } catch {
      setError("Failed to process YouTube video. It may not have captions.");
    } finally {
      setLoading(false);
    }
  };

  const remove = async (sourceId: string) => {
    await deleteSource(sourceId);
    await refresh();
  };

  const reset = async () => {
    await startNewSession();
    await refresh();
  };

  return { sources, loading, error, addPdf, addWebsite, addYoutube, remove, reset };
}