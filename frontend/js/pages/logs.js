// Logs Page - Bootstrap 5 Version
const LogsPage = {
    render() {
        return `
        <div class="fade-in">
            <div class="mb-4">
                <h3 class="h4 fw-bold text-dark mb-1">Tool Execution Logs</h3>
                <p class="text-muted small mb-0">API call telemetry and performance tracking</p>
            </div>

            <!-- Stats -->
            <div class="row g-3 mb-4">
                <div class="col-6 col-md-3">
                    <div class="card border-0 shadow-sm bg-white p-3 text-center mb-0">
                        <h4 class="fw-bold text-primary mb-1" id="logTotal">0</h4>
                        <span class="text-muted small" style="font-size: 0.75rem;">Total Calls</span>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="card border-0 shadow-sm bg-white p-3 text-center mb-0">
                        <h4 class="fw-bold text-success mb-1" id="logSuccess">100%</h4>
                        <span class="text-muted small" style="font-size: 0.75rem;">Success Rate</span>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="card border-0 shadow-sm bg-white p-3 text-center mb-0">
                        <h4 class="fw-bold text-warning mb-1" id="logCost">$0</h4>
                        <span class="text-muted small" style="font-size: 0.75rem;">Total Cost</span>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="card border-0 shadow-sm bg-white p-3 text-center mb-0">
                        <h4 class="fw-bold text-accent-primary" id="logLatency" style="color: var(--accent-primary);">0s</h4>
                        <span class="text-muted small" style="font-size: 0.75rem;">Avg Latency</span>
                    </div>
                </div>
            </div>

            <!-- Filters -->
            <div class="card border-0 shadow-sm bg-white mb-4">
                <div class="card-body d-flex flex-wrap gap-3 align-items-center py-3">
                    <input type="text" id="logProvider" placeholder="Provider..." class="form-control form-control-sm w-auto" style="max-width: 150px;">
                    <input type="text" id="logEndpoint" placeholder="Endpoint..." class="form-control form-control-sm w-auto" style="max-width: 150px;">
                    <select id="logStatus" class="form-select form-select-sm w-auto">
                        <option value="">All Status</option>
                        <option value="SUCCESS">Success</option>
                        <option value="FAILED">Failed</option>
                        <option value="TIMEOUT">Timeout</option>
                    </select>
                    <button onclick="LogsPage.loadLogs()" class="btn btn-sm btn-outline-secondary px-3">Filter</button>
                </div>
            </div>

            <!-- Logs Table -->
            <div class="card border-0 shadow-sm bg-white mb-4">
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th class="ps-4">Provider</th>
                                <th>Endpoint</th>
                                <th class="text-center">Status</th>
                                <th class="text-center">Cost</th>
                                <th class="text-center">Latency</th>
                                <th class="pe-4 text-end">Account</th>
                            </tr>
                        </thead>
                        <tbody id="logsTableBody">
                            <!-- Dynamic Content -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>`;
    },

    async load() {
        await Promise.all([LogsPage.loadStats(), LogsPage.loadLogs()]);
    },

    async loadStats() {
        try {
            const stats = await API.get('/logs/stats');
            $('#logTotal').text(stats.total_tool_calls || 0);
            $('#logSuccess').text((stats.success_rate_percent || 100) + '%');
            $('#logCost').text('$' + (stats.total_cost_usd || 0).toFixed(3));
            $('#logLatency').text((stats.avg_latency_seconds || 0).toFixed(2) + 's');
        } catch (e) { /* handled */ }
    },

    async loadLogs() {
        const params = {
            provider: $('#logProvider').val() || undefined,
            endpoint: $('#logEndpoint').val() || undefined,
            status: $('#logStatus').val() || undefined,
            limit: 50
        };
        try {
            const logs = await API.get('/logs', params);
            let html = '';
            if (!logs || logs.length === 0) {
                html = '<tr><td colspan="6" class="text-center text-muted py-4 small"><i class="bi bi-inbox me-1"></i> No logs found</td></tr>';
            } else {
                logs.forEach(l => {
                    const isSuccess = l.status === 'SUCCESS' || l.status === 'COMPLETED';
                    const statusColor = isSuccess ? 'bg-success-subtle text-success' : l.status === 'FAILED' ? 'bg-danger-subtle text-danger' : 'bg-light text-secondary border';
                    html += `
                    <tr>
                        <td class="ps-4 fw-semibold text-dark">${l.provider || '—'}</td>
                        <td class="text-muted small font-mono">${l.endpoint || '—'}</td>
                        <td class="text-center"><span class="badge ${statusColor}">${l.status}</span></td>
                        <td class="text-center fw-medium">$${(l.reported_cost_value || 0).toFixed(4)}</td>
                        <td class="text-center fw-medium">${(l.overall_latency || 0).toFixed(2)}s</td>
                        <td class="pe-4 text-end text-muted small">${l.account_name || '—'}</td>
                    </tr>`;
                });
            }
            $('#logsTableBody').html(html);
        } catch (e) {
            $('#logsTableBody').html('<tr><td colspan="6" class="text-center text-danger py-4 small">Failed to load logs</td></tr>');
        }
    }
};
