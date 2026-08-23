// API helpers for the Voicera backend. All calls go to our own server — no
// third-party keys ever touch the browser.

const API_BASE = (import.meta.env.VITE_API_BASE ?? "http://localhost:8000").replace(/\/$/, "");

async function unwrap(res) {
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body);
    } catch {
      /* non-JSON error body */
    }
    throw new Error(detail);
  }
  return res;
}

export async function getVoices() {
  const res = await unwrap(await fetch(`${API_BASE}/voices`));
  return res.json();
}

export async function synthesize({ text, voiceId, language }) {
  const res = await unwrap(
    await fetch(`${API_BASE}/synthesize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, voice_id: voiceId, language }),
    })
  );
  return res.blob();
}

export async function transcribe(file) {
  const form = new FormData();
  form.append("file", file, file.name || "recording.webm");
  const res = await unwrap(await fetch(`${API_BASE}/transcribe`, { method: "POST", body: form }));
  const data = await res.json();
  return data.text;
}

export async function cloneVoice({ name, displayName, file }) {
  const form = new FormData();
  form.append("name", name);
  form.append("display_name", displayName || name);
  form.append("file", file);
  const res = await unwrap(await fetch(`${API_BASE}/clone-voice`, { method: "POST", body: form }));
  return res.json();
}

export async function deleteVoice(voiceId) {
  const res = await unwrap(await fetch(`${API_BASE}/voices/${voiceId}`, { method: "DELETE" }));
  return res.json();
}

export async function updateVoice(voiceId, displayName) {
  const res = await unwrap(
    await fetch(`${API_BASE}/voices/${voiceId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ display_name: displayName }),
    })
  );
  return res.json();
}

// ── Streaming chat ───────────────────────────────────────────────────────────

/**
 * Send a chat message via the streaming /chat-stream endpoint.
 *
 * Returns an async generator that yields NDJSON event objects:
 *   { type: "token", text: "..." }   — partial LLM text
 *   { type: "audio", data: "..." }   — base64 WAV for one sentence
 *   { type: "done",  reply: "..." }  — full reply, stream finished
 *   { type: "error", detail: "..." } — something went wrong
 *
 * Supports abort via AbortController — pass signal to cancel mid-stream.
 */
export async function chatStream({ message, history, voiceId, language, industry }, signal) {
  const res = await fetch(`${API_BASE}/chat-stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      history: history ?? [],
      voice_id: voiceId,
      language,
      industry: industry ?? "general",
    }),
    signal,
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body);
    } catch { /* ignore */ }
    throw new Error(detail);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  async function* events() {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      // Keep the last (potentially incomplete) line in the buffer
      buffer = lines.pop();
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;
        try {
          yield JSON.parse(trimmed);
        } catch {
          // Skip malformed lines
        }
      }
    }
    // Flush remaining buffer
    const remaining = buffer.trim();
    if (remaining) {
      try { yield JSON.parse(remaining); } catch { /* ignore */ }
    }
  }

  return events();
}
