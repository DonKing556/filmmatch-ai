import { useState, useCallback, useRef } from "react";

interface SSEState {
  status: "idle" | "connecting" | "streaming" | "done" | "error";
  messages: SSEMessage[];
  error: string | null;
}

interface SSEMessage {
  event: string;
  data: string;
}

export function useSSE() {
  const [state, setState] = useState<SSEState>({
    status: "idle",
    messages: [],
    error: null,
  });
  const sourceRef = useRef<EventSource | null>(null);

  const connect = useCallback((url: string) => {
    // Close any existing connection
    if (sourceRef.current) {
      sourceRef.current.close();
    }

    setState({ status: "connecting", messages: [], error: null });

    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("fm_access_token")
        : null;

    const fullUrl = token ? `${url}?token=${encodeURIComponent(token)}` : url;
    const source = new EventSource(fullUrl);
    sourceRef.current = source;

    source.onopen = () => {
      setState((s) => ({ ...s, status: "streaming" }));
    };

    source.addEventListener("status", (e) => {
      setState((s) => ({
        ...s,
        messages: [...s.messages, { event: "status", data: e.data }],
      }));
    });

    source.addEventListener("candidates", (e) => {
      setState((s) => ({
        ...s,
        messages: [...s.messages, { event: "candidates", data: e.data }],
      }));
    });

    source.addEventListener("result", (e) => {
      setState((s) => ({
        ...s,
        status: "done",
        messages: [...s.messages, { event: "result", data: e.data }],
      }));
      source.close();
    });

    source.addEventListener("error", (e) => {
      const errorEvent = e as MessageEvent;
      setState((s) => ({
        ...s,
        status: "error",
        error: errorEvent.data || "Connection failed",
      }));
      source.close();
    });

    source.onerror = () => {
      setState((s) => ({
        ...s,
        status: "error",
        error: "Connection lost",
      }));
      source.close();
    };
  }, []);

  const disconnect = useCallback(() => {
    if (sourceRef.current) {
      sourceRef.current.close();
      sourceRef.current = null;
    }
    setState({ status: "idle", messages: [], error: null });
  }, []);

  return { ...state, connect, disconnect };
}
