import { useEffect, useRef, useState } from "react";
import { chatStream, getVoices, synthesize, transcribe } from "../api.js";
import { MicIcon, UserIcon } from "./icons.jsx";

const GREETING = "Heyy. How can I help you?";
const VAD_THRESHOLD = 0.03;
const SILENCE_DURATION_MS = 1500;
const IDLE_TIMEOUT_MS = 20000;
const IDLE_PROMPT_TIMEOUT_MS = 12000;
const IDLE_PROMPT_TEXT = "Still there? Let me know if you have another question.";

export default function IndustryWidget({ industry, isActive, onActivate, tone }) {
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState("");
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [busy, setBusy] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [toast, setToast] = useState(null);

  const chatRef = useRef(null);
  const recorderRef = useRef(null);
  const chunksRef = useRef([]);
  const audioRef = useRef(null);
  const busyRef = useRef(false);
  const abortRef = useRef(null);
  const audioQueueRef = useRef([]);
  const audioQueueBusyRef = useRef(false);
  const voiceIdRef = useRef(null);
  const autoRecordRef = useRef(false);
  const recordingStartRef = useRef(0);
  const _tRef = useRef({});
  const streamRef = useRef(null);
  const audioCtxRef = useRef(null);
  const analyserRef = useRef(null);
  const vadIntervalRef = useRef(null);
  const silenceStartRef = useRef(0);
  const isRecordingRef = useRef(false);
  const isMonitoringRef = useRef(false);
  const idleTimerRef = useRef(null);
  const idlePromptTimerRef = useRef(null);

  useEffect(() => {
    const chat = chatRef.current;
    if (chat) chat.scrollTop = chat.scrollHeight;
  }, [messages]);

  useEffect(() => {
    return () => {
      if (abortRef.current) abortRef.current.abort();
      if (vadIntervalRef.current) clearInterval(vadIntervalRef.current);
      if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
      if (idlePromptTimerRef.current) clearTimeout(idlePromptTimerRef.current);
      if (streamRef.current) streamRef.current.getTracks().forEach((t) => t.stop());
      if (audioCtxRef.current) audioCtxRef.current.close().catch(() => {});
      stopAudio();
      audioQueueRef.current = [];
      audioQueueBusyRef.current = false;
    };
  }, []);

  function showToast(msg) {
    setToast(msg);
    window.clearTimeout(showToast._t);
    showToast._t = window.setTimeout(() => setToast(null), 4000);
  }

  function stopAudio() {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setSpeaking(false);
  }

  function stopRecording() {
    const rec = recorderRef.current;
    if (rec && rec.state !== "inactive") rec.stop();
  }

  function fullReset() {
    if (abortRef.current) abortRef.current.abort();
    if (vadIntervalRef.current) { clearInterval(vadIntervalRef.current); vadIntervalRef.current = null; }
    if (idleTimerRef.current) { clearTimeout(idleTimerRef.current); idleTimerRef.current = null; }
    if (idlePromptTimerRef.current) { clearTimeout(idlePromptTimerRef.current); idlePromptTimerRef.current = null; }
    if (streamRef.current) { streamRef.current.getTracks().forEach((t) => t.stop()); streamRef.current = null; }
    if (audioCtxRef.current) { audioCtxRef.current.close().catch(() => {}); audioCtxRef.current = null; }
    analyserRef.current = null;
    isRecordingRef.current = false;
    isMonitoringRef.current = false;
    silenceStartRef.current = 0;
    stopRecording();
    stopAudio();
    audioQueueRef.current = [];
    audioQueueBusyRef.current = false;
    autoRecordRef.current = false;
    busyRef.current = false;
    setMessages([]);
    setListening(false);
    setSpeaking(false);
    setBusy(false);
    setTranscribing(false);
    setThinking(false);
    setStatus("");
  }

  // ── Audio queue ─────────────────────────────────────────────────────────

  function playBase64Wav(b64) {
    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    const blob = new Blob([bytes], { type: "audio/wav" });
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audioRef.current = audio;
    audio.onended = () => {
      URL.revokeObjectURL(url);
      audioRef.current = null;
      audioQueueBusyRef.current = false;
      playNextAudio();
    };
    audio.onerror = () => {
      URL.revokeObjectURL(url);
      audioRef.current = null;
      audioQueueBusyRef.current = false;
      playNextAudio();
    };
    audio.play().then(() => {
      const tPlay = (performance.now() - _tRef.current.t0).toFixed(0);
      console.log(`[TIMING] audio playback started: ${tPlay} ms from recording stopped`);
      if (_tRef.current.t0) {
        const total = (performance.now() - _tRef.current.t0).toFixed(0);
        console.log(`[TIMING] ── TOTAL recording-stopped → audio-playing: ${total} ms ──`);
      }
    }).catch(() => {
      URL.revokeObjectURL(url);
      audioRef.current = null;
      setSpeaking(false);
      audioQueueBusyRef.current = false;
      playNextAudio();
    });
    setSpeaking(true);
  }

  function playGreetingBlob(blob) {
    return new Promise((resolve) => {
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audioRef.current = audio;
      audio.onended = () => {
        URL.revokeObjectURL(url);
        audioRef.current = null;
        setSpeaking(false);
        resolve();
      };
      audio.onerror = () => {
        URL.revokeObjectURL(url);
        audioRef.current = null;
        setSpeaking(false);
        resolve();
      };
      audio.play().catch(() => {
        URL.revokeObjectURL(url);
        audioRef.current = null;
        setSpeaking(false);
        resolve();
      });
      setSpeaking(true);
    });
  }

  function playNextAudio() {
    if (audioQueueRef.current.length === 0) {
      setSpeaking(false);
      setStatus("");
      if (autoRecordRef.current && !busyRef.current) {
        autoRecordRef.current = false;
        startVadLoop();
      }
      return;
    }
    if (audioQueueBusyRef.current) return;
    audioQueueBusyRef.current = true;
    playBase64Wav(audioQueueRef.current.shift());
  }

  function queueAudio(b64) {
    audioQueueRef.current.push(b64);
    if (!audioQueueBusyRef.current) playNextAudio();
  }

  function pickRandomVoiceId(voices) {
    if (!voices || voices.length === 0) return null;
    return voices[Math.floor(Math.random() * voices.length)].id;
  }

  // ── Streaming chat ──────────────────────────────────────────────────────

  async function sendAndPlay(text) {
    if (busyRef.current) return;
    busyRef.current = true;
    setBusy(true);
    setThinking(true);
    setStatus("");

    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      console.log("[TIMING] chat-stream started");
      const tChatStart = performance.now();
      let firstEventDone = false;
      let audioReceived = false;

      const events = await chatStream(
        {
          message: text,
          history: messages.map((m) => ({
            role: m.role === "ai" ? "assistant" : "user",
            content: m.text,
          })),
          voiceId: voiceIdRef.current,
          language: "en",
          industry,
        },
        controller.signal,
      );

      let replyText = "";
      let streamingIdx = -1;

      for await (const event of events) {
        if (controller.signal.aborted) break;

        if (event.type === "token") {
          if (!firstEventDone) {
            firstEventDone = true;
            const tFirst = (performance.now() - tChatStart).toFixed(0);
            console.log(`[TIMING] chat-stream first event: ${tFirst} ms`);
          }
          replyText += event.text;
          setMessages((prev) => {
            const updated = [...prev];
            if (streamingIdx === -1) {
              streamingIdx = updated.length;
              updated.push({ role: "ai", text: event.text });
            } else {
              updated[streamingIdx] = {
                ...updated[streamingIdx],
                text: replyText.trim(),
              };
            }
            return updated;
          });
        } else if (event.type === "audio") {
          if (!audioReceived) {
            audioReceived = true;
            const tAudio = (performance.now() - _tRef.current.t0).toFixed(0);
            console.log(`[TIMING] audio received: ${tAudio} ms from recording stopped`);
          }
          queueAudio(event.data);
        } else if (event.type === "done") {
          if (streamingIdx !== -1 && event.reply) {
            setMessages((prev) => {
              const updated = [...prev];
              updated[streamingIdx] = {
                ...updated[streamingIdx],
                text: event.reply,
              };
              return updated;
            });
          }
        } else if (event.type === "error") {
          throw new Error(event.detail);
        }
      }
    } catch (err) {
      if (err.name === "AbortError") return;
      showToast("Something went wrong. Please try again.");
    } finally {
      if (!controller.signal.aborted) {
        busyRef.current = false;
        setBusy(false);
        setThinking(false);
      }
    }
  }

  // ── Start / Stop ────────────────────────────────────────────────────────

  async function handleToggle() {
    if (isActive) {
      fullReset();
      onActivate(null);
      return;
    }

    fullReset();
    onActivate(industry);

    const stream = await initStream();
    if (!stream) {
      onActivate(null);
      return;
    }

    let voices;
    try {
      voices = await getVoices();
    } catch (err) {
      showToast(`Could not load voices: ${err.message}`);
      return;
    }
    if (!voices || !voices.length) {
      showToast("No voices available. Clone one at /admin first.");
      return;
    }

    voiceIdRef.current = pickRandomVoiceId(voices);

    setMessages([{ role: "ai", text: GREETING }]);
    setBusy(true);
    setStatus("");

    try {
      const blob = await synthesize({
        text: GREETING,
        voiceId: voiceIdRef.current,
        language: "en",
      });
      await playGreetingBlob(blob);
    } catch (err) {
      showToast(`Greeting failed: ${err.message}`);
      setBusy(false);
      return;
    }

    setBusy(false);
    autoRecordRef.current = true;
    startVadLoop();
  }

  // ── VAD + microphone ────────────────────────────────────────────────────

  function clearIdleTimers() {
    if (idleTimerRef.current) { clearTimeout(idleTimerRef.current); idleTimerRef.current = null; }
    if (idlePromptTimerRef.current) { clearTimeout(idlePromptTimerRef.current); idlePromptTimerRef.current = null; }
  }

  function stopVadLoop() {
    if (vadIntervalRef.current) { clearInterval(vadIntervalRef.current); vadIntervalRef.current = null; }
    isMonitoringRef.current = false;
    silenceStartRef.current = 0;
    clearIdleTimers();
  }

  async function initStream() {
    if (streamRef.current) return streamRef.current;
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      showToast("Microphone is not supported in this browser.");
      return null;
    }
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      showToast("Microphone access denied. Allow it in your browser settings.");
      return null;
    }
    streamRef.current = stream;

    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    audioCtxRef.current = audioCtx;
    const source = audioCtx.createMediaStreamSource(stream);
    const analyser = audioCtx.createAnalyser();
    analyser.fftSize = 512;
    source.connect(analyser);
    analyserRef.current = analyser;

    return stream;
  }

  function startVadLoop(silent) {
    if (vadIntervalRef.current || !analyserRef.current) return;
    isMonitoringRef.current = true;
    silenceStartRef.current = 0;
    clearIdleTimers();

    if (!silent) {
      setListening(true);
      setStatus("Listening...");
    }

    const dataArray = new Float32Array(analyserRef.current.fftSize);

    vadIntervalRef.current = setInterval(() => {
      if (!isMonitoringRef.current) return;

      analyserRef.current.getFloatTimeDomainData(dataArray);
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) sum += dataArray[i] * dataArray[i];
      const rms = Math.sqrt(sum / dataArray.length);

      if (!isRecordingRef.current && !busyRef.current) {
        if (rms > VAD_THRESHOLD) {
          clearIdleTimers();
          setListening(true);
          setStatus("Listening...");
          beginRecording();
        }
      } else if (isRecordingRef.current) {
        if (rms < VAD_THRESHOLD) {
          if (silenceStartRef.current === 0) {
            silenceStartRef.current = performance.now();
          } else if (performance.now() - silenceStartRef.current >= SILENCE_DURATION_MS) {
            stopRecording();
          }
        } else {
          silenceStartRef.current = 0;
        }
      }
    }, 100);

    idleTimerRef.current = setTimeout(() => {
      if (!isMonitoringRef.current) return;
      setStatus(IDLE_PROMPT_TEXT);
      idlePromptTimerRef.current = setTimeout(() => {
        if (!isMonitoringRef.current) return;
        setStatus("");
      }, IDLE_PROMPT_TIMEOUT_MS);
    }, IDLE_TIMEOUT_MS);
  }

  function beginRecording() {
    if (!streamRef.current || isRecordingRef.current) return;
    isRecordingRef.current = true;
    silenceStartRef.current = 0;

    const recorder = new MediaRecorder(streamRef.current);
    chunksRef.current = [];

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    recorder.onstop = async () => {
      isRecordingRef.current = false;
      busyRef.current = true;
      const blob = new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" });
      setListening(false);

      const durationMs = (performance.now() - recordingStartRef.current).toFixed(0);
      console.log(`[TIMING] recording duration: ${durationMs} ms`);
      console.log(`[TIMING] recording MIME: ${recorder.mimeType || "audio/webm"}`);
      console.log(`[TIMING] recording size: ${(blob.size / 1024).toFixed(1)} KB`);
      _tRef.current = { t0: performance.now() };

      if (blob.size === 0) {
        busyRef.current = false;
        restartVadAfterProcessing();
        return;
      }

      setBusy(true);
      setTranscribing(true);
      try {
        console.log("[TIMING] transcribe upload started");
        const text = await transcribe(blob);
        const tTranscribe = (performance.now() - _tRef.current.t0).toFixed(0);
        console.log(`[TIMING] transcribe response: ${tTranscribe} ms`);
        _tRef.current.tTranscribeDone = performance.now();

        if (text) {
          setMessages((prev) => [...prev, { role: "user", text }]);
          autoRecordRef.current = true;
          busyRef.current = false;
          await sendAndPlay(text);
        } else {
          busyRef.current = false;
          restartVadAfterProcessing();
        }
      } catch (err) {
        busyRef.current = false;
        showToast(err.message);
        restartVadAfterProcessing();
      } finally {
        setBusy(false);
        setTranscribing(false);
      }
    };

    recorderRef.current = recorder;
    recordingStartRef.current = performance.now();
    recorder.start();
  }

  function restartVadAfterProcessing() {
    setListening(false);
    setStatus("");
    setTimeout(() => {
      if (streamRef.current && streamRef.current.active) {
        startVadLoop();
      }
    }, 300);
  }

  // ── Render ──────────────────────────────────────────────────────────────

  const industryLabels = {
    hospital: "Hospital",
    enterprise: "Enterprises",
    store: "Store",
  };

  const isConnected = isActive;

  return (
    <div className={`demo-card ${tone || "blue"}${isConnected ? " active-card" : ""}`}>
      <div className="demo-card-top">
        {industry === "hospital" && (
          <svg className="icon-hospital" viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path
              d="M20 8C20 6.89543 20.8954 6 22 6H30C31.1046 6 32 6.89543 32 8V20H44C45.1046 20 46 20.8954 46 22V30C46 31.1046 45.1046 32 44 32H32V44C32 45.1046 31.1046 46 30 46H22C20.8954 46 20 45.1046 20 44V32H8C6.89543 32 6 31.1046 6 30V22C6 20.8954 6.89543 20 8 20H20V8Z"
              stroke="#B8FFF0"
              strokeWidth="4"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
        {industry === "enterprise" && (
          <svg className="icon-standalone" viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path
              d="M8 48H44M12 48V18H40V48M18 18V12H34V18M22 24H30M22 30H30M22 36H26"
              stroke="#B8FFF0"
              strokeWidth="4"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
        {industry === "store" && (
          <svg className="icon-standalone" viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path
              d="M8 20L12 8H40L44 20M8 20H44V44C44 45.1046 43.1046 46 42 46H10C8.89543 46 8 45.1046 8 44V20Z"
              stroke="#B8FFF0"
              strokeWidth="4"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M20 46V32H32V46"
              stroke="#B8FFF0"
              strokeWidth="4"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
        <h3>{industryLabels[industry]}</h3>
        <p>
          {industry === "hospital" && "Book appointments, verify insurance, answer timing questions."}
          {industry === "enterprise" && "Route callers, take messages, never put anyone on hold."}
          {industry === "store" && "Answer stock, hours, and order queries after closing time."}
        </p>
      </div>

      <button
        type="button"
        className={`card-cta${isConnected ? " card-cta--active" : ""}`}
        onClick={handleToggle}
      >
        {isConnected ? (
          <span className="card-cta-connected">
            <span className="card-cta-dot" />
            Connected
          </span>
        ) : (
          "Start Speaking"
        )}
      </button>

      {isConnected && (
        <>
          <p className="card-status">
            {listening ? (
              <b>Listening</b>
            ) : transcribing ? (
              "Transcribing..."
            ) : speaking ? (
              <>
                <b>Voicera</b> is speaking...
              </>
            ) : thinking ? (
              <>
                <b>Voicera</b> is thinking...
              </>
            ) : (
              status || "Ask me anything"
            )}
          </p>

          <p className="card-note">
            <b>Voicera</b> {industryLabels[industry]} assistant
          </p>
        </>
      )}

      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}
