// Signals Page - Bootstrap 5 Version
const SignalsPage = {
    render() {
        return `
        <div class="fade-in">
            <div class="mb-4">
                <h3 class="h4 fw-bold text-dark mb-1">Sales Trigger Signals</h3>
                <p class="text-muted small mb-0">Buying events and modernization triggers</p>
            </div>

            <!-- Stats -->
            <div class="row g-3 mb-4" id="signalStats">
                <div class="col-6 col-md-3">
                    <div class="card border-0 shadow-sm bg-white p-3 text-center mb-0">
                        <h4 class="fw-bold text-danger mb-1" id="sigCritical">0</h4>
                        <span class="text-muted small" style="font-size: 0.75rem;">Critical</span>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="card border-0 shadow-sm bg-white p-3 text-center mb-0">
                        <h4 class="fw-bold text-warning mb-1" id="sigHigh">0</h4>
                        <span class="text-muted small" style="font-size: 0.75rem;">High</span>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="card border-0 shadow-sm bg-white p-3 text-center mb-0">
                        <h4 class="fw-bold text-primary mb-1" id="sigMedium">0</h4>
                        <span class="text-muted small" style="font-size: 0.75rem;">Medium</span>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="card border-0 shadow-sm bg-white p-3 text-center mb-0">
                        <h4 class="fw-bold text-secondary mb-1" id="sigLow">0</h4>
                        <span class="text-muted small" style="font-size: 0.75rem;">Low</span>
                    </div>
                </div>
            </div>

            <!-- Filters -->
            <div class="card border-0 shadow-sm bg-white mb-4">
                <div class="card-body d-flex flex-wrap gap-3 align-items-center py-3">
                    <select id="signalType" class="form-select form-select-sm w-auto">
                        <option value="">All Types</option>
                        <option value="LEADERSHIP_CHANGE">Leadership Change</option>
                        <option value="TECH_STACK_MODERNIZATION">Tech Modernization</option>
                        <option value="EXPANSION">Expansion</option>
                        <option value="FUNDING">Funding</option>
                        <option value="HIRING_SURGE">Hiring Surge</option>
                    </select>
                    <select id="signalPriority" class="form-select form-select-sm w-auto">
                        <option value="">All Priority</option>
                        <option value="CRITICAL">Critical</option>
                        <option value="HIGH">High</option>
                        <option value="MEDIUM">Medium</option>
                        <option value="LOW">Low</option>
                    </select>
                    <select id="signalStatus" class="form-select form-select-sm w-auto">
                        <option value="">All Status</option>
                        <option value="NEW">New</option>
                        <option value="ACTIONED">Actioned</option>
                        <option value="DISMISSED">Dismissed</option>
                    </select>
                    <button onclick="SignalsPage.loadSignals()" class="btn btn-sm btn-outline-secondary px-3">Filter</button>
                </div>
            </div>

            <!-- Signals List -->
            <div class="d-flex flex-column gap-3" id="signalsList"></div>
        </div>`;
    },

    async load() {
        await Promise.all([SignalsPage.loadStats(), SignalsPage.loadSignals()]);
    },

    async loadStats() {
        try {
            const stats = await API.get('/signals/stats');
            const byPriority = stats.by_priority || {};
            $('#sigCritical').text(byPriority.CRITICAL || 0);
            $('#sigHigh').text(byPriority.HIGH || 0);
            $('#sigMedium').text(byPriority.MEDIUM || 0);
            $('#sigLow').text(byPriority.LOW || 0);
        } catch (e) { /* handled */ }
    },

    async loadSignals() {
        const params = {
            signal_type: $('#signalType').val() || undefined,
            priority: $('#signalPriority').val() || undefined,
            status: $('#signalStatus').val() || undefined,
            limit: 50
        };
        try {
            const signals = await API.get('/signals', params);
            let html = '';
            if (!signals || signals.length === 0) {
                html = '<div class="text-center py-5 text-muted small"><i class="bi bi-bell-slash me-1"></i> No signals found</div>';
            } else {
                signals.forEach(s => {
                    const isCritical = s.priority === 'CRITICAL';
                    const isHigh = s.priority === 'HIGH';
                    const borderLeftColor = isCritical ? '#dc3545' : isHigh ? '#ffc107' : s.priority === 'MEDIUM' ? '#0d6efd' : '#6c757d';
                    
                    const statusBadge = s.status === 'NEW' ? 'bg-success-subtle text-success' : s.status === 'ACTIONED' ? 'bg-primary-subtle text-primary' : 'bg-light text-secondary border';
                    const priorityBadge = isCritical ? 'bg-danger-subtle text-danger' : isHigh ? 'bg-warning-subtle text-warning' : 'bg-light text-secondary border';

                    html += `
                    <div class="card border-0 shadow-sm bg-white p-4 mb-0" style="border-left: 5px solid ${borderLeftColor} !important;">
                        <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start gap-3">
                            <div class="flex-grow-1">
                                <div class="d-flex align-items-center gap-2 mb-2">
                                    <h4 class="h6 fw-bold text-dark mb-0">${s.title || s.signal_type}</h4>
                                    <span class="badge ${statusBadge}" style="font-size: 0.65rem;">${s.status}</span>
                                </div>
                                <p class="text-muted mb-2" style="font-size: 0.75rem;">
                                    <i class="bi bi-info-circle me-1"></i> ${s.signal_type || ''} &bull; <i class="bi bi-building me-1"></i> ${s.account_name || ''}
                                </p>
                                <p class="text-dark small mb-3 lh-base">${s.summary || ''}</p>
                                ${s.recommended_action ? `
                                    <div class="alert alert-light border-0 p-2 mb-0 small text-primary-emphasis bg-primary-subtle" style="font-size: 0.8rem;">
                                        <i class="bi bi-arrow-right-circle-fill me-1 text-primary"></i> ${s.recommended_action}
                                    </div>
                                ` : ''}
                            </div>
                            <div class="d-flex flex-sm-column align-items-end gap-2 ms-sm-3 min-w-auto text-end">
                                <span class="badge ${priorityBadge} text-uppercase" style="font-size: 0.65rem;">${s.priority}</span>
                                ${s.status === 'NEW' ? `
                                <div class="d-flex gap-1 mt-sm-2">
                                    <button onclick="SignalsPage.updateStatus('${s.id}', 'ACTIONED')" class="btn btn-xs btn-outline-primary py-1 px-2" style="font-size: 0.75rem;">Action</button>
                                    <button onclick="SignalsPage.updateStatus('${s.id}', 'DISMISSED')" class="btn btn-xs btn-outline-secondary py-1 px-2" style="font-size: 0.75rem;">Dismiss</button>
                                </div>` : ''}
                            </div>
                        </div>
                    </div>`;
                });
            }
            $('#signalsList').html(html);
        } catch (e) {
            $('#signalsList').html('<div class="text-center py-4 text-danger small">Failed to load signals</div>');
        }
    },

    async updateStatus(signalId, newStatus) {
        try {
            await API.patch(`/signals/${signalId}/status`, { status: newStatus });
            App.toast(`Signal marked as ${newStatus}`);
            SignalsPage.loadSignals();
        } catch (e) { /* handled */ }
    }
};
