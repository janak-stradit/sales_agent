// Accounts Page - Bootstrap 5 Version
const AccountsPage = {
    render() {
        return `
        <div class="fade-in">
            <!-- Header + Actions -->
            <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-3 mb-4">
                <div>
                    <h3 class="h4 fw-bold text-dark mb-1">Target Accounts</h3>
                    <p class="text-muted small mb-0">Enterprise organizations in your pipeline</p>
                </div>
                <button onclick="AccountsPage.showCreateModal()" class="btn btn-primary d-flex align-items-center gap-2">
                    <i class="bi bi-plus-lg"></i> Add Account
                </button>
            </div>

            <!-- Filters -->
            <div class="card border-0 shadow-sm mb-4 bg-white">
                <div class="card-body d-flex flex-wrap gap-3 align-items-center py-3">
                    <div class="position-relative" style="width: 250px;">
                        <input type="text" id="accountSearch" placeholder="Search accounts..." class="form-control form-control-sm ps-4">
                        <i class="bi bi-search position-absolute start-0 top-50 translate-middle-y ms-2 text-muted" style="font-size: 0.8rem;"></i>
                    </div>
                    <select id="accountIndustry" class="form-select form-select-sm w-auto">
                        <option value="">All Industries</option>
                        <option value="Technology">Technology</option>
                        <option value="Finance">Finance</option>
                        <option value="Healthcare">Healthcare</option>
                        <option value="Manufacturing">Manufacturing</option>
                        <option value="Retail">Retail</option>
                    </select>
                    <button onclick="AccountsPage.load()" class="btn btn-sm btn-outline-secondary px-3">Filter</button>
                </div>
            </div>

            <!-- Accounts Grid -->
            <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4" id="accountsGrid"></div>

            <!-- Create Account Modal -->
            <div id="createAccountModal" class="modal fade" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content border-0 shadow-lg">
                        <div class="modal-header">
                            <h5 class="modal-title fw-bold">Add New Account</h5>
                            <button type="button" class="btn-close" onclick="$('#createAccountModal').modal('hide')"></button>
                        </div>
                        <form id="createAccountForm">
                            <div class="modal-body">
                                <div class="mb-3">
                                    <label class="form-label small fw-semibold text-muted">Company Name *</label>
                                    <input type="text" name="name" required class="form-control">
                                </div>
                                <div class="row g-3 mb-3">
                                    <div class="col">
                                        <label class="form-label small fw-semibold text-muted">Domain</label>
                                        <input type="text" name="domain" placeholder="example.com" class="form-control">
                                    </div>
                                    <div class="col">
                                        <label class="form-label small fw-semibold text-muted">Industry</label>
                                        <input type="text" name="industry" class="form-control">
                                    </div>
                                </div>
                                <div class="row g-3 mb-3">
                                    <div class="col">
                                        <label class="form-label small fw-semibold text-muted">Employees</label>
                                        <input type="number" name="employee_count" class="form-control">
                                    </div>
                                    <div class="col">
                                        <label class="form-label small fw-semibold text-muted">Revenue (USD)</label>
                                        <input type="number" name="annual_revenue_usd" class="form-control">
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small fw-semibold text-muted">Website URL</label>
                                    <input type="url" name="website_url" class="form-control">
                                </div>
                                <div class="mb-0">
                                    <label class="form-label small fw-semibold text-muted">Headquarters</label>
                                    <input type="text" name="headquarters" class="form-control">
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" onclick="$('#createAccountModal').modal('hide')" class="btn btn-sm btn-outline-secondary">Cancel</button>
                                <button type="submit" class="btn btn-sm btn-primary">Create Account</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Account Detail Modal -->
            <div id="accountDetailModal" class="modal fade" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered modal-lg">
                    <div class="modal-content border-0 shadow-lg">
                        <div class="modal-header">
                            <h5 class="modal-title fw-bold" id="detailAccountName">Account Details</h5>
                            <button type="button" class="btn-close" onclick="$('#accountDetailModal').modal('hide')"></button>
                        </div>
                        <div class="modal-body" id="accountDetailContent">
                            <div class="d-flex justify-content-center py-5">
                                <div class="loader"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>`;
    },

    showCreateModal() {
        const modal = new bootstrap.Modal(document.getElementById('createAccountModal'));
        modal.show();
    },

    async load() {
        const search = $('#accountSearch').val() || '';
        const industry = $('#accountIndustry').val() || '';
        try {
            const accounts = await API.get('/accounts', { search, industry, limit: 50 });
            let html = '';
            if (!accounts || accounts.length === 0) {
                html = '<div class="col-12 text-center py-5 text-muted small"><i class="bi bi-inbox me-1"></i> No accounts found</div>';
            } else {
                accounts.forEach(a => {
                    const revenue = a.annual_revenue_usd ? `$${(a.annual_revenue_usd / 1e6).toFixed(0)}M` : '—';
                    html += `
                    <div class="col">
                        <div class="card h-100 border-0 shadow-sm bg-white p-4 cursor-pointer" onclick="AccountsPage.showDetail('${a.id}')">
                            <div class="d-flex items-start justify-content-between mb-3">
                                <div class="flex-grow-1 min-w-0">
                                    <h4 class="h6 fw-bold text-dark truncate mb-1">${a.name}</h4>
                                    <p class="text-muted small truncate mb-0">${a.domain || a.industry || '—'}</p>
                                </div>
                                <div class="rounded-circle bg-light d-flex align-items-center justify-content-center fw-bold text-secondary ms-2" style="width: 40px; height: 40px; min-width: 40px;">
                                    ${a.name ? a.name[0] : '?'}
                                </div>
                            </div>
                            <div class="row g-2 text-center py-3 border-top border-bottom border-light">
                                <div class="col-4 border-end border-light">
                                    <h5 class="fw-bold text-primary mb-0">${a.lead_count || 0}</h5>
                                    <span class="text-muted text-uppercase" style="font-size: 0.65rem;">Leads</span>
                                </div>
                                <div class="col-4 border-end border-light">
                                    <h5 class="fw-bold text-accent-primary mb-0" style="color: var(--accent-primary);">${a.decision_maker_count || 0}</h5>
                                    <span class="text-muted text-uppercase" style="font-size: 0.65rem;">DMs</span>
                                </div>
                                <div class="col-4">
                                    <h5 class="fw-bold text-success mb-0">${revenue}</h5>
                                    <span class="text-muted text-uppercase" style="font-size: 0.65rem;">Revenue</span>
                                </div>
                            </div>
                            <div class="d-flex justify-content-between align-items-center mt-3 small text-muted">
                                <span><i class="bi bi-tags me-1"></i> ${a.industry || '—'}</span>
                                <span><i class="bi bi-people me-1"></i> ${a.employee_count ? a.employee_count.toLocaleString() : '—'}</span>
                            </div>
                        </div>
                    </div>`;
                });
            }
            $('#accountsGrid').html(html);
        } catch (e) {
            $('#accountsGrid').html('<div class="col-12 text-center py-4 text-danger small">Failed to load accounts</div>');
        }
    },

    async showDetail(accountId) {
        const modal = new bootstrap.Modal(document.getElementById('accountDetailModal'));
        modal.show();
        $('#accountDetailContent').html('<div class="d-flex justify-content-center py-5"><div class="loader"></div></div>');
        try {
            const data = await API.get(`/accounts/${accountId}/360`);
            let html = `
            <div class="container-fluid p-0">
                <div class="row g-3 text-center mb-4">
                    <div class="col-6 col-sm-3 py-2 bg-light rounded border border-white">
                        <span class="text-muted small d-block">Industry</span>
                        <strong class="text-dark">${data.industry || '—'}</strong>
                    </div>
                    <div class="col-6 col-sm-3 py-2 bg-light rounded border border-white">
                        <span class="text-muted small d-block">Employees</span>
                        <strong class="text-dark">${data.employee_count ? data.employee_count.toLocaleString() : '—'}</strong>
                    </div>
                    <div class="col-6 col-sm-3 py-2 bg-light rounded border border-white">
                        <span class="text-muted small d-block">Revenue</span>
                        <strong class="text-dark">${data.annual_revenue_usd ? '$' + (data.annual_revenue_usd / 1e6).toFixed(0) + 'M' : '—'}</strong>
                    </div>
                    <div class="col-6 col-sm-3 py-2 bg-light rounded border border-white">
                        <span class="text-muted small d-block">Domain</span>
                        <strong class="text-dark">${data.domain || '—'}</strong>
                    </div>
                </div>
                ${data.lobs && data.lobs.length ? `
                <div class="mb-4">
                    <h6 class="fw-bold mb-2 text-dark"><i class="bi bi-grid-fill text-primary"></i> Lines of Business (${data.lobs.length})</h6>
                    <div class="list-group list-group-flush border rounded">
                        ${data.lobs.map(l => `
                            <div class="list-group-item d-flex justify-content-between align-items-center py-2 px-3">
                                <span>${l.name}</span>
                                <span class="badge bg-secondary-subtle text-secondary">${l.entity_type || 'LOB'}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>` : ''}
                ${data.signals && data.signals.length ? `
                <div>
                    <h6 class="fw-bold mb-2 text-dark"><i class="bi bi-lightning-fill text-warning"></i> Recent Buying Signals (${data.signals.length})</h6>
                    <div class="list-group list-group-flush border rounded">
                        ${data.signals.slice(0, 5).map(s => `
                            <div class="list-group-item d-flex justify-content-between align-items-center py-2 px-3">
                                <span class="small fw-semibold">${s.title || s.signal_type}</span>
                                <span class="badge ${s.priority === 'CRITICAL' ? 'bg-danger' : s.priority === 'HIGH' ? 'bg-warning text-dark' : 'bg-info'}">${s.priority || 'MEDIUM'}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>` : ''}
            </div>`;
            $('#detailAccountName').text(data.name || 'Account Details');
            $('#accountDetailContent').html(html);
        } catch (e) {
            $('#accountDetailContent').html('<p class="text-danger small py-3 text-center">Failed to load account details</p>');
        }
    },

    init() {
        $(document).off('submit', '#createAccountForm').on('submit', '#createAccountForm', async function(e) {
            e.preventDefault();
            const formData = {};
            $(this).serializeArray().forEach(f => { if (f.value) formData[f.name] = f.value; });
            if (formData.employee_count) formData.employee_count = parseInt(formData.employee_count);
            if (formData.annual_revenue_usd) formData.annual_revenue_usd = parseInt(formData.annual_revenue_usd);
            try {
                await API.post('/accounts', formData);
                const modalEl = document.getElementById('createAccountModal');
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
                App.toast('Account created successfully');
                AccountsPage.load();
            } catch (e) { /* handled in API */ }
        });
    }
};
