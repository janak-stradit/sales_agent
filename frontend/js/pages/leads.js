// Leads Page - Bootstrap 5 Version
const LeadsPage = {
    render() {
        return `
        <div class="fade-in">
            <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-3 mb-4">
                <div>
                    <h3 class="h4 fw-bold text-dark mb-1">Executive Leads</h3>
                    <p class="text-muted small mb-0">Lead scoring and persona intelligence</p>
                </div>
                <button onclick="LeadsPage.recalculateAll()" class="btn btn-warning text-dark d-flex align-items-center gap-2">
                    <i class="bi bi-calculator"></i> Recalculate All Scores
                </button>
            </div>

            <!-- Filters -->
            <div class="card border-0 shadow-sm mb-4 bg-white">
                <div class="card-body d-flex flex-wrap gap-3 align-items-center py-3">
                    <select id="leadSeniority" class="form-select form-select-sm w-auto">
                        <option value="">All Seniority</option>
                        <option value="CXO">CXO</option>
                        <option value="VP">VP</option>
                        <option value="Director">Director</option>
                        <option value="Manager">Manager</option>
                    </select>
                    <select id="leadStatus" class="form-select form-select-sm w-auto">
                        <option value="">All Status</option>
                        <option value="Hot">Hot</option>
                        <option value="Warm">Warm</option>
                        <option value="Cold">Cold</option>
                    </select>
                    <select id="leadAuthority" class="form-select form-select-sm w-auto">
                        <option value="">All Authority</option>
                        <option value="final">Sole / Final</option>
                        <option value="shared">Shared</option>
                        <option value="influencer">Influencer</option>
                    </select>
                    <input type="number" id="leadMinScore" placeholder="Min Score" class="form-control form-control-sm w-auto" style="max-width: 120px;">
                    <button onclick="LeadsPage.load()" class="btn btn-sm btn-outline-secondary px-3">Filter</button>
                </div>
            </div>

            <!-- Leads Table -->
            <div class="card border-0 shadow-sm bg-white mb-4">
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th class="ps-4">Name</th>
                                <th>Title</th>
                                <th class="text-center">Seniority</th>
                                <th class="text-center">Score</th>
                                <th class="text-center">Status</th>
                                <th class="text-center">Authority</th>
                                <th class="text-end pe-4">Actions</th>
                            </tr>
                        </thead>
                        <tbody id="leadsTableBody">
                            <!-- Dynamic Content -->
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Lead Profile Modal -->
            <div id="leadProfileModal" class="modal fade" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered modal-lg">
                    <div class="modal-content border-0 shadow-lg">
                        <div class="modal-header">
                            <h5 class="modal-title fw-bold" id="leadProfileName">Lead Profile</h5>
                            <button type="button" class="btn-close" onclick="$('#leadProfileModal').modal('hide')"></button>
                        </div>
                        <div class="modal-body" id="leadProfileContent">
                            <div class="d-flex justify-content-center py-5">
                                <div class="loader"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>`;
    },

    async load() {
        const params = {
            seniority_tier: $('#leadSeniority').val() || undefined,
            lead_status: $('#leadStatus').val() || undefined,
            decision_authority: $('#leadAuthority').val() || undefined,
            min_score: $('#leadMinScore').val() || undefined,
            limit: 50
        };
        try {
            const leads = await API.get('/leads', params);
            let html = '';
            if (!leads || leads.length === 0) {
                html = '<tr><td colspan="7" class="text-center text-muted py-5 small"><i class="bi bi-inbox me-1"></i> No leads found</td></tr>';
            } else {
                leads.forEach(l => {
                    const isHot = l.lead_status === 'Hot';
                    const isWarm = l.lead_status === 'Warm';
                    const statusClass = isHot ? 'bg-danger-subtle text-danger' : isWarm ? 'bg-warning-subtle text-warning' : 'bg-info-subtle text-info';
                    const initials = l.avatar_initials || (l.full_name ? l.full_name.split(' ').map(n => n[0]).join('') : '?');

                    html += `
                    <tr>
                        <td class="ps-4">
                            <div class="d-flex align-items-center gap-2">
                                <div class="rounded-circle bg-primary-subtle text-primary fw-bold d-flex align-items-center justify-content-center" style="width: 34px; height: 34px; font-size: 0.8rem;">
                                    ${initials}
                                </div>
                                <div>
                                    <strong class="text-dark d-block" style="font-size: 0.9rem;">${l.full_name || '—'}</strong>
                                    <span class="text-muted small">${l.email || ''}</span>
                                </div>
                            </div>
                        </td>
                        <td class="text-muted truncate" style="max-width: 250px;">${l.title || '—'}</td>
                        <td class="text-center">
                            <span class="badge bg-purple-subtle text-purple" style="color: #6f42c1; background-color: rgba(111,66,193,0.12);">${l.seniority_tier || '—'}</span>
                        </td>
                        <td class="text-center fw-bold text-dark">${l.lead_score}</td>
                        <td class="text-center">
                            <span class="badge ${statusClass}">${l.lead_status}</span>
                        </td>
                        <td class="text-center text-muted small">${l.decision_authority || '—'}</td>
                        <td class="text-end pe-4">
                            <button onclick="LeadsPage.showProfile('${l.id}')" class="btn btn-sm btn-outline-primary py-1 px-2.5">
                                <i class="bi bi-person-badge"></i> Profile
                            </button>
                        </td>
                    </tr>`;
                });
            }
            $('#leadsTableBody').html(html);
        } catch (e) {
            $('#leadsTableBody').html('<tr><td colspan="7" class="text-center text-danger py-4 small">Failed to load leads</td></tr>');
        }
    },

    async showProfile(contactId) {
        const modal = new bootstrap.Modal(document.getElementById('leadProfileModal'));
        modal.show();
        $('#leadProfileContent').html('<div class="d-flex justify-content-center py-5"><div class="loader"></div></div>');
        try {
            const p = await API.get(`/leads/${contactId}/profile`);
            const initials = p.avatar_initials || (p.full_name ? p.full_name.split(' ').map(n => n[0]).join('') : '?');
            const scoreClass = p.lead_score >= 80 ? 'text-danger' : p.lead_score >= 50 ? 'text-warning' : 'text-info';

            let html = `
            <div class="container-fluid p-0">
                <div class="d-flex align-items-center gap-3 mb-4">
                    <div class="rounded-circle bg-primary-subtle text-primary d-flex align-items-center justify-content-center fw-bold text-large" style="width: 56px; height: 56px; font-size: 1.25rem;">
                        ${initials}
                    </div>
                    <div class="flex-grow-1 min-w-0">
                        <h4 class="h5 fw-bold text-dark mb-1">${p.full_name || '—'}</h4>
                        <p class="text-muted mb-1 small">${p.title || ''} ${p.organization ? '@ ' + p.organization : ''}</p>
                        <p class="text-muted small mb-0"><i class="bi bi-geo-alt me-1"></i> ${p.location || 'Unknown Location'}</p>
                    </div>
                    <div class="text-center bg-light px-3 py-2 rounded border">
                        <span class="h3 fw-bold d-block mb-0 ${scoreClass}">${p.lead_score}</span>
                        <span class="text-muted text-uppercase" style="font-size: 0.6rem; font-weight: 600;">Lead Score</span>
                    </div>
                </div>
                
                ${p.summary_bio ? `
                <div class="mb-4">
                    <div class="alert alert-light border p-3 mb-0 small text-dark">
                        <strong class="d-block mb-1 text-muted uppercase" style="font-size: 0.65rem;">Executive Biography</strong>
                        ${p.summary_bio}
                    </div>
                </div>` : ''}
                
                ${p.career_timeline && p.career_timeline.length ? `
                <div class="mb-4">
                    <h6 class="fw-bold mb-3 text-dark"><i class="bi bi-briefcase-fill text-primary"></i> Career History</h6>
                    <div class="position-relative ps-3 border-start border-light" style="margin-left: 10px;">
                        ${p.career_timeline.map(c => `
                            <div class="mb-3 position-relative">
                                <span class="d-inline-block rounded-circle bg-primary position-absolute" style="width: 8px; height: 8px; left: -19px; top: 6px;"></span>
                                <strong class="text-dark small d-block">${c.title}</strong>
                                <span class="text-muted small d-block">${c.company} &bull; ${c.start_date || ''} – ${c.end_date || 'Present'}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>` : ''}
                
                ${p.ai_insights ? `
                <div class="mb-0">
                    <h6 class="fw-bold mb-2 text-dark"><i class="bi bi-lightbulb-fill text-warning"></i> AI Personalization Insights</h6>
                    <div class="alert alert-info-subtle text-info-emphasis border-0 p-3 mb-0 small">
                        ${p.ai_insights}
                    </div>
                </div>` : ''}
            </div>`;
            $('#leadProfileName').text(p.full_name || 'Lead Profile');
            $('#leadProfileContent').html(html);
        } catch (e) {
            $('#leadProfileContent').html('<p class="text-danger text-center small py-3">Failed to load profile</p>');
        }
    },

    async recalculateAll() {
        if (!confirm('Recalculate all lead scores? This may take a moment.')) return;
        try {
            await API.post('/leads/recalculate-all');
            App.toast('Score recalculation triggered');
            LeadsPage.load();
        } catch (e) { /* handled */ }
    }
};
