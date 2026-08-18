// Pipeline Page - Bootstrap 5 Version
const PipelinePage = {
    render() {
        return `
        <div class="fade-in">
            <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-3 mb-4">
                <div>
                    <h3 class="h4 fw-bold text-dark mb-1">Pipeline Collection Engine</h3>
                    <p class="text-muted small mb-0">Trigger and monitor data collection runs</p>
                </div>
                <button onclick="PipelinePage.showTriggerModal()" class="btn btn-primary d-flex align-items-center gap-2">
                    <i class="bi bi-play-circle"></i> Trigger Pipeline
                </button>
            </div>

            <!-- Warehouse Status -->
            <div class="card border-0 shadow-sm bg-white p-4 mb-4" id="warehouseStatus">
                <h5 class="card-title h6 fw-bold mb-4"><i class="bi bi-database-fill text-success"></i> Warehouse Status</h5>
                <div class="row g-3 text-center" id="warehouseMetrics">
                    <div class="col-6 col-md-3">
                        <strong class="h4 fw-bold text-success d-block mb-1" id="whStatus">—</strong>
                        <span class="text-muted small" style="font-size: 0.75rem;">DB Status</span>
                    </div>
                    <div class="col-6 col-md-3 border-start border-light">
                        <strong class="h4 fw-bold text-dark d-block mb-1" id="whAccounts">—</strong>
                        <span class="text-muted small" style="font-size: 0.75rem;">Accounts</span>
                    </div>
                    <div class="col-6 col-md-3 border-start border-light">
                        <strong class="h4 fw-bold text-dark d-block mb-1" id="whContacts">—</strong>
                        <span class="text-muted small" style="font-size: 0.75rem;">Contacts</span>
                    </div>
                    <div class="col-6 col-md-3 border-start border-light">
                        <strong class="h4 fw-bold text-dark d-block mb-1" id="whSignals">—</strong>
                        <span class="text-muted small" style="font-size: 0.75rem;">Signals</span>
                    </div>
                </div>
            </div>

            <!-- Recent Runs -->
            <div class="card border-0 shadow-sm bg-white mb-4">
                <div class="card-header bg-white border-0 py-3">
                    <h5 class="card-title h6 fw-bold mb-0"><i class="bi bi-activity text-primary"></i> Recent Pipeline Runs</h5>
                </div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th class="ps-4">Account</th>
                                <th>Mode</th>
                                <th class="text-center">Status</th>
                                <th class="text-center" style="width: 180px;">Progress</th>
                                <th class="text-center">Records</th>
                                <th class="text-end pe-4">Cost</th>
                            </tr>
                        </thead>
                        <tbody id="pipelineRunsBody">
                            <!-- Dynamic Content -->
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Trigger Modal -->
            <div id="triggerModal" class="modal fade" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content border-0 shadow-lg">
                        <div class="modal-header">
                            <h5 class="modal-title fw-bold">Trigger Pipeline Collection</h5>
                            <button type="button" class="btn-close" onclick="$('#triggerModal').modal('hide')"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label small fw-semibold text-muted">Target Account</label>
                                <select id="triggerAccount" class="form-select"></select>
                            </div>
                            <div class="mb-0">
                                <label class="form-label small fw-semibold text-muted">Collection Mode</label>
                                <select id="triggerMode" class="form-select"></select>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" onclick="$('#triggerModal').modal('hide')" class="btn btn-sm btn-outline-secondary">Cancel</button>
                            <button type="button" onclick="PipelinePage.triggerRun()" class="btn btn-sm btn-primary">Trigger</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>`;
    },

    async load() {
        await Promise.all([PipelinePage.loadRuns(), PipelinePage.loadWarehouseStatus()]);
    },

    async loadWarehouseStatus() {
        try {
            const ws = await API.get('/pipeline/warehouse-status');
            const isConn = ws.database_status === 'CONNECTED' || ws.database_status === 'OK';
            $('#whStatus').text(ws.database_status || 'OK').removeClass('text-success text-danger').addClass(isConn ? 'text-success' : 'text-danger');
            $('#whAccounts').text(ws.total_accounts || 0);
            $('#whContacts').text(ws.total_contacts || 0);
            $('#whSignals').text(ws.total_signals || 0);
        } catch (e) { /* handled */ }
    },

    async loadRuns() {
        try {
            const runs = await API.get('/pipeline/runs', { limit: 20 });
            let html = '';
            if (!runs || runs.length === 0) {
                html = '<tr><td colspan="6" class="text-center text-muted py-4 small"><i class="bi bi-inbox me-1"></i> No pipeline runs yet</td></tr>';
            } else {
                runs.forEach(r => {
                    const statusColor = r.status === 'COMPLETED' ? 'bg-success-subtle text-success' : r.status === 'RUNNING' ? 'bg-primary-subtle text-primary' : r.status === 'FAILED' ? 'bg-danger-subtle text-danger' : 'bg-light text-secondary border';
                    const prog = r.progress_percent || 0;
                    
                    html += `
                    <tr>
                        <td class="ps-4 fw-semibold text-dark">${r.account_name || '—'}</td>
                        <td class="text-muted small">${r.collection_mode_label || r.collection_mode}</td>
                        <td class="text-center"><span class="badge ${statusColor}">${r.status}</span></td>
                        <td class="text-center">
                            <div class="d-flex align-items-center gap-2">
                                <div class="progress flex-grow-1" style="height: 6px;">
                                    <div class="progress-bar ${r.status === 'FAILED' ? 'bg-danger' : 'bg-primary'}" role="progressbar" style="width: ${prog}%"></div>
                                </div>
                                <span class="small text-muted" style="font-size: 0.75rem; min-width: 32px;">${prog}%</span>
                            </div>
                        </td>
                        <td class="text-center fw-medium">${(r.records_created || 0) + (r.records_updated || 0)}</td>
                        <td class="text-end pe-4 fw-bold text-dark">$${(r.total_cost_usd || 0).toFixed(3)}</td>
                    </tr>`;
                });
            }
            $('#pipelineRunsBody').html(html);
        } catch (e) {
            $('#pipelineRunsBody').html('<tr><td colspan="6" class="text-center text-danger py-4 small">Failed to load runs</td></tr>');
        }
    },

    async showTriggerModal() {
        const modal = new bootstrap.Modal(document.getElementById('triggerModal'));
        modal.show();
        try {
            const [accounts, modes] = await Promise.all([
                API.get('/accounts', { limit: 100 }),
                API.get('/pipeline/modes')
            ]);
            let accOpts = '<option value="">Select account...</option>';
            (accounts || []).forEach(a => { accOpts += `<option value="${a.id}">${a.name}</option>`; });
            $('#triggerAccount').html(accOpts);

            let modeOpts = '';
            (modes || []).forEach(m => { modeOpts += `<option value="${m.key}">${m.label}</option>`; });
            $('#triggerMode').html(modeOpts);
        } catch (e) { /* handled */ }
    },

    async triggerRun() {
        const accountId = $('#triggerAccount').val();
        const mode = $('#triggerMode').val();
        if (!accountId || !mode) { App.toast('Please select account and mode'); return; }
        try {
            await API.post('/pipeline/trigger', { account_id: accountId, collection_mode: mode });
            App.toast('Pipeline triggered successfully');
            
            const modalEl = document.getElementById('triggerModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            
            PipelinePage.loadRuns();
        } catch (e) { /* handled */ }
    }
};
