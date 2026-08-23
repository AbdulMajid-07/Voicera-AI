import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { cloneVoice, deleteVoice, getVoices, updateVoice } from "../api.js";
import { BrandMark } from "../components/icons.jsx";

export default function Admin() {
  const [voices, setVoices] = useState([]);
  const [name, setName] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [editingName, setEditingName] = useState("");

  async function refresh() {
    try {
      setVoices(await getVoices());
    } catch (err) {
      setNotice({ kind: "error", text: `Could not load voices: ${err.message}` });
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function onSubmit(event) {
    event.preventDefault();
    if (!name.trim() || !file) {
      setNotice({ kind: "error", text: "Provide an internal name and a reference audio file." });
      return;
    }
    setBusy(true);
    setNotice(null);
    try {
      const voice = await cloneVoice({ name: name.trim(), displayName: displayName.trim(), file });
      setNotice({ kind: "ok", text: `Cloned "${voice.display_name}" — refresh the landing page to try it.` });
      setName("");
      setDisplayName("");
      setFile(null);
      event.target.reset();
      await refresh();
    } catch (err) {
      setNotice({ kind: "error", text: err.message });
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(voiceId, displayName) {
    if (!confirm(`Delete voice "${displayName}"? This cannot be undone.`)) return;
    setNotice(null);
    try {
      await deleteVoice(voiceId);
      setNotice({ kind: "ok", text: `Deleted "${displayName}".` });
      await refresh();
    } catch (err) {
      setNotice({ kind: "error", text: err.message });
    }
  }

  function startEditing(voice) {
    setEditingId(voice.id);
    setEditingName(voice.display_name);
  }

  function cancelEditing() {
    setEditingId(null);
    setEditingName("");
  }

  async function saveEditing(voiceId) {
    if (!editingName.trim()) return;
    setNotice(null);
    try {
      await updateVoice(voiceId, editingName.trim());
      setNotice({ kind: "ok", text: "Display name updated." });
      setEditingId(null);
      setEditingName("");
      await refresh();
    } catch (err) {
      setNotice({ kind: "error", text: err.message });
    }
  }

  return (
    <div className="admin">
      <header className="admin-header">
        <div className="admin-header-inner">
          <Link className="brand" to="/">
            <BrandMark />
            Voicera <span className="admin-tag">Voice admin</span>
          </Link>
          <Link className="chip" to="/">
            ← Back to site
          </Link>
        </div>
      </header>

      <main className="admin-main">
        <section className="admin-card">
          <h2>Clone a new voice</h2>
          <p className="admin-note">
            Upload 20–30 seconds of clean speech (single speaker, no background noise). WAV or MP3.
          </p>

          <form onSubmit={onSubmit} className="admin-form">
            <label>
              Internal name
              <input
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="e.g. monica"
                autoComplete="off"
              />
            </label>

            <label>
              Display name <span className="admin-opt">(optional — shown to users)</span>
              <input
                type="text"
                value={displayName}
                onChange={(event) => setDisplayName(event.target.value)}
                placeholder="e.g. Monica"
                autoComplete="off"
              />
            </label>

            <label>
              Reference audio
              <input
                type="file"
                accept=".wav,.mp3"
                onChange={(event) => setFile(event.target.files[0])}
              />
            </label>

            <button type="submit" className="btn btn-primary" disabled={busy}>
              {busy ? "Cloning…" : "Clone voice"}
            </button>
          </form>

          {notice && <p className={`admin-notice admin-notice--${notice.kind}`}>{notice.text}</p>}
        </section>

        <section className="admin-card">
          <h2>Voices</h2>
          {voices.length === 0 ? (
            <p className="admin-note">No voices yet. Clone one above or start the backend seed.</p>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Display name</th>
                  <th>Source</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {voices.map((voice) => (
                  <tr key={voice.id}>
                    <td><code>{voice.id}</code></td>
                    <td>
                      {editingId === voice.id ? (
                        <span className="admin-inline-edit">
                          <input
                            type="text"
                            value={editingName}
                            onChange={(e) => setEditingName(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") saveEditing(voice.id);
                              if (e.key === "Escape") cancelEditing();
                            }}
                            autoFocus
                          />
                          <button className="admin-action admin-action--save" onClick={() => saveEditing(voice.id)}>Save</button>
                          <button className="admin-action admin-action--cancel" onClick={cancelEditing}>Cancel</button>
                        </span>
                      ) : (
                        voice.display_name
                      )}
                    </td>
                    <td>{voice.source}</td>
                    <td>
                      {editingId !== voice.id && (
                        <span className="admin-actions">
                          <button className="admin-action admin-action--edit" onClick={() => startEditing(voice)}>Rename</button>
                          <button className="admin-action admin-action--delete" onClick={() => handleDelete(voice.id, voice.display_name)}>Delete</button>
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </main>
    </div>
  );
}
