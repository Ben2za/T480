const statusLine = document.querySelector("#statusLine");
const recordBtn = document.querySelector("#recordBtn");
const pauseBtn = document.querySelector("#pauseBtn");
const resumeBtn = document.querySelector("#resumeBtn");
const stopBtn = document.querySelector("#stopBtn");
const replayBtn = document.querySelector("#replayBtn");
const speakBtn = document.querySelector("#speakBtn");
const sendTextBtn = document.querySelector("#sendTextBtn");
const textInput = document.querySelector("#textInput");
const transcriptBox = document.querySelector("#transcript");
const answerBox = document.querySelector("#answer");
const logList = document.querySelector("#log");
const audioPlayer = document.querySelector("#audioPlayer");
const autoSpeak = document.querySelector("#autoSpeak");
const modeButtons = Array.from(document.querySelectorAll("[data-mode]"));
const queueActionBtn = document.querySelector("#queueActionBtn");
const refreshQueueBtn = document.querySelector("#refreshQueueBtn");
const approveActionBtn = document.querySelector("#approveActionBtn");
const rejectActionBtn = document.querySelector("#rejectActionBtn");
const actionList = document.querySelector("#actionList");
const actionPreview = document.querySelector("#actionPreview");
const quickActionButtons = Array.from(document.querySelectorAll("[data-action-text]"));
const codexReviewPanel = document.querySelector("#codexReviewPanel");
const codexReviewMeta = document.querySelector("#codexReviewMeta");
const codexSpec = document.querySelector("#codexSpec");
const codexReviewed = document.querySelector("#codexReviewed");
const revalidateCodexBtn = document.querySelector("#revalidateCodexBtn");
const runCodexBtn = document.querySelector("#runCodexBtn");
const CLIENT_BUILD = "2026-07-19.3";

let mode = "chat";
let stream = null;
let recorder = null;
let chunks = [];
let lastAudioUrl = "";
let lastTtsAudioUrl = "";
let lastAnswer = "";
let lastInputText = "";
let selectedAction = null;
let busy = false;
let codexPreview = null;

function setStatus(text, tone = "") {
  statusLine.textContent = text;
  statusLine.className = tone;
}

function showRequestError(error) {
  const message = String(error && error.message ? error.message : error);
  answerBox.textContent = `Request failed: ${message}`;
  lastAnswer = "";
  speakBtn.disabled = true;
  setStatus(message, "bad");
  log("error", message);
}

function log(role, text) {
  const item = document.createElement("li");
  const label = document.createElement("strong");
  label.textContent = `${role}: `;
  item.append(label, document.createTextNode(text));
  logList.prepend(item);
  while (logList.children.length > 30) {
    logList.lastElementChild.remove();
  }
}

function updateCodexRunButton() {
  runCodexBtn.disabled = busy || !codexPreview || !codexPreview.runnable || !codexReviewed.checked;
  revalidateCodexBtn.disabled = busy || !codexSpec.value.trim() || Boolean(codexPreview);
}

function invalidateCodexPreview(message = "No validated preview.") {
  codexPreview = null;
  codexReviewed.checked = false;
  codexReviewed.disabled = true;
  codexSpec.disabled = true;
  codexReviewMeta.textContent = message;
  codexSpec.value = "";
  updateCodexRunButton();
}

function applyCodexPreview(data) {
  const required = ["preview_id", "spec_sha256", "canonical_spec", "workspace", "approval_class"];
  if (!required.every((key) => typeof data[key] === "string" && data[key])) {
    throw new Error("incomplete Codex preview response");
  }
  codexPreview = {
    previewId: data.preview_id,
    digest: data.spec_sha256,
    canonical: data.canonical_spec,
    workspace: data.workspace,
    approvalClass: data.approval_class,
    expiresAt: data.expires_at || "unknown",
    runnable: data.runnable === true,
  };
  const runState = codexPreview.runnable
    ? "live run enabled"
    : "preview only; live run awaits informed OpenAI disclosure approval";
  codexReviewMeta.textContent = `workspace ${codexPreview.workspace} · ${codexPreview.approvalClass} · sha256 ${codexPreview.digest} · expires ${codexPreview.expiresAt} · ${runState}`;
  codexSpec.value = codexPreview.canonical;
  codexSpec.disabled = false;
  codexReviewed.checked = false;
  codexReviewed.disabled = !codexPreview.runnable;
  updateCodexRunButton();
  codexReviewPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function markCodexSpecEdited() {
  if (!codexPreview) {
    return;
  }
  codexPreview = null;
  codexReviewed.checked = false;
  codexReviewed.disabled = true;
  codexReviewMeta.textContent = "Edited draft is not authorized. Revalidate it before review or execution.";
  updateCodexRunButton();
}

function setBusy(value) {
  busy = value;
  recordBtn.disabled = value || Boolean(recorder);
  sendTextBtn.disabled = value;
  queueActionBtn.disabled = value;
  refreshQueueBtn.disabled = value;
  quickActionButtons.forEach((button) => {
    button.disabled = value;
  });
  modeButtons.forEach((button) => {
    button.disabled = value;
  });
  textInput.disabled = value;
  updateActionButtons();
  updateCodexRunButton();
}

function updateRecordButtons(state) {
  const recording = state === "recording";
  const paused = state === "paused";
  recordBtn.disabled = busy || recording || paused;
  pauseBtn.disabled = !recording;
  resumeBtn.disabled = !paused;
  stopBtn.disabled = !(recording || paused);
}

function activeMode() {
  return mode;
}

function setMode(nextMode) {
  mode = nextMode || "chat";
  invalidateCodexPreview();
  modeButtons.forEach((item) => item.classList.toggle("active", item.dataset.mode === mode));
  codexReviewPanel.hidden = mode !== "codex";
  const labels = {
    chat: "Local chat",
    brief: "CTOS brief",
    codex: "Codex spec preview",
    action: "Action preview",
  };
  setStatus(labels[mode] || "Local chat", "ok");
}

function pickMimeType() {
  if (!window.MediaRecorder) {
    return "";
  }
  const candidates = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/ogg;codecs=opus",
    "audio/ogg",
  ];
  return candidates.find((candidate) => MediaRecorder.isTypeSupported(candidate)) || "";
}

async function ensureMic() {
  if (stream) {
    return stream;
  }
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    throw new Error("microphone API unavailable");
  }
  stream = await navigator.mediaDevices.getUserMedia({
    audio: {
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
    },
  });
  return stream;
}

async function startRecording() {
  try {
    if (activeMode() === "codex") {
      invalidateCodexPreview("Recording a new local request.");
    }
    chunks = [];
    const mic = await ensureMic();
    const mimeType = pickMimeType();
    recorder = mimeType ? new MediaRecorder(mic, { mimeType }) : new MediaRecorder(mic);
    recorder.addEventListener("dataavailable", (event) => {
      if (event.data && event.data.size > 0) {
        chunks.push(event.data);
      }
    });
    recorder.addEventListener("stop", () => {
      const type = recorder.mimeType || "audio/webm";
      const blob = new Blob(chunks, { type });
      recorder = null;
      updateRecordButtons("idle");
      void sendAudio(blob);
    });
    recorder.start();
    updateRecordButtons("recording");
    setStatus("Recording", "ok");
    log("mic", "recording started");
  } catch (error) {
    setStatus(String(error.message || error), "bad");
    log("error", String(error.message || error));
    updateRecordButtons("idle");
  }
}

function pauseRecording() {
  if (!recorder || recorder.state !== "recording") {
    return;
  }
  recorder.pause();
  updateRecordButtons("paused");
  setStatus("Paused", "warn");
  log("mic", "recording paused");
}

function resumeRecording() {
  if (!recorder || recorder.state !== "paused") {
    return;
  }
  recorder.resume();
  updateRecordButtons("recording");
  setStatus("Recording", "ok");
  log("mic", "recording resumed");
}

function stopRecording() {
  if (!recorder || recorder.state === "inactive") {
    return;
  }
  recorder.stop();
  setStatus("Sending audio", "warn");
}

async function postJson(path, payload) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok || !data.ok) {
    throw new Error(data.error || data.stderr || `HTTP ${response.status}`);
  }
  return data;
}

function actionTitle(item, kind) {
  if (kind === "agenda") {
    return item.title || item.input || `Agenda #${item.id}`;
  }
  return item.title || item.action || `Approval #${item.id}`;
}

function actionMeta(item, kind) {
  if (kind === "agenda") {
    const due = item.due_date || "no date";
    const estimate = item.estimate_minutes ? `${item.estimate_minutes}m` : "?";
    return `agenda #${item.id} P${item.priority || "?"} ${due} ${estimate}`;
  }
  return `approval #${item.id} T${item.tier || "?"} ${item.action || ""}`;
}

function actionDetails(item, kind) {
  if (!item) {
    return "No pending action selected.";
  }
  const command = Array.isArray(item.command) ? item.command.join(" ") : item.command || "";
  const lines = [
    `${kind} #${item.id}`,
    "==============",
    `title     ${actionTitle(item, kind)}`,
    `status    ${item.status || "pending"}`,
  ];
  if (kind === "agenda") {
    lines.push(
      `due       ${item.due_date || "-"}`,
      `priority  ${item.priority || "-"}`,
      `estimate  ${item.estimate_minutes || "-"} min`,
      `command   ${command || "-"}`
    );
  } else {
    lines.push(
      `action    ${item.action || "-"}`,
      `tier      ${item.tier || "-"}`,
      `target    ${item.target || "-"}`,
      `command   ${command || "-"}`,
      `risk      ${item.risk || "-"}`,
      `rollback  ${item.rollback || "-"}`
    );
  }
  if (item.note) {
    lines.push(`note      ${item.note}`);
  }
  return lines.join("\n");
}

function updateActionButtons() {
  const hasSelection = Boolean(selectedAction);
  approveActionBtn.disabled = busy || !hasSelection;
  rejectActionBtn.disabled = busy || !hasSelection;
}

function selectAction(kind, item) {
  selectedAction = { kind, id: Number(item.id), item };
  actionPreview.textContent = actionDetails(item, kind);
  Array.from(actionList.querySelectorAll(".action-item")).forEach((button) => {
    button.classList.toggle(
      "selected",
      button.dataset.kind === kind && Number(button.dataset.id) === Number(item.id)
    );
  });
  updateActionButtons();
}

function renderActionQueue(data) {
  actionList.replaceChildren();
  const rows = [];
  (data.approvals || []).forEach((item) => rows.push({ kind: "approval", item }));
  (data.agenda || []).forEach((item) => rows.push({ kind: "agenda", item }));
  if (!rows.length) {
    const empty = document.createElement("li");
    empty.className = "action-meta";
    empty.textContent = "No pending action.";
    actionList.append(empty);
    selectedAction = null;
    actionPreview.textContent = "Queue empty.";
    updateActionButtons();
    return;
  }
  rows.forEach(({ kind, item }) => {
    const button = document.createElement("button");
    const title = document.createElement("span");
    const meta = document.createElement("span");
    button.type = "button";
    button.className = "action-item";
    button.dataset.kind = kind;
    button.dataset.id = item.id;
    title.className = "action-title";
    title.textContent = actionTitle(item, kind);
    meta.className = "action-meta";
    meta.textContent = actionMeta(item, kind);
    button.append(title, meta);
    button.addEventListener("click", () => selectAction(kind, item));
    actionList.append(button);
  });
  if (selectedAction) {
    const match = rows.find(({ kind, item }) => kind === selectedAction.kind && Number(item.id) === selectedAction.id);
    if (match) {
      selectAction(match.kind, match.item);
      return;
    }
  }
  selectAction(rows[0].kind, rows[0].item);
}

async function refreshActionQueue(showOk = true) {
  try {
    const response = await fetch("/api/voice/action/queue", { cache: "no-store" });
    const data = await response.json();
    if (!response.ok || !data.ok) {
      throw new Error(data.error || "queue unavailable");
    }
    renderActionQueue(data);
    if (showOk) {
      setStatus(`Queue ${data.total || 0} pending`, "ok");
    }
  } catch (error) {
    setStatus(String(error.message || error), "bad");
    log("error", String(error.message || error));
  }
}

async function queueLastAction() {
  const text = (textInput.value || transcriptBox.value || lastInputText).trim();
  if (!text) {
    setStatus("No action text", "warn");
    return;
  }
  setBusy(true);
  setStatus("Queueing", "warn");
  try {
    const data = await postJson("/api/voice/action/queue", { text });
    const route = data.route || {};
    answerBox.textContent = data.answer || route.answer || "No action queued.";
    lastAnswer = answerBox.textContent;
    actionPreview.textContent = data.queued ? actionDetails(data.item, data.kind) : (route.answer || answerBox.textContent);
    if (data.queue) {
      renderActionQueue(data.queue);
    } else {
      await refreshActionQueue(false);
    }
    speakBtn.disabled = !lastAnswer;
    setStatus(data.queued ? "Queued" : "Not queued", data.queued ? "ok" : "warn");
    log("action", data.queued ? data.answer : "no queueable action");
    textInput.value = "";
  } catch (error) {
    showRequestError(error);
  } finally {
    setBusy(false);
  }
}

async function queueQuickAction(text) {
  if (!text) {
    return;
  }
  setMode("action");
  transcriptBox.value = text;
  textInput.value = "";
  lastInputText = text;
  await queueLastAction();
}

async function resolveSelectedAction(action) {
  if (!selectedAction) {
    return;
  }
  if (action === "approve") {
    const ok = window.confirm(`Execute ${selectedAction.kind} #${selectedAction.id}?`);
    if (!ok) {
      return;
    }
  }
  setBusy(true);
  setStatus(action === "approve" ? "Approving" : "Rejecting", "warn");
  try {
    const endpoint = action === "approve" ? "/api/voice/action/approve" : "/api/voice/action/reject";
    const data = await postJson(endpoint, {
      kind: selectedAction.kind,
      id: selectedAction.id,
      reason: "Voice Console V0",
    });
    answerBox.textContent = data.stdout || data.stderr || `${action} ok`;
    lastAnswer = answerBox.textContent;
    speakBtn.disabled = !lastAnswer;
    if (data.queue) {
      renderActionQueue(data.queue);
    } else {
      await refreshActionQueue(false);
    }
    setStatus(action === "approve" ? "Approved" : "Rejected", "ok");
    log("action", `${action} ${selectedAction.kind} #${selectedAction.id}`);
  } catch (error) {
    showRequestError(error);
  } finally {
    setBusy(false);
  }
}

async function sendAudio(blob) {
  const requestMode = activeMode();
  setBusy(true);
  replayBtn.disabled = false;
  if (lastAudioUrl) {
    URL.revokeObjectURL(lastAudioUrl);
  }
  lastAudioUrl = URL.createObjectURL(blob);
  audioPlayer.src = lastAudioUrl;
  try {
    const params = new URLSearchParams({ mode: requestMode, max_tokens: "180" });
    const response = await fetch(`/api/voice/audio?${params.toString()}`, {
      method: "POST",
      headers: { "Content-Type": blob.type || "application/octet-stream" },
      body: blob,
    });
    const data = await response.json();
    if (!response.ok || !data.ok) {
      throw new Error(data.error || data.stderr || `audio stage failed: ${data.stage || "unknown"}`);
    }
    if (requestMode === "codex") {
      transcriptBox.value = "";
      lastInputText = "";
      lastAnswer = "";
      answerBox.textContent = "Validated read-only spec ready for review. No Codex task has run.";
      speakBtn.disabled = true;
      applyCodexPreview(data);
      setStatus("Codex preview ready", "ok");
      log("codex", "validated spec preview ready; raw voice input stayed local");
      return;
    }
    transcriptBox.value = data.transcript || "";
    answerBox.textContent = data.answer || "";
    lastInputText = data.transcript || "";
    lastAnswer = data.answer || "";
    if (requestMode === "action") {
      actionPreview.textContent = data.answer || "";
      await refreshActionQueue(false);
    }
    speakBtn.disabled = !lastAnswer;
    setStatus("Answer ready", "ok");
    log(requestMode, data.transcript || "audio sent");
    if (autoSpeak.checked && lastAnswer) {
      await speakLast();
    }
  } catch (error) {
    showRequestError(error);
  } finally {
    setBusy(false);
    updateRecordButtons("idle");
  }
}

async function sendText() {
  const text = textInput.value.trim() || transcriptBox.value.trim();
  if (!text) {
    setStatus("No text", "warn");
    return;
  }
  const requestMode = activeMode();
  setBusy(true);
  setStatus(
    requestMode === "codex" ? "Compiling local Codex preview (up to 120 s)" : "Thinking",
    "warn"
  );
  try {
    const data = await postJson("/api/voice/ask-text", {
      text,
      mode: requestMode,
      max_tokens: 180,
    });
    if (requestMode === "codex") {
      transcriptBox.value = "";
      textInput.value = "";
      lastInputText = "";
      lastAnswer = "";
      answerBox.textContent = "Validated read-only spec ready for review. No Codex task has run.";
      speakBtn.disabled = true;
      applyCodexPreview(data);
      setStatus("Codex preview ready", "ok");
      log("codex", "validated spec preview ready; raw typed input stayed local");
      return;
    }
    transcriptBox.value = data.text || text;
    answerBox.textContent = data.answer || "";
    lastInputText = data.text || text;
    lastAnswer = data.answer || "";
    if (requestMode === "action") {
      actionPreview.textContent = data.answer || "";
      await refreshActionQueue(false);
    }
    speakBtn.disabled = !lastAnswer;
    setStatus("Answer ready", "ok");
    log(requestMode, text);
    textInput.value = "";
    if (autoSpeak.checked && lastAnswer) {
      await speakLast();
    }
  } catch (error) {
    showRequestError(error);
  } finally {
    setBusy(false);
  }
}

async function runCodexPreview() {
  if (!codexPreview || !codexReviewed.checked) {
    setStatus("Review the exact Codex spec first", "warn");
    return;
  }
  const approved = window.confirm(
    `Run one read-only Codex task?\n\nThis sends the canonical spec and permitted repository content to OpenAI.\nWorkspace: ${codexPreview.workspace}\nSHA-256: ${codexPreview.digest}`
  );
  if (!approved) {
    return;
  }
  setBusy(true);
  setStatus("Running read-only Codex", "warn");
  try {
    const data = await postJson("/api/voice/codex/run", {
      preview_id: codexPreview.previewId,
      spec_sha256: codexPreview.digest,
      canonical_spec: codexPreview.canonical,
      confirmed: true,
    });
    answerBox.textContent = data.answer || JSON.stringify(data.result || {}, null, 2);
    lastAnswer = answerBox.textContent;
    speakBtn.disabled = !lastAnswer;
    invalidateCodexPreview("Preview consumed. Create a new preview for another run.");
    setStatus("Codex result ready", "ok");
    log("codex", "read-only task completed");
  } catch (error) {
    invalidateCodexPreview("Run failed or preview consumed. Create a new preview before retrying.");
    setStatus(String(error.message || error), "bad");
    log("error", String(error.message || error));
  } finally {
    setBusy(false);
  }
}

async function revalidateEditedCodexSpec() {
  const draft = codexSpec.value.trim();
  if (!draft) {
    setStatus("No edited Codex spec", "warn");
    return;
  }
  setBusy(true);
  setStatus("Revalidating edited spec", "warn");
  try {
    const data = await postJson("/api/voice/codex/review", { canonical_spec: draft });
    applyCodexPreview(data);
    setStatus("Edited Codex spec validated", "ok");
    log("codex", "operator-edited spec revalidated; no Codex task has run");
  } catch (error) {
    codexPreview = null;
    codexReviewed.checked = false;
    codexReviewed.disabled = true;
    setStatus(String(error.message || error), "bad");
    log("error", String(error.message || error));
  } finally {
    setBusy(false);
  }
}

function replayAudio() {
  if (!lastAudioUrl) {
    return;
  }
  audioPlayer.hidden = false;
  audioPlayer.currentTime = 0;
  void audioPlayer.play();
}

async function speakLast() {
  if (!lastAnswer) {
    return;
  }
  speakBtn.disabled = true;
  try {
    const response = await fetch("/api/voice/synthesize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: speechText(lastAnswer) }),
    });
    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try {
        const payload = await response.json();
        detail = payload.error || payload.stderr || detail;
      } catch (_error) {
        // Keep the visible HTTP error when the server did not return JSON.
      }
      throw new Error(detail);
    }
    const audio = await response.blob();
    if (audio.type !== "audio/wav") {
      throw new Error(`unexpected TTS content type: ${audio.type || "unknown"}`);
    }
    if (lastTtsAudioUrl) {
      URL.revokeObjectURL(lastTtsAudioUrl);
    }
    lastTtsAudioUrl = URL.createObjectURL(audio);
    audioPlayer.src = lastTtsAudioUrl;
    audioPlayer.hidden = false;
    audioPlayer.currentTime = 0;
    await audioPlayer.play();
    setStatus("Piper playing on this browser", "ok");
  } catch (error) {
    setStatus(String(error.message || error), "bad");
    log("error", String(error.message || error));
  } finally {
    speakBtn.disabled = false;
  }
}

function speechText(text) {
  if (text.startsWith("Etat CTOS reel:")) {
    const lines = text
      .split("\n")
      .filter((line) => line.startsWith("- Host:") || line.startsWith("- RAM:") || line.startsWith("- Tour/core:") || line.startsWith("- Kali:") || line.startsWith("- OpenJarvis") || line.startsWith("- Prochaine action:"));
    return `Etat CTOS affiche. ${lines.join(". ")}. Details complets a l'ecran.`;
  }
  if (text.length <= 900) {
    return text;
  }
  return `${text.slice(0, 850)}. Reponse complete affichee a l'ecran.`;
}

async function loadStatus() {
  try {
    const response = await fetch("/api/voice/status", { cache: "no-store" });
    const data = await response.json();
    if (data.build !== CLIENT_BUILD) {
      throw new Error(`UI/server build mismatch: ${CLIENT_BUILD} / ${data.build || "unknown"}`);
    }
    const commands = data.commands || {};
    const ready = commands["ctos-openjarvis"] && commands["ctos-voice"] && commands.ffmpeg;
    if (!busy) {
      setStatus(ready ? "Ready" : "Partial backend", ready ? "ok" : "warn");
    }
    if (data.openjarvis && data.openjarvis.model) {
      log("status", `build ${CLIENT_BUILD} · model ${data.openjarvis.model}`);
    }
  } catch (error) {
    setStatus(String(error.message || error), "bad");
  }
}

modeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    setMode(button.dataset.mode || "chat");
  });
});

recordBtn.addEventListener("click", () => void startRecording());
pauseBtn.addEventListener("click", pauseRecording);
resumeBtn.addEventListener("click", resumeRecording);
stopBtn.addEventListener("click", stopRecording);
replayBtn.addEventListener("click", replayAudio);
speakBtn.addEventListener("click", () => void speakLast());
sendTextBtn.addEventListener("click", () => void sendText());
queueActionBtn.addEventListener("click", () => void queueLastAction());
refreshQueueBtn.addEventListener("click", () => void refreshActionQueue());
approveActionBtn.addEventListener("click", () => void resolveSelectedAction("approve"));
rejectActionBtn.addEventListener("click", () => void resolveSelectedAction("reject"));
codexReviewed.addEventListener("change", updateCodexRunButton);
revalidateCodexBtn.addEventListener("click", () => void revalidateEditedCodexSpec());
runCodexBtn.addEventListener("click", () => void runCodexPreview());
quickActionButtons.forEach((button) => {
  button.addEventListener("click", () => void queueQuickAction(button.dataset.actionText || ""));
});
textInput.addEventListener("input", () => {
  if (activeMode() === "codex" && codexPreview) {
    invalidateCodexPreview("Input changed. Generate and review a new preview.");
  }
});
transcriptBox.addEventListener("input", () => {
  if (activeMode() === "codex" && codexPreview) {
    invalidateCodexPreview("Input changed. Generate and review a new preview.");
  }
});
codexSpec.addEventListener("input", markCodexSpecEdited);
textInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    void sendText();
  }
});

updateRecordButtons("idle");
void loadStatus();
void refreshActionQueue(false);
