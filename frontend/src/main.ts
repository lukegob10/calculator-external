type ApiEnvelope<T> = { data: T; metadata: Record<string, unknown> };
type User = { id: number; full_name: string; soeid: string; role: string; status: string };
type Calculation = {
  id: number;
  name: string;
  description: string;
  status: string;
  owner_user_id: number;
  asset: { identifier: string; name: string; asset_type: string };
  current_run_id: number | null;
  latest_run: {
    id: number;
    status: string;
    result: Record<string, number | string>;
    warnings: Array<Record<string, string>>;
    engine_version: string;
  } | null;
  permission: string;
};
type Run = {
  id: number;
  calculation_id: number;
  parameter_set_id: number;
  status: string;
  result: Record<string, number | string>;
  warnings: Array<Record<string, string>>;
  engine_version: string;
};
type Share = { id: number; resource_id: number; grantee_name: string; grantee_soeid: string; permission_level: string; revoked_at: string | null };
type AccessGrant = Share & {
  calculation_name: string;
  calculation_owner_id: number;
  calculation_owner_name: string;
  granted_by_name: string;
};
type UserDetail = {
  user: User;
  owned_calculations: number;
  active_grants_received: number;
  active_grants_given: number;
  recent_audit_events: Array<{ event_type: string; resource_type: string; resource_id: number | null; created_at: string }>;
};
type ParameterSet = { id: number; name: string; version: string; status: string; effective_date: string; payload: Record<string, unknown> };
type AuditEvent = { id: number; event_type: string; resource_type: string; resource_id: number | null; metadata: Record<string, unknown>; created_at: string };

const API_BASE = "http://127.0.0.1:8000";
const app = document.querySelector<HTMLDivElement>("#app");
let token = localStorage.getItem("ecw_token") ?? "";
let currentUser: User | null = null;
let route = "dashboard";

function html(strings: TemplateStringsArray, ...values: unknown[]): string {
  return strings.reduce((out, part, index) => out + part + String(values[index] ?? ""), "");
}

function escapeHtml(value: unknown): string {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  const body = (await response.json()) as ApiEnvelope<T> | { detail: string };
  if (!response.ok) throw new Error("detail" in body ? body.detail : "API request failed.");
  return (body as ApiEnvelope<T>).data;
}

function badge(value: string): string {
  const normalized = value.toUpperCase();
  const color = normalized.includes("COMPLETE") || normalized.includes("ACTIVE") || normalized.includes("PUBLISHED") ? "green"
    : normalized.includes("WARNING") || normalized.includes("PENDING") || normalized.includes("DRAFT") ? "amber"
    : normalized.includes("FAILED") || normalized.includes("DISABLED") || normalized.includes("REVOKED") ? "red"
    : normalized.includes("EDIT") || normalized.includes("ADMIN") || normalized.includes("VIEW") ? "blue"
    : "gray";
  return `<span class="badge ${color}">${escapeHtml(value)}</span>`;
}

function money(value: unknown): string {
  const number = Number(value ?? 0);
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(number);
}

function pct(value: unknown): string {
  if (value === undefined || value === null || value === "") return "-";
  const number = Number(value ?? 0);
  return `${number.toFixed(2)}%`;
}

function emptyState(title: string, body: string, action = ""): string {
  return html`<div class="empty-state">
    <strong>${escapeHtml(title)}</strong>
    <span>${escapeHtml(body)}</span>
    ${action}
  </div>`;
}

function setApp(markup: string): void {
  if (!app) return;
  app.innerHTML = markup;
}

function shell(content: string, active: string): string {
  const isAdmin = currentUser?.role === "ADMIN";
  const nav = [
    ["dashboard", "Deals"],
    ["calculation-new", "New Calculation"],
    ["sharing", "Sharing"],
    ["audit", "Activity"],
    ...(isAdmin ? [["admin", "Admin"], ["parameters", "Parameters"]] : []),
  ];
  return html`
    <div class="app-shell">
      <aside class="sidebar">
        <div class="brand"><div class="brand-mark">EC</div><div><strong>External Calc</strong><span>${escapeHtml(currentUser?.role ?? "")}</span></div></div>
        <div class="nav-label">Workspace</div>
        ${nav.map(([id, label]) => `<button class="nav-item ${active === id ? "active" : ""}" data-route="${id}">${escapeHtml(label)}</button>`).join("")}
      </aside>
      <main class="main">
        <div class="topbar">
          <div class="search">Search deal, asset, SOEID, run ID</div>
          <button class="button" data-action="logout">Logout</button>
          <div class="avatar">${escapeHtml((currentUser?.full_name ?? "U").split(" ").map(part => part[0]).join("").slice(0, 2))}</div>
        </div>
        ${content}
      </main>
    </div>`;
}

function bindShell(): void {
  document.querySelectorAll<HTMLButtonElement>("[data-route]").forEach(button => {
    button.addEventListener("click", () => {
      route = button.dataset.route ?? "dashboard";
      void render();
    });
  });
  document.querySelector<HTMLButtonElement>("[data-action='logout']")?.addEventListener("click", () => {
    token = "";
    currentUser = null;
    localStorage.removeItem("ecw_token");
    void render();
  });
}

function renderLogin(error = ""): void {
  setApp(html`
    <div class="auth-wrap">
      <section class="auth-copy">
        <div class="brand"><div class="brand-mark">EC</div><div><strong>Enterprise Calculation</strong><span>Asset return workspace</span></div></div>
        <h1>Run governed asset calculations with clean audit evidence.</h1>
        <p>Create deals, compare scenarios, inspect applied tax assumptions, and preserve every run with exact input, parameter set, and engine version.</p>
      </section>
      <section class="auth-panel">
        <h2>Sign in</h2>
        <p class="notice">Demo admin: admin / Admin123!. Demo user: lgoblirsch / Demo123!.</p>
        ${error ? `<div class="error">${escapeHtml(error)}</div>` : ""}
        <form id="login-form">
          <div class="field"><label>SOEID</label><input name="soeid" value="lgoblirsch" required></div>
          <div class="field"><label>Password</label><input name="password" type="password" value="Demo123!" required></div>
          <button class="button primary" style="width:100%" type="submit">Sign in</button>
        </form>
      </section>
    </div>`);
  document.querySelector<HTMLFormElement>("#login-form")?.addEventListener("submit", async event => {
    event.preventDefault();
    const form = new FormData(event.currentTarget as HTMLFormElement);
    try {
      const result = await api<{ token: string; user: User }>("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ soeid: form.get("soeid"), password: form.get("password") }),
      });
      token = result.token;
      currentUser = result.user;
      localStorage.setItem("ecw_token", token);
      route = currentUser.role === "ADMIN" ? "admin" : "dashboard";
      await render();
    } catch (err) {
      renderLogin(err instanceof Error ? err.message : "Login failed.");
    }
  });
}

async function renderDashboard(): Promise<void> {
  const data = await api<{ stats: Record<string, number>; calculations: Calculation[] }>("/api/dashboard/business");
  const content = html`
    <div class="page-head"><div><h1>Deals</h1><p>Saved calculations, shared work, and recent output evidence.</p></div><button class="button primary" data-route="calculation-new">New calculation</button></div>
    <div class="status-strip">
      <div class="stat"><span>Open drafts</span><strong>${data.stats.open_drafts ?? 0}</strong></div>
      <div class="stat"><span>Accessible calculations</span><strong>${data.stats.accessible_calculations ?? 0}</strong></div>
      <div class="stat"><span>Shared with me</span><strong>${data.stats.shared_with_me ?? 0}</strong></div>
      <div class="stat"><span>Tasks due</span><strong>${data.stats.tasks_due ?? 0}</strong></div>
      <div class="stat"><span>Exports</span><strong>Scoped</strong></div>
    </div>
    <section class="panel">
      <div class="panel-head"><h2>Calculation deals</h2><span class="pill">Active work</span></div>
      <table><thead><tr><th>Deal</th><th>Asset</th><th>Status</th><th class="num">External return</th><th class="num">Tax impact</th><th>Permission</th><th class="action-cell">Actions</th></tr></thead><tbody>
        ${data.calculations.map(row => html`<tr>
          <td class="name-cell"><strong>${escapeHtml(row.name)}</strong><span>${escapeHtml(row.description || "No description")}</span></td>
          <td>${escapeHtml(row.asset.identifier)}</td><td>${badge(row.status)}</td>
          <td class="num">${pct(row.latest_run?.result.external_return_percent)}</td>
          <td class="num">${pct(row.latest_run?.result.tax_impact_percent)}</td>
          <td>${badge(row.permission)}</td>
          <td class="action-cell"><div class="actions"><button class="button" data-open="${row.id}">Open</button><button class="button primary" data-run="${row.id}">Run</button></div></td>
        </tr>`).join("")}
      </tbody></table>
      ${data.calculations.length === 0 ? emptyState("No calculations yet", "Create the first calculation to see saved work, output evidence, and sharing controls.", `<button class="button primary" data-route="calculation-new">New calculation</button>`) : ""}
    </section>`;
  setApp(shell(content, "dashboard"));
  bindShell();
  document.querySelectorAll<HTMLButtonElement>("[data-run]").forEach(button => button.addEventListener("click", async () => {
    await api<Run>(`/api/calculations/${button.dataset.run}/runs`, { method: "POST" });
    await renderDashboard();
  }));
  document.querySelectorAll<HTMLButtonElement>("[data-open]").forEach(button => button.addEventListener("click", async () => {
    await renderCalculationDetail(Number(button.dataset.open));
  }));
}

async function renderCalculationDetail(id: number): Promise<void> {
  const calc = await api<Calculation>(`/api/calculations/${id}`);
  const runs = await api<Run[]>(`/api/calculations/${id}/runs`);
  const latest = runs[0];
  const metrics = latest?.result ?? {};
  const warningMarkup = latest?.warnings.length
    ? latest.warnings.map(w => `<div class="notice warning">${escapeHtml(w.code)}: ${escapeHtml(w.message)}</div>`).join("")
    : latest
      ? `<div class="notice success">No run warnings on the latest completed run.</div>`
      : `<div class="notice">Run this calculation to generate warning and validation evidence.</div>`;
  const content = html`
    <div class="page-head"><div><h1>${escapeHtml(calc.name)}</h1><p>${escapeHtml(calc.asset.identifier)}. Permission: ${escapeHtml(calc.permission)}.</p></div><div class="actions"><button class="button" data-route="sharing">Share</button><button class="button primary" data-run="${calc.id}">Run calculation</button></div></div>
    <div class="grid wide">
      <section class="panel">
        <div class="panel-head"><h2>Output summary</h2>${badge(calc.status)}</div>
        <div class="metric-grid">
          <div class="metric"><span>External return</span><strong>${pct(metrics.external_return_percent)}</strong></div>
          <div class="metric"><span>ROTCE-like return</span><strong>${pct(metrics.rotce_like_return_percent)}</strong></div>
          <div class="metric"><span>Tax impact</span><strong>${pct(metrics.tax_impact_percent)}</strong></div>
          <div class="metric"><span>Projected value</span><strong>${latest ? money(metrics.projected_value) : "-"}</strong></div>
        </div>
        ${latest ? "" : emptyState("No runs yet", "Run this calculation to generate persisted output, parameter evidence, and engine version metadata.")}
        <table><thead><tr><th>Run</th><th>Status</th><th>Engine</th><th>Parameter</th><th class="num">Net income</th></tr></thead><tbody>
          ${runs.map(run => `<tr><td>RUN-${run.id}</td><td>${badge(run.status)}</td><td>${escapeHtml(run.engine_version)}</td><td>Parameter ${run.parameter_set_id}</td><td class="num">${money(run.result.net_income)}</td></tr>`).join("")}
        </tbody></table>
      </section>
      <aside class="rail">
        <section class="panel"><div class="panel-head"><h2>Run provenance</h2>${badge(latest ? latest.status : "Draft")}</div><div class="activity">
          <div class="activity-item"><strong>Parameter set</strong><span>${latest ? `Parameter ${latest.parameter_set_id}` : "Not applied yet"}</span></div>
          <div class="activity-item"><strong>Engine version</strong><span>${escapeHtml(latest?.engine_version ?? "Not run")}</span></div>
          <div class="activity-item"><strong>Latest run</strong><span>${latest ? `RUN-${latest.id}` : "No run history"}</span></div>
        </div></section>
        <section class="panel"><div class="panel-head"><h2>Warnings</h2>${badge(latest?.warnings.length ? "Review" : "Clean")}</div><div class="panel-body">${warningMarkup}</div></section>
      </aside>
    </div>`;
  setApp(shell(content, "dashboard"));
  bindShell();
  document.querySelector<HTMLButtonElement>("[data-run]")?.addEventListener("click", async () => {
    await api<Run>(`/api/calculations/${id}/runs`, { method: "POST" });
    await renderCalculationDetail(id);
  });
}

async function renderNewCalculation(): Promise<void> {
  const content = html`
    <div class="page-head"><div><h1>New Calculation</h1><p>Create a governed external asset calculation with versioned inputs.</p></div></div>
    <section class="panel"><div class="panel-head"><h2>Calculation setup</h2><span class="pill">Placeholder model</span></div>
      <div class="panel-body">
        <form id="calc-form" class="form-grid">
          <div class="field"><label>Name</label><input name="name" value="Alpha Credit Base" required></div>
          <div class="field"><label>Asset identifier</label><input name="identifier" value="CUSIP 123456AB" required></div>
          <div class="field"><label>Asset name</label><input name="assetName" value="Alpha Credit" required></div>
          <div class="field"><label>Asset value</label><input name="asset_value" type="number" value="84200000" required></div>
          <div class="field"><label>Balance</label><input name="balance" type="number" value="76000000" required></div>
          <div class="field"><label>Price</label><input name="price" type="number" value="98.625" step="0.001" required></div>
          <div class="field"><label>Spread bps</label><input name="spread_bps" type="number" value="245" required></div>
          <div class="field"><label>Rate percent</label><input name="rate_percent" type="number" value="6.4" step="0.01" required></div>
          <div class="field"><label>Capital allocation</label><input name="capital_allocation" type="number" value="11400000" required></div>
          <div class="field"><label>Tax jurisdiction</label><input name="tax_jurisdiction" value="DEFAULT"></div>
          <div style="grid-column:1 / -1"><button class="button primary" type="submit">Create calculation</button></div>
        </form>
      </div>
    </section>`;
  setApp(shell(content, "calculation-new"));
  bindShell();
  document.querySelector<HTMLFormElement>("#calc-form")?.addEventListener("submit", async event => {
    event.preventDefault();
    const f = new FormData(event.currentTarget as HTMLFormElement);
    const created = await api<Calculation>("/api/calculations", {
      method: "POST",
      body: JSON.stringify({
        name: f.get("name"),
        description: "Created from the local MVP form.",
        asset: { identifier: f.get("identifier"), name: f.get("assetName"), identifier_type: "CUSIP", asset_type: "External Asset" },
        input_payload: {
          asset_value: Number(f.get("asset_value")),
          balance: Number(f.get("balance")),
          price: Number(f.get("price")),
          spread_bps: Number(f.get("spread_bps")),
          rate_percent: Number(f.get("rate_percent")),
          capital_allocation: Number(f.get("capital_allocation")),
          tax_jurisdiction: String(f.get("tax_jurisdiction") ?? "DEFAULT"),
        },
      }),
    });
    await renderCalculationDetail(created.id);
  });
}

async function renderAdmin(): Promise<void> {
  const [dashboard, users, grants] = await Promise.all([
    api<{ stats: Record<string, number> }>("/api/dashboard/admin"),
    api<User[]>("/api/admin/users"),
    api<AccessGrant[]>("/api/admin/access-grants"),
  ]);
  const s = dashboard.stats;
  const pending = users.filter(user => user.status === "PENDING").length;
  const disabled = users.filter(user => user.status === "DISABLED").length;
  const content = html`
    <div class="page-head"><div><h1>Application Administration</h1><p>Approve base users, assign roles, disable accounts, and audit access.</p></div></div>
    <div class="status-strip">
      <div class="stat"><span>Active users</span><strong>${s.active_users ?? 0}</strong></div>
      <div class="stat"><span>Pending users</span><strong>${pending}</strong></div>
      <div class="stat"><span>Calculations</span><strong>${s.calculations ?? 0}</strong></div>
      <div class="stat"><span>Active grants</span><strong>${s.active_grants ?? 0}</strong></div>
      <div class="stat"><span>Disabled</span><strong>${disabled}</strong></div>
    </div>
    <div class="grid admin-grid">
      <section class="panel"><div class="panel-head"><h2>User access queue</h2><span class="pill">Admin-only</span></div>
        <table><thead><tr><th>User</th><th>Status</th><th>Role</th><th class="action-cell">Actions</th></tr></thead><tbody>
          ${users.map(user => `<tr><td class="name-cell"><strong>${escapeHtml(user.full_name)}</strong><span>${escapeHtml(user.soeid)}</span></td><td>${badge(user.status)}</td><td>${badge(user.role)}</td><td class="action-cell"><div class="actions"><button class="button" data-user-detail="${user.id}">Inspect</button><button class="button" data-activate="${user.id}">Activate</button><button class="button danger" data-disable="${user.id}">Disable</button></div></td></tr>`).join("")}
        </tbody></table>
      </section>
      <aside class="panel" id="user-detail-panel"><div class="panel-head"><h2>User detail</h2><span class="pill">Select a user</span></div>${emptyState("No user selected", "Inspect a user to see owned work, received grants, granted access, and recent audit events.")}</aside>
    </div>
    <section class="panel" style="margin-top:14px"><div class="panel-head"><h2>Active and historical access grants</h2><span class="pill">Global admin view</span></div>
      <table><thead><tr><th>Calculation</th><th>Owner</th><th>Collaborator</th><th>Permission</th><th>Granted by</th><th>Status</th></tr></thead><tbody>
        ${grants.map(grant => `<tr><td class="name-cell"><strong>${escapeHtml(grant.calculation_name)}</strong><span>Calculation ${grant.resource_id}</span></td><td>${escapeHtml(grant.calculation_owner_name)}</td><td class="name-cell"><strong>${escapeHtml(grant.grantee_name)}</strong><span>${escapeHtml(grant.grantee_soeid)}</span></td><td>${badge(grant.permission_level)}</td><td>${escapeHtml(grant.granted_by_name)}</td><td>${grant.revoked_at ? badge("Revoked") : badge("Active")}</td></tr>`).join("")}
      </tbody></table>
      ${grants.length === 0 ? emptyState("No grants yet", "Owner-created shares and admin access grants will appear here.") : ""}
    </section>`;
  setApp(shell(content, "admin"));
  bindShell();
  document.querySelectorAll<HTMLButtonElement>("[data-user-detail]").forEach(button => button.addEventListener("click", async () => {
    const detail = await api<UserDetail>(`/api/admin/users/${button.dataset.userDetail}`);
    const panel = document.querySelector<HTMLElement>("#user-detail-panel");
    if (!panel) return;
    panel.innerHTML = html`
      <div class="panel-head"><h2>${escapeHtml(detail.user.full_name)}</h2>${badge(detail.user.status)}</div>
      <div class="metric-grid compact">
        <div class="metric"><span>Owned calculations</span><strong>${detail.owned_calculations}</strong></div>
        <div class="metric"><span>Grants received</span><strong>${detail.active_grants_received}</strong></div>
        <div class="metric"><span>Grants given</span><strong>${detail.active_grants_given}</strong></div>
      </div>
      <div class="activity">
        ${detail.recent_audit_events.length ? detail.recent_audit_events.map(event => `<div class="activity-item"><strong>${escapeHtml(event.event_type)}</strong><span>${escapeHtml(event.resource_type)} ${escapeHtml(event.resource_id ?? "")} · ${new Date(event.created_at).toLocaleString()}</span></div>`).join("") : `<div class="notice">No recent audit events for this user.</div>`}
      </div>`;
  }));
  document.querySelectorAll<HTMLButtonElement>("[data-activate]").forEach(button => button.addEventListener("click", async () => {
    await api<User>(`/api/admin/users/${button.dataset.activate}`, { method: "PATCH", body: JSON.stringify({ status: "ACTIVE" }) });
    await renderAdmin();
  }));
  document.querySelectorAll<HTMLButtonElement>("[data-disable]").forEach(button => button.addEventListener("click", async () => {
    await api<User>(`/api/admin/users/${button.dataset.disable}`, { method: "PATCH", body: JSON.stringify({ status: "DISABLED" }) });
    await renderAdmin();
  }));
}

async function renderParameters(): Promise<void> {
  const parameters = await api<ParameterSet[]>("/api/admin/parameter-sets");
  const content = html`
    <div class="page-head"><div><h1>Parameter Sets</h1><p>Draft, publish, and preserve governed tax/capital assumptions.</p></div></div>
    <section class="panel"><div class="panel-head"><h2>Version list</h2><span class="pill">Published sets immutable</span></div>
      <table><thead><tr><th>Name</th><th>Status</th><th>Effective</th><th>Payload</th></tr></thead><tbody>
        ${parameters.map(p => `<tr><td class="name-cell"><strong>${escapeHtml(p.name)} ${escapeHtml(p.version)}</strong><span>ID ${p.id}</span></td><td>${badge(p.status)}</td><td>${escapeHtml(p.effective_date)}</td><td>${escapeHtml(JSON.stringify(p.payload))}</td></tr>`).join("")}
      </tbody></table>
    </section>`;
  setApp(shell(content, "parameters"));
  bindShell();
}

async function renderSharing(): Promise<void> {
  const [calculations, shares] = await Promise.all([api<Calculation[]>("/api/calculations"), api<Share[]>("/api/shares")]);
  const firstOwned = calculations.find(c => c.permission === "OWNER" || c.permission === "ADMIN_FULL");
  const content = html`
    <div class="page-head"><div><h1>Sharing And Revocation</h1><p>Grant view, edit, or values-only export access. Owners and admins can revoke.</p></div></div>
    <div class="grid">
      <section class="panel"><div class="panel-head"><h2>Current grants</h2><span class="pill">Audited</span></div>
        <table><thead><tr><th>Resource</th><th>Collaborator</th><th>Permission</th><th>Status</th><th class="action-cell">Actions</th></tr></thead><tbody>
          ${shares.map(s => `<tr><td>Calculation ${s.resource_id}</td><td class="name-cell"><strong>${escapeHtml(s.grantee_name)}</strong><span>${escapeHtml(s.grantee_soeid)}</span></td><td>${badge(s.permission_level)}</td><td>${s.revoked_at ? badge("Revoked") : badge("Active")}</td><td class="action-cell">${s.revoked_at ? "" : `<button class="button danger" data-revoke="${s.id}">Revoke</button>`}</td></tr>`).join("")}
        </tbody></table>
      </section>
      <aside class="panel"><div class="panel-head"><h2>Grant access</h2><span class="pill">Owner/Admin</span></div>
        <div class="panel-body">
          <form id="share-form">
            <div class="field"><label>Calculation</label><select name="resource_id">${calculations.map(c => `<option value="${c.id}" ${c.id === firstOwned?.id ? "selected" : ""}>${escapeHtml(c.name)}</option>`).join("")}</select></div>
            <div class="field"><label>Grantee SOEID</label><input name="grantee_soeid" value="apatel"></div>
            <div class="field"><label>Permission</label><select name="permission_level"><option>VIEW</option><option selected>EDIT</option><option>EXPORT_VALUES</option></select></div>
            <button class="button primary" type="submit">Grant access</button>
          </form>
        </div>
      </aside>
    </div>`;
  setApp(shell(content, "sharing"));
  bindShell();
  document.querySelector<HTMLFormElement>("#share-form")?.addEventListener("submit", async event => {
    event.preventDefault();
    const f = new FormData(event.currentTarget as HTMLFormElement);
    await api<Share>("/api/shares", { method: "POST", body: JSON.stringify({ resource_id: Number(f.get("resource_id")), grantee_soeid: f.get("grantee_soeid"), permission_level: f.get("permission_level") }) });
    await renderSharing();
  });
  document.querySelectorAll<HTMLButtonElement>("[data-revoke]").forEach(button => button.addEventListener("click", async () => {
    await api<Share>(`/api/shares/${button.dataset.revoke}`, { method: "DELETE" });
    await renderSharing();
  }));
}

async function renderAudit(): Promise<void> {
  const events = await api<AuditEvent[]>("/api/audit-events");
  const content = html`
    <div class="page-head"><div><h1>Activity And Audit</h1><p>Significant access, run, parameter, and sharing events.</p></div></div>
    <section class="panel"><div class="panel-head"><h2>Audit events</h2><span class="pill">Scoped by role</span></div>
      <table><thead><tr><th>Event</th><th>Resource</th><th>Metadata</th><th>Timestamp</th></tr></thead><tbody>
        ${events.map(e => `<tr><td>${escapeHtml(e.event_type)}</td><td>${escapeHtml(e.resource_type)} ${escapeHtml(e.resource_id ?? "")}</td><td>${escapeHtml(JSON.stringify(e.metadata))}</td><td>${new Date(e.created_at).toLocaleString()}</td></tr>`).join("")}
      </tbody></table>
    </section>`;
  setApp(shell(content, "audit"));
  bindShell();
}

async function render(): Promise<void> {
  if (!token) {
    renderLogin();
    return;
  }
  try {
    currentUser = await api<User>("/api/auth/me");
  } catch {
    token = "";
    localStorage.removeItem("ecw_token");
    renderLogin();
    return;
  }
  if (route === "dashboard") await renderDashboard();
  else if (route === "calculation-new") await renderNewCalculation();
  else if (route === "admin") await renderAdmin();
  else if (route === "parameters") await renderParameters();
  else if (route === "sharing") await renderSharing();
  else if (route === "audit") await renderAudit();
  else await renderDashboard();
}

void render();
