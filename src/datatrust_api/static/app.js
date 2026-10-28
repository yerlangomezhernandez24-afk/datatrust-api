"use strict";

const RUN_LIMIT = 10;
const ISSUE_LIMIT = 25;
const MAX_FILE_BYTES = 2 * 1024 * 1024;
const state = {
  runsOffset: 0,
  issuesOffset: 0,
  currentRunId: null,
  runsHasNext: false,
  issuesHasNext: false,
};
const byId = (id) => document.getElementById(id);

function setStatus(message, kind = "info") {
  const status = byId("status");
  status.textContent = message;
  status.dataset.kind = kind;
  status.setAttribute("role", kind === "error" ? "alert" : "status");
  status.setAttribute("aria-live", kind === "error" ? "assertive" : "polite");
}

function setUploadBusy(isBusy) {
  const formElement = byId("upload-form");
  formElement.setAttribute("aria-busy", String(isBusy));
  for (const control of formElement.querySelectorAll("button, input, select")) {
    control.disabled = isBusy;
  }
}

async function apiJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    let message = `Error HTTP ${response.status}`;
    try {
      const payload = await response.json();
      message = payload.detail || message;
    } catch (_) {
      // La respuesta puede no ser JSON; se conserva el mensaje HTTP neutro.
    }
    throw new Error(message);
  }
  return response.json();
}

async function loadHealth() {
  const health = await apiJson("/health");
  byId("app-health").textContent = `API local activa · v${health.version}`;
}

function setHealthError() {
  const health = byId("app-health");
  health.textContent = "API local no disponible";
  health.closest(".health-line").dataset.kind = "error";
}

function setMetrics(run) {
  byId("metric-total").textContent = run ? run.total_rows : "—";
  byId("metric-valid").textContent = run ? run.valid_rows : "—";
  byId("metric-invalid").textContent = run ? run.invalid_rows : "—";
  byId("metric-issues").textContent = run ? run.issue_count : "—";
}

async function loadProfiles() {
  const profiles = await apiJson("/api/v1/profiles");
  const select = byId("profile");
  select.replaceChildren();
  for (const profile of profiles) {
    const option = document.createElement("option");
    option.value = profile.id;
    option.textContent = `${profile.id} — ${profile.description}`;
    if (profile.id === "orders_v1") {
      option.selected = true;
      option.defaultSelected = true;
    }
    select.append(option);
  }
}

function runLabel(run) {
  const created = new Date(run.created_at);
  const timestamp = Number.isNaN(created.valueOf())
    ? run.created_at
    : created.toLocaleString();
  return `${timestamp} · ${run.profile} · ${run.issue_count} incidencias`;
}

async function loadRuns() {
  const fetched = await apiJson(
    `/api/v1/runs?limit=${RUN_LIMIT + 1}&offset=${state.runsOffset}`,
  );
  state.runsHasNext = fetched.length > RUN_LIMIT;
  const runs = fetched.slice(0, RUN_LIMIT);
  const list = byId("runs-list");
  list.replaceChildren();
  byId("runs-empty").hidden = runs.length !== 0;
  for (const run of runs) {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "run-item";
    button.dataset.runId = run.id;
    button.setAttribute("aria-pressed", String(run.id === state.currentRunId));
    button.textContent = runLabel(run);
    button.addEventListener("click", () => selectRun(run.id));
    item.append(button);
    list.append(item);
  }
  const page = Math.floor(state.runsOffset / RUN_LIMIT) + 1;
  byId("runs-page").textContent = `Página ${page}`;
  byId("runs-prev").disabled = state.runsOffset === 0;
  byId("runs-next").disabled = !state.runsHasNext;
}

function markSelectedRun() {
  for (const button of document.querySelectorAll(".run-item")) {
    button.setAttribute("aria-pressed", String(button.dataset.runId === state.currentRunId));
  }
}

function renderIssues(issues) {
  const body = byId("issues-body");
  body.replaceChildren();
  byId("issues-empty").hidden = issues.length !== 0;
  for (const issue of issues) {
    const row = document.createElement("tr");
    for (const value of [issue.row_number, issue.field_name, issue.code, issue.message]) {
      const cell = document.createElement("td");
      cell.textContent = String(value);
      row.append(cell);
    }
    body.append(row);
  }
}

async function loadIssues() {
  if (!state.currentRunId) return;
  const fetched = await apiJson(
    `/api/v1/runs/${encodeURIComponent(state.currentRunId)}/issues?limit=${ISSUE_LIMIT + 1}&offset=${state.issuesOffset}`,
  );
  state.issuesHasNext = fetched.length > ISSUE_LIMIT;
  renderIssues(fetched.slice(0, ISSUE_LIMIT));
  const page = Math.floor(state.issuesOffset / ISSUE_LIMIT) + 1;
  byId("issues-page").textContent = `Página ${page}`;
  byId("issues-prev").disabled = state.issuesOffset === 0;
  byId("issues-next").disabled = !state.issuesHasNext;
}

async function selectRun(runId, announce = true) {
  try {
    state.currentRunId = runId;
    markSelectedRun();
    state.issuesOffset = 0;
    const run = await apiJson(`/api/v1/runs/${encodeURIComponent(runId)}`);
    setMetrics(run);
    byId("selected-run").textContent = `${run.filename} · ${run.profile} · ${run.status}`;
    const download = byId("download-link");
    download.href = `/api/v1/runs/${encodeURIComponent(runId)}/issues.csv`;
    download.classList.remove("disabled");
    download.removeAttribute("aria-disabled");
    download.removeAttribute("tabindex");
    await loadIssues();
    if (announce) setStatus("Ejecución cargada.", "success");
  } catch (error) {
    setStatus(error.message, "error");
  }
}

function updateSelectedFile() {
  const file = byId("csv-file").files[0];
  byId("selected-file").textContent = file
    ? `${file.name} · ${(file.size / 1024).toFixed(1)} KiB`
    : "Ningún archivo seleccionado";
}

function clientFileProblem(file) {
  if (!file.name.toLocaleLowerCase().endsWith(".csv")) {
    return "Selecciona un archivo con extensión .csv.";
  }
  if (file.size > MAX_FILE_BYTES) {
    return "El archivo supera 2 MiB. Reduce su tamaño antes de validarlo.";
  }
  return null;
}

async function submitUpload(event) {
  event.preventDefault();
  const fileInput = byId("csv-file");
  const file = fileInput.files[0];
  if (!file) return;
  const problem = clientFileProblem(file);
  if (problem) {
    setStatus(problem, "error");
    return;
  }

  setUploadBusy(true);
  setStatus("Validando archivo…");
  const form = new FormData();
  form.append("file", file);
  const profile = encodeURIComponent(byId("profile").value);
  try {
    const run = await apiJson(`/api/v1/runs?profile=${profile}`, { method: "POST", body: form });
    setMetrics(run);
    fileInput.value = "";
    updateSelectedFile();
    state.runsOffset = 0;
    await loadRuns();
    await selectRun(run.id, false);
    const validRowsLabel = run.valid_rows === 1 ? "fila válida" : "filas válidas";
    const issuesLabel = run.issue_count === 1 ? "incidencia" : "incidencias";
    setStatus(
      `Validación completada: ${run.valid_rows} ${validRowsLabel} y ${run.issue_count} ${issuesLabel}.`,
      "success",
    );
  } catch (error) {
    setStatus(error.message, "error");
  } finally {
    setUploadBusy(false);
  }
}

byId("upload-form").addEventListener("submit", submitUpload);
byId("csv-file").addEventListener("change", updateSelectedFile);
byId("refresh-runs").addEventListener("click", () => loadRuns().catch((error) => setStatus(error.message, "error")));
byId("runs-prev").addEventListener("click", () => {
  state.runsOffset = Math.max(0, state.runsOffset - RUN_LIMIT);
  loadRuns().catch((error) => setStatus(error.message, "error"));
});
byId("runs-next").addEventListener("click", () => {
  state.runsOffset += RUN_LIMIT;
  loadRuns().catch((error) => setStatus(error.message, "error"));
});
byId("issues-prev").addEventListener("click", () => {
  state.issuesOffset = Math.max(0, state.issuesOffset - ISSUE_LIMIT);
  loadIssues().catch((error) => setStatus(error.message, "error"));
});
byId("issues-next").addEventListener("click", () => {
  state.issuesOffset += ISSUE_LIMIT;
  loadIssues().catch((error) => setStatus(error.message, "error"));
});

loadHealth().catch(setHealthError);
Promise.all([loadProfiles(), loadRuns()]).catch((error) => setStatus(error.message, "error"));
