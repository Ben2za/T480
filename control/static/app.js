const $ = (id) => document.getElementById(id);

let previousCpu = null;
let actionBusy = false;
let lastVmAction = null;

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;",
  }[char]));
}

function clamp(value) {
  return Math.max(0, Math.min(100, value));
}

function pct(value) {
  return `${clamp(value).toFixed(1)}%`;
}

function uptimeText(seconds) {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  if (days) return `${days}d ${hours}h ${minutes}m`;
  return `${hours}h ${minutes}m`;
}

function item(left, right, note = "", tone = "") {
  return `<div class="item"><span>${esc(left)}<br><small>${esc(note)}</small></span><strong class="${tone}">${esc(right)}</strong></div>`;
}

function cpuPercent(cpu) {
  if (!previousCpu) {
    previousCpu = cpu;
    return 0;
  }
  const idle = cpu.idle - previousCpu.idle;
  const total = cpu.total - previousCpu.total;
  previousCpu = cpu;
  if (total <= 0) return 0;
  return (1 - idle / total) * 100;
}

function serviceTone(state) {
  if (state === "active") return "ok";
  if (state === "inactive") return "warn";
  return "bad";
}

function eventRows(data) {
  const events = [];
  events.push(["CTRL", "cockpit telemetry refresh"]);
  if (lastVmAction) events.push(["VMS", lastVmAction]);
  if (!data.vms.available) events.push(["VMS", "libvirt unavailable or no socket access"]);
  if (data.vms.infra && data.vms.infra.available && !data.vms.infra.ok) {
    events.push(["VMS", "CTOS libvirt infra has pending actions or conflicts"]);
  }
  if (data.vms.infra && !data.vms.infra.available) {
    events.push(["VMS", `CTOS infra status unavailable: ${data.vms.infra.error || "unknown"}`]);
  }
  if (!data.core || !data.core.available) {
    events.push(["CORE", `ctos-core unavailable: ${data.core && data.core.error ? data.core.error : "unknown"}`]);
  } else {
    const srv = data.core.storage && data.core.storage.srv ? data.core.storage.srv : {};
    const layout = data.core.layout || {};
    if (!srv.mounted) events.push(["CORE", "/srv/ctos is not mounted"]);
    if (srv.mounted && !srv.writable) events.push(["CORE", "/srv/ctos is not writable by ctos"]);
    if (layout && layout.complete === false) events.push(["CORE", "/srv/ctos service layout is incomplete"]);
    for (const check of (data.core.network && data.core.network.checks) || []) {
      if (!check.ok) events.push(["CORE", `${check.name} check failed: ${check.target}`]);
    }
  }
  if (!data.fleet || data.fleet.available === false) {
    events.push(["FLEET", `inventory unavailable: ${data.fleet && data.fleet.error ? data.fleet.error : "unknown"}`]);
  }
  for (const connection of data.vms.blocked || []) {
    events.push(["VMS", `${connection.name} blocked: ${connection.raw || "unknown"}`]);
  }
  const ai = data.ai || {};
  const agenda = ai.agenda || {};
  const approvals = ai.approvals || {};
  const runtimeProfiles = ai.runtime_profiles || {};
  const approvalCounts = approvals.counts || {};
  const tools = ai.tools || {};
  if (!tools.ctos_ai || !tools.ctos_ai.available) events.push(["AI", "ctos-ai tool unavailable"]);
  if (!tools.ctos_agenda || !tools.ctos_agenda.available) events.push(["AI", "ctos-agenda tool unavailable"]);
  if (agenda.error) events.push(["AI", `agenda status error: ${agenda.error}`]);
  if (approvals.error) events.push(["AI", `approval status error: ${approvals.error}`]);
  if (runtimeProfiles.error) events.push(["AI", `runtime profile error: ${runtimeProfiles.error}`]);
  if ((approvalCounts.pending || 0) > 0) events.push(["AI", `${approvalCounts.pending} approval(s) pending`]);
  if (!agenda.db_exists) events.push(["AI", "agenda database not initialized yet"]);
  if (!ai.ollama_installed) events.push(["AI", "ollama not installed; model runtime is deferred"]);
  for (const service of data.services) {
    if (service.active !== "active") events.push(["SERVICE", `${service.name} active state: ${service.active}`]);
  }
  if (!events.length) events.push(["OK", "no local events"]);
  return events.slice(0, 8).map(([kind, text]) => `<div class="event"><strong>${kind}</strong><span>${text}</span></div>`).join("");
}

function toneForState(state) {
  if (state === "running") return "ok";
  if (state === "shut off") return "warn";
  if (state === "healthy" || state === "ok" || state === "quiet") return "ok";
  if (state === "not_checked" || state === "offline") return "warn";
  return "bad";
}

function healthPill(label, value) {
  const tone = toneForState(value);
  return `<span class="health-pill"><small>${esc(label)}</small><strong class="${tone}">${esc(value || "--")}</strong></span>`;
}

function renderKali(kali) {
  if (!kali || !kali.available) {
    return `<div class="vm-card kali-card">${item("ctos-kali", "blocked", kali && kali.error ? kali.error : "domain unavailable", "bad")}</div>`;
  }

  const health = kali.health || {};
  const isRunning = kali.state === "running";
  const isShutoff = kali.state === "shut off";
  const current = kali.current_snapshot || kali.disk_role || "no snapshot";
  const disk = kali.active_disk ? kali.active_disk.replace("/var/lib/libvirt/ctos/", "") : "unknown";
  const checked = health.checked_at ? new Date(health.checked_at * 1000).toLocaleTimeString() : "not checked";
  const disabled = actionBusy ? "disabled" : "";
  const startDisabled = actionBusy || !isShutoff ? "disabled" : "";
  const shutdownDisabled = actionBusy || !isRunning ? "disabled" : "";
  const checkpointDisabled = actionBusy || !isShutoff ? "disabled" : "";

  return `
    <div class="vm-card kali-card">
      <div class="vm-top">
        <div>
          <strong>ctos-kali</strong>
          <small>${esc(current)}</small>
        </div>
        <span class="${toneForState(kali.state)}">${esc(kali.state_raw || kali.state)}</span>
      </div>
      <div class="vm-meta">
        <span>${esc(kali.disk_role)}</span>
        <span>${esc(disk)}</span>
      </div>
      <div class="health-grid">
        ${healthPill("agent", health.agent)}
        ${healthPill("net", health.internet)}
        ${healthPill("dns", health.dns)}
        ${healthPill("voice", health.voice)}
      </div>
      <div class="vm-note">health ${esc(health.summary || "unknown")} / ${esc(checked)}</div>
      <div class="vm-actions">
        <button class="vm-action" data-domain="ctos-kali" data-action="start" ${startDisabled} title="Start ctos-kali">Start</button>
        <button class="vm-action" data-domain="ctos-kali" data-action="shutdown" ${shutdownDisabled} title="Graceful shutdown through guest agent">Shutdown</button>
        <button class="vm-action" data-domain="ctos-kali" data-action="console" ${disabled} title="Open virt-manager console">Console</button>
        <button class="vm-action" data-domain="ctos-kali" data-action="checkpoint" ${checkpointDisabled} title="Create checkpoint while shut off">Checkpoint</button>
      </div>
    </div>
  `;
}

function renderCore(core) {
  if (!core || !core.available) {
    $("coreState").textContent = "offline";
    $("core").innerHTML = item("ctos-core", "unavailable", core && core.error ? core.error : "missing", "bad");
    return;
  }

  const memory = core.memory || {};
  const storage = core.storage || {};
  const srv = storage.srv || {};
  const layout = core.layout || {};
  const role = core.role || {};
  const checks = (core.network && core.network.checks) || [];
  const serviceNote = (core.services || []).map((s) => `${s.name}:${s.active}`).join(" ");
  const netNote = checks.map((check) => `${check.name}:${check.ok ? "ok" : "bad"}`).join(" ");
  const srvTone = srv.mounted && srv.writable ? "ok" : "bad";

  $("coreState").textContent = role.role ? `${role.role} online` : "online";
  $("core").innerHTML = [
    item(core.hostname || "ctos-core", core.kernel || "unknown", `up ${uptimeText(core.uptime_seconds || 0)}`, "ok"),
    item("/srv/ctos", srv.mounted ? "mounted" : "missing", `${srv.source || "--"} / free ${srv.free_text || "--"}`, srvTone),
    item("Layout", layout.complete ? "complete" : "partial", `marker ${layout.marker_exists ? "present" : "missing"}`, layout.complete ? "ok" : "warn"),
    item("RAM", `${memory.used_percent || 0}%`, `${memory.used_text || "--"} / ${memory.total_text || "--"}`, "info"),
    item("Network", checks.every((check) => check.ok) ? "ok" : "attention", netNote || "not checked", checks.every((check) => check.ok) ? "ok" : "warn"),
    item("Services", "tracked", serviceNote || "not checked", "info"),
    item("Sudo", core.sudo_password_required ? "closed" : "open", "passwordless bootstrap path", core.sudo_password_required ? "ok" : "bad"),
  ].join("");
}

function renderFleet(fleet) {
  if (!fleet || fleet.available === false) {
    $("fleetState").textContent = "offline";
    $("fleet").innerHTML = item("inventory", "unavailable", fleet && fleet.error ? fleet.error : "missing", "bad");
    return;
  }

  const nodes = fleet.nodes || [];
  const online = nodes.filter((node) => node.live && node.live.available).length;
  $("fleetState").textContent = `${online}/${nodes.length} online`;
  const nodeHtml = nodes.map((node) => {
    const live = node.live || {};
    const state = live.available ? "online" : node.status || "planned";
    const note = live.available ? `${node.role} / ${live.kernel || "live"}` : `${node.role} / ${node.os}`;
    return item(node.id, state, note, live.available ? "ok" : state === "planned" ? "info" : "warn");
  }).join("");
  const features = (fleet.features || []).slice(0, 4).map((feature) => (
    item(feature.id, feature.status, `${feature.owner} -> ${feature.target}`, feature.status === "v1" ? "ok" : "info")
  )).join("");
  $("fleet").innerHTML = nodeHtml + features;
}

async function runVmAction(button) {
  if (actionBusy) return;
  const action = button.dataset.action;
  const domain = button.dataset.domain;
  actionBusy = true;
  lastVmAction = `${domain} ${action} requested`;
  try {
    const res = await fetch("/api/vm/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ domain, action }),
    });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || "action failed");
    lastVmAction = `${domain} ${action}: ${data.message || "ok"}`;
  } catch (error) {
    lastVmAction = `${domain} ${action}: ${error.message}`;
  } finally {
    actionBusy = false;
    refresh();
  }
}

async function refresh() {
  const res = await fetch("/api/status", { cache: "no-store" });
  const data = await res.json();
  const host = data.host;
  const cpu = cpuPercent(host.cpu);

  $("time").textContent = new Date(data.time * 1000).toLocaleString();
  $("host").textContent = host.hostname;
  $("uptime").textContent = `up ${uptimeText(host.uptime_seconds)}`;
  $("load").textContent = `load ${host.load.join(" ")}`;
  $("mode").textContent = data.modes.active;

  $("cpuBar").style.width = pct(cpu);
  $("cpuText").textContent = pct(cpu);
  $("ramBar").style.width = pct(host.memory.used_percent);
  $("ramText").textContent = `${host.memory.used_percent}%`;
  $("rootBar").style.width = pct(host.disk.root_used_percent);
  $("rootText").textContent = `${host.disk.root_used_percent}%`;
  $("homeBar").style.width = pct(host.disk.home_used_percent);
  $("homeText").textContent = `${host.disk.home_used_percent}%`;
  $("temps").innerHTML = host.temps.map((t) => `<span class="chip">${t.name} ${t.celsius}C</span>`).join("") || `<span class="chip">temps unavailable</span>`;

  $("modes").innerHTML = data.modes.planned.map((mode) => `
    <div class="mode-card">
      <strong>${mode.name}</strong>
      <small>${mode.state} / ${mode.ram}</small>
    </div>
  `).join("");

  $("network").innerHTML = data.network.map((n) => {
    const tone = n.state === "up" ? "ok" : "warn";
    return item(n.name, n.state, `rx ${n.rx_text} / tx ${n.tx_text}`, tone);
  }).join("");

  if (data.vms.available) {
    const ready = (data.vms.connections || []).filter((conn) => conn.available).length;
    const infra = data.vms.infra;
    const infraResources = infra && infra.available ? infra.resources || [] : [];
    const kali = data.vms.kali;
    $("vmState").textContent = kali && kali.available ? `kali ${kali.state} / ${ready} conns` : `${data.vms.domains.length} domains / ${ready} conns`;
    const kaliHtml = renderKali(kali);
    let restHtml = "";
    if (data.vms.domains.length) {
      restHtml = data.vms.domains
        .filter((vm) => vm.name !== "ctos-kali")
        .map((vm) => item(vm.name, vm.state, `${vm.connection} / id ${vm.id}`, vm.state.includes("running") ? "ok" : "warn"))
        .join("");
    } else if (infraResources.length) {
      restHtml = infraResources.map((res) => {
        const pending = (res.actions || []).length > 0;
        const tone = res.errors && res.errors.length ? "bad" : pending ? "warn" : "ok";
        const state = res.errors && res.errors.length ? "conflict" : pending ? "pending" : "ready";
        return item(res.name, state, `${res.kind} / active ${res.active} / autostart ${res.autostart}`, tone);
      }).join("");
    } else {
      restHtml = (data.vms.connections || []).map((conn) => item(conn.name, conn.available ? "empty" : "blocked", conn.uri, conn.available ? "warn" : "bad")).join("");
    }
    $("vms").innerHTML = [kaliHtml, restHtml].filter(Boolean).join("");
  } else {
    $("vmState").textContent = "blocked";
    $("vms").innerHTML = item("libvirt", "unavailable", data.vms.raw || "unknown", "bad");
  }

  renderCore(data.core);
  renderFleet(data.fleet);
  $("services").innerHTML = data.services.map((s) => item(s.name, s.active, `enabled ${s.enabled}`, serviceTone(s.active))).join("");
  const ai = data.ai || {};
  const agenda = ai.agenda || {};
  const counts = agenda.counts || {};
  const approvals = ai.approvals || {};
  const approvalCounts = approvals.counts || {};
  const pendingApprovals = Array.isArray(approvals.pending) ? approvals.pending : [];
  const pendingCount = approvalCounts.pending || 0;
  const tools = ai.tools || {};
  const runtime = ai.model_runtime || {};
  const runtimeProfiles = ai.runtime_profiles || {};
  const profiles = Array.isArray(runtimeProfiles.profiles) ? runtimeProfiles.profiles : [];
  const adapter = runtimeProfiles.adapter_contract || {};
  const toolsReady = tools.ctos_ai && tools.ctos_ai.available && tools.ctos_agenda && tools.ctos_agenda.available;
  $("aiState").textContent = toolsReady ? `${counts.open || 0} open / ${pendingCount} pending` : "partial";
  const approvalItems = [
    item(
      "Approvals",
      approvals.db_exists ? `${pendingCount} pending` : "new",
      `failed ${approvalCounts.failed || 0} / total ${approvalCounts.total || 0}`,
      approvals.error ? "bad" : pendingCount ? "warn" : approvals.db_exists ? "ok" : "info",
    ),
    ...pendingApprovals.slice(0, 3).map((approval) => (
      item(
        `#${approval.id} ${approval.action}`,
        `T${approval.tier}`,
        approval.target || approval.title || "pending approval",
        "warn",
      )
    )),
  ].join("");
  const runtimeItems = [
    item(
      "Runtime Profiles",
      runtimeProfiles.available ? `${runtimeProfiles.count || profiles.length} known` : "missing",
      `active ${runtimeProfiles.active_profile || "none"}`,
      runtimeProfiles.error ? "bad" : runtimeProfiles.available ? "info" : "warn",
    ),
    ...profiles.slice(0, 2).map((profile) => (
      item(
        profile.id || "runtime",
        profile.status || "candidate",
        `${profile.target_node || "--"} / ${profile.readiness || "--"}`,
        profile.status === "first_local_candidate" ? "ok" : "info",
      )
    )),
    item(
      "Dry-run Adapter",
      adapter.command ? "ready" : "missing",
      adapter.network_default === false ? "no network/model contact by default" : "check policy",
      adapter.command ? "ok" : "warn",
    ),
  ].join("");
  $("ai").innerHTML = [
    item("Tool Contract", toolsReady ? "ready" : "partial", "ctos-ai + ctos-agenda", toolsReady ? "ok" : "warn"),
    item("Agenda", agenda.db_exists ? `${counts.open || 0} open` : "new", `due ${counts.due_today || 0} / total ${counts.total || 0}`, agenda.error ? "bad" : agenda.db_exists ? "ok" : "warn"),
    approvalItems,
    runtimeItems,
    item("Model Runtime", runtime.configured ? "configured" : "deferred", runtime.note || "waiting for approval boundary", runtime.configured ? "ok" : "info"),
    item("Ollama", ai.ollama_running ? "running" : "stopped", ai.ollama_installed ? "installed" : "not installed", ai.ollama_running ? "ok" : "warn"),
    item("Workers", "planned", "kali-triage / dev-coder / kb-retriever", "info"),
  ].join("");
  $("events").innerHTML = eventRows(data);
}

const canvas = $("globe");
const ctx = canvas.getContext("2d");
let t = 0;

function drawGlobe() {
  const rect = canvas.getBoundingClientRect();
  const scale = window.devicePixelRatio || 1;
  canvas.width = Math.floor(rect.width * scale);
  canvas.height = Math.floor(rect.height * scale);
  ctx.setTransform(scale, 0, 0, scale, 0, 0);
  const w = rect.width;
  const h = rect.height;
  const r = Math.min(w, h) * 0.42;
  const cx = w / 2;
  const cy = h / 2;
  ctx.clearRect(0, 0, w, h);

  ctx.strokeStyle = "#8b0000";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, Math.PI * 2);
  ctx.stroke();

  ctx.strokeStyle = "#303640";
  ctx.lineWidth = 1;
  for (let i = -3; i <= 3; i++) {
    ctx.beginPath();
    ctx.ellipse(cx, cy, r * Math.cos(i * 0.22), r, 0, 0, Math.PI * 2);
    ctx.stroke();
  }
  for (let y = -2; y <= 2; y++) {
    ctx.beginPath();
    ctx.ellipse(cx, cy + y * r * 0.28, r * Math.sqrt(1 - Math.abs(y) * 0.12), r * 0.12, 0, 0, Math.PI * 2);
    ctx.stroke();
  }

  for (let i = 0; i < 24; i++) {
    const a = t * 0.011 + i * 0.58;
    const x = cx + Math.cos(a) * r * 0.82;
    const y = cy + Math.sin(a * 1.7) * r * 0.45;
    ctx.fillStyle = i % 3 === 0 ? "#65b8d8" : "#e8e8e8";
    ctx.beginPath();
    ctx.arc(x, y, i % 3 === 0 ? 2.5 : 1.8, 0, Math.PI * 2);
    ctx.fill();
  }

  ctx.strokeStyle = "rgba(214, 64, 64, 0.55)";
  for (let i = 0; i < 4; i++) {
    const a = t * 0.015 + i * 1.3;
    ctx.beginPath();
    ctx.arc(cx, cy, r * (0.55 + i * 0.09), a, a + 0.55);
    ctx.stroke();
  }

  t++;
  requestAnimationFrame(drawGlobe);
}

refresh();
setInterval(refresh, 2500);
drawGlobe();

document.addEventListener("click", (event) => {
  const button = event.target.closest(".vm-action");
  if (!button) return;
  runVmAction(button);
});
