// Dashboard Page - Enterprise Bootstrap 5 Version
const DashboardPage = {
    lastSearchResults: null,
    currentFilter: 'all',

    render() {
        return `
        <div class="fade-in">
            <!-- Enhanced Search Section -->
            <div class="card mb-4 border-0 shadow-sm bg-white p-4">
                <div class="search-container mx-auto w-100">
                    <div class="position-relative">
                        <i class="bi bi-search search-icon-inside"></i>
                        <input type="text" id="globalSearch" class="form-control search-box w-100" placeholder="Search people, accounts, roles, LOBs, signals...">
                        <span class="position-absolute end-0 top-50 translate-middle-y me-3 text-muted small d-none d-sm-inline" id="searchHint">Press Enter to search</span>
                    </div>
                    
                    <!-- Search History & Quick Tips -->
                    <div class="d-flex flex-wrap align-items-center gap-2 mt-3" id="searchHistoryContainer" style="display: none;">
                        <span class="text-muted small d-flex align-items-center gap-1">
                            <i class="bi bi-clock-history"></i> Recent:
                        </span>
                        <div id="searchHistoryList" class="d-flex gap-2 flex-wrap"></div>
                        <button onclick="DashboardPage.clearHistory()" class="btn btn-link btn-sm text-danger p-0 ms-2 text-decoration-none" style="font-size: 0.75rem;">
                            <i class="bi bi-trash"></i> Clear
                        </button>
                    </div>

                    <!-- Enhanced Search Results Dropdown -->
                    <div id="searchResults" class="search-results-dropdown d-none">
                        <!-- Category Filters inside Dropdown -->
                        <div class="px-3 py-2 border-bottom bg-light d-flex gap-2 align-items-center justify-content-between">
                            <span class="small fw-semibold text-secondary">Search Results</span>
                            <div class="btn-group btn-group-sm" role="group" id="searchCategoryFilters">
                                <button type="button" class="btn btn-outline-secondary active py-0 px-2" data-filter="all" style="font-size: 0.75rem;">All</button>
                                <button type="button" class="btn btn-outline-secondary py-0 px-2" data-filter="people" style="font-size: 0.75rem;">People</button>
                                <button type="button" class="btn btn-outline-secondary py-0 px-2" data-filter="accounts" style="font-size: 0.75rem;">Accounts</button>
                                <button type="button" class="btn btn-outline-secondary py-0 px-2" data-filter="signals" style="font-size: 0.75rem;">Signals</button>
                            </div>
                        </div>
                        <div id="searchResultsBody"></div>
                    </div>
                </div>
            </div>

            <!-- Account Filter -->
            <div class="card mb-4 shadow-sm border-0 bg-white">
                <div class="card-body py-3 d-flex align-items-center gap-3">
                    <label for="dashAccountFilter" class="form-label mb-0 fw-semibold text-muted small">Target Account:</label>
                    <select id="dashAccountFilter" class="form-select form-select-sm w-auto" style="min-width: 200px;">
                        <option value="">All Accounts</option>
                    </select>
                    <button onclick="DashboardPage.loadWithFilter()" class="btn btn-sm btn-outline-primary px-3">
                        <i class="bi bi-funnel-fill"></i> Apply Filter
                    </button>
                </div>
            </div>

            <!-- KPI Cards -->
            <div class="row row-cols-1 row-cols-md-3 row-cols-lg-5 g-3 mb-4" id="kpiCards">
                <div class="col">
                    <div class="card h-100 border-0 shadow-sm bg-white p-3 mb-0 hover-up" style="border-radius: 12px; border-left: 4px solid #0d6efd !important;">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <div>
                                <p class="text-uppercase text-muted small fw-bold mb-1" style="font-size: 0.65rem; letter-spacing: 0.05em;">Target Accounts</p>
                                <h3 class="fw-extrabold mb-0 text-dark" id="kpiAccounts">—</h3>
                            </div>
                            <div class="rounded-3 bg-primary-subtle p-2 text-primary d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                                <i class="bi bi-building fs-5"></i>
                            </div>
                        </div>
                        <div class="d-flex align-items-center gap-1 mt-2">
                            <span class="badge bg-success-subtle text-success py-1 px-2" style="font-size: 0.65rem;"><i class="bi bi-arrow-up-short"></i> +8.2%</span>
                            <span class="text-muted" style="font-size: 0.65rem;">vs last month</span>
                        </div>
                    </div>
                </div>
                <div class="col">
                    <div class="card h-100 border-0 shadow-sm bg-white p-3 mb-0 hover-up" style="border-radius: 12px; border-left: 4px solid #198754 !important;">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <div>
                                <p class="text-uppercase text-muted small fw-bold mb-1" style="font-size: 0.65rem; letter-spacing: 0.05em;">Total Leads</p>
                                <h3 class="fw-extrabold mb-0 text-dark" id="kpiLeads">—</h3>
                            </div>
                            <div class="rounded-3 bg-success-subtle p-2 text-success d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                                <i class="bi bi-people-fill fs-5"></i>
                            </div>
                        </div>
                        <div class="d-flex align-items-center gap-1 mt-2">
                            <span class="badge bg-success-subtle text-success py-1 px-2" style="font-size: 0.65rem;"><i class="bi bi-arrow-up-short"></i> +12.4%</span>
                            <span class="text-muted" style="font-size: 0.65rem;">new this week</span>
                        </div>
                    </div>
                </div>
                <div class="col">
                    <div class="card h-100 border-0 shadow-sm bg-white p-3 mb-0 hover-up" style="border-radius: 12px; border-left: 4px solid var(--accent-primary) !important;">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <div>
                                <p class="text-uppercase text-muted small fw-bold mb-1" style="font-size: 0.65rem; letter-spacing: 0.05em;">Decision Makers</p>
                                <h3 class="fw-extrabold mb-0 text-dark" id="kpiDM">—</h3>
                            </div>
                            <div class="rounded-3 bg-accent-primary-soft p-2 text-accent-primary d-flex align-items-center justify-content-center" style="width: 40px; height: 40px; color: var(--accent-primary); background-color: rgba(138, 98, 72, 0.15) !important;">
                                <i class="bi bi-shield-check fs-5"></i>
                            </div>
                        </div>
                        <div class="d-flex align-items-center gap-1 mt-2">
                            <span class="badge bg-accent-primary-soft text-accent-primary py-1 px-2" style="font-size: 0.65rem; color: var(--accent-primary); background-color: rgba(138, 98, 72, 0.15) !important;">Coverage</span>
                            <span class="text-muted" style="font-size: 0.65rem;">76% of total leads</span>
                        </div>
                    </div>
                </div>
                <div class="col">
                    <div class="card h-100 border-0 shadow-sm bg-white p-3 mb-0 hover-up" style="border-radius: 12px; border-left: 4px solid #ffc107 !important;">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <div>
                                <p class="text-uppercase text-muted small fw-bold mb-1" style="font-size: 0.65rem; letter-spacing: 0.05em;">Active Signals</p>
                                <h3 class="fw-extrabold mb-0 text-dark" id="kpiSignals">—</h3>
                            </div>
                            <div class="rounded-3 bg-warning-subtle p-2 text-warning d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                                <i class="bi bi-lightning-charge-fill fs-5"></i>
                            </div>
                        </div>
                        <div class="d-flex align-items-center gap-1 mt-2">
                            <span class="badge bg-danger-subtle text-danger py-1 px-2" style="font-size: 0.65rem;">Priority</span>
                            <span class="text-muted" style="font-size: 0.65rem;">Real-time stream</span>
                        </div>
                    </div>
                </div>
                <div class="col">
                    <div class="card h-100 border-0 shadow-sm bg-white p-3 mb-0 hover-up" style="border-radius: 12px; border-left: 4px solid #0dcaf0 !important;">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <div>
                                <p class="text-uppercase text-muted small fw-bold mb-1" style="font-size: 0.65rem; letter-spacing: 0.05em;">Revenue Covered</p>
                                <h3 class="fw-extrabold mb-0 text-dark" id="kpiRevenue">—</h3>
                            </div>
                            <div class="rounded-3 bg-info-subtle p-2 text-info d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                                <i class="bi bi-cash-coin fs-5"></i>
                            </div>
                        </div>
                        <div class="d-flex align-items-center gap-1 mt-2">
                            <span class="badge bg-info-subtle text-info py-1 px-2" style="font-size: 0.65rem;">Valued</span>
                            <span class="text-muted" style="font-size: 0.65rem;">92% target coverage</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Distribution & Seniority charts -->
            <div class="row g-4 mb-4">
                <!-- Score Distribution -->
                <div class="col-12 col-lg-6">
                    <div class="card border-0 shadow-sm bg-white p-4 h-100 mb-0">
                        <h5 class="card-title h6 fw-bold mb-4"><i class="bi bi-bar-chart-fill text-primary"></i> Lead Score Distribution</h5>
                        <div id="scoreDistribution" class="d-flex flex-column gap-3">
                            <div>
                                <div class="d-flex justify-content-between mb-1">
                                    <span class="small"><i class="bi bi-circle-fill text-danger me-2"></i>Hot (&ge;80)</span>
                                    <span class="small fw-bold" id="scoreHot">—</span>
                                </div>
                                <div class="progress" style="height: 8px;">
                                    <div id="scoreHotBar" class="progress-bar bg-danger" role="progressbar" style="width: 0%"></div>
                                </div>
                            </div>
                            <div>
                                <div class="d-flex justify-content-between mb-1">
                                    <span class="small"><i class="bi bi-circle-fill text-warning me-2"></i>Warm (50-79)</span>
                                    <span class="small fw-bold" id="scoreWarm">—</span>
                                </div>
                                <div class="progress" style="height: 8px;">
                                    <div id="scoreWarmBar" class="progress-bar bg-warning" role="progressbar" style="width: 0%"></div>
                                </div>
                            </div>
                            <div>
                                <div class="d-flex justify-content-between mb-1">
                                    <span class="small"><i class="bi bi-circle-fill text-info me-2"></i>Cold (&lt;50)</span>
                                    <span class="small fw-bold" id="scoreCold">—</span>
                                </div>
                                <div class="progress" style="height: 8px;">
                                    <div id="scoreColdBar" class="progress-bar bg-info" role="progressbar" style="width: 0%"></div>
                                </div>
                            </div>
                        </div>
                        <div class="mt-4 pt-3 border-top d-flex justify-content-between text-muted small">
                            <span>Avg Score: <strong class="text-dark" id="scoreAvg">—</strong></span>
                            <span>Total Leads: <strong class="text-dark" id="scoreTotal">—</strong></span>
                        </div>
                    </div>
                </div>

                <!-- Seniority Breakdown -->
                <div class="col-12 col-lg-6">
                    <div class="card border-0 shadow-sm bg-white p-4 h-100 mb-0">
                        <h5 class="card-title h6 fw-bold mb-3"><i class="bi bi-diagram-2-fill text-info"></i> Seniority Breakdown</h5>
                        <div id="seniorityList" class="d-flex flex-column gap-2" style="max-height: 250px; overflow-y: auto;">
                            <!-- Dynamic Content -->
                        </div>
                    </div>
                </div>
            </div>

            <!-- Top Target Accounts Table -->
            <div class="card border-0 shadow-sm bg-white mb-4">
                <div class="card-header bg-white border-0 py-3">
                    <h5 class="card-title h6 fw-bold mb-0"><i class="bi bi-star-fill text-warning"></i> Top Target Accounts</h5>
                </div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th class="ps-4">Account</th>
                                <th>Industry</th>
                                <th class="text-center">Leads</th>
                                <th class="text-center">DMs</th>
                                <th class="text-center">Hot</th>
                                <th class="text-center">Signals</th>
                                <th class="text-end pe-4">Revenue</th>
                            </tr>
                        </thead>
                        <tbody id="topAccountsBody">
                            <!-- Dynamic Content -->
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Recent Signals -->
            <div class="card border-0 shadow-sm bg-white mb-0">
                <div class="card-header bg-white border-0 py-3">
                    <h5 class="card-title h6 fw-bold mb-0"><i class="bi bi-bell-fill text-danger"></i> Recent Intent & Buying Signals</h5>
                </div>
                <div class="card-body pt-0">
                    <div id="recentSignalsList" class="d-flex flex-column gap-3">
                        <!-- Dynamic Content -->
                    </div>
                </div>
            </div>
        </div>`;
    },

    async load() {
        // Load accounts for filter dropdown
        try {
            const accounts = await API.get('/accounts', { limit: 100 });
            let opts = '<option value="">All Accounts</option>';
            (accounts || []).forEach(a => { opts += `<option value="${a.name}">${a.name}</option>`; });
            $('#dashAccountFilter').html(opts);
        } catch(e) {}

        // Load dashboard data
        await DashboardPage.loadWithFilter();

        // Setup search & history
        DashboardPage.initSearch();
        DashboardPage.renderHistory();
    },

    async loadWithFilter() {
        const account = $('#dashAccountFilter').val() || undefined;
        try {
            const data = await API.get('/dashboard/overview', { account });
            const m = data.metrics;
            $('#kpiAccounts').text(m.total_target_accounts);
            $('#kpiLeads').text(m.total_leads_identified);
            $('#kpiDM').text(m.decision_makers_count);
            $('#kpiSignals').text(m.active_signals_count);
            $('#kpiRevenue').text(m.total_revenue_formatted || '$0');

            // Score distribution
            const sd = data.score_distribution;
            $('#scoreHot').text(sd.hot_count);
            $('#scoreWarm').text(sd.warm_count);
            $('#scoreCold').text(sd.cold_count);
            $('#scoreHotBar').css('width', sd.hot_percentage + '%');
            $('#scoreWarmBar').css('width', sd.warm_percentage + '%');
            $('#scoreColdBar').css('width', sd.cold_percentage + '%');
            $('#scoreAvg').text(sd.average_score ? sd.average_score.toFixed(1) : '—');
            $('#scoreTotal').text(sd.total_count || 0);

            // Seniority
            let senHtml = '';
            (data.seniority_distribution || []).forEach(s => {
                senHtml += `
                <div class="d-flex align-items-center justify-content-between py-2 border-bottom border-light">
                    <span class="small text-muted fw-semibold">${s.tier}</span>
                    <div class="d-flex align-items-center gap-3">
                        <span class="text-muted small" style="font-size: 0.75rem;">${s.hot_count} hot &bull; ${s.decision_maker_count} DMs</span>
                        <div class="progress" style="width: 100px; height: 6px;">
                            <div class="progress-bar bg-info" role="progressbar" style="width: ${s.percentage}%"></div>
                        </div>
                        <span class="badge bg-secondary text-white ms-2" style="min-width: 25px;">${s.count}</span>
                    </div>
                </div>`;
            });
            $('#seniorityList').html(senHtml || '<p class="text-muted text-center small py-3">No data</p>');

            // Top Accounts
            let accHtml = '';
            (data.top_accounts || []).forEach(a => {
                const revenue = a.annual_revenue_usd ? `$${(a.annual_revenue_usd / 1e6).toFixed(0)}M` : '—';
                accHtml += `
                <tr class="cursor-pointer" onclick="App.navigate('accounts', '${a.account_id}')">
                    <td class="ps-4 fw-semibold text-primary">${a.name}</td>
                    <td class="text-muted">${a.industry || '—'}</td>
                    <td class="text-center fw-medium">${a.lead_count}</td>
                    <td class="text-center fw-medium">${a.decision_maker_count}</td>
                    <td class="text-center">
                        <span class="badge bg-danger-subtle text-danger px-2">${a.hot_lead_count}</span>
                    </td>
                    <td class="text-center fw-medium">${a.signal_count}</td>
                    <td class="text-end pe-4 fw-bold text-dark">${revenue}</td>
                </tr>`;
            });
            $('#topAccountsBody').html(accHtml || '<tr><td colspan="7" class="text-center text-muted py-4">No accounts found</td></tr>');

            // Recent Signals
            let sigHtml = '';
            (data.recent_signals || []).slice(0, 5).forEach(s => {
                const isCritical = s.priority === 'CRITICAL';
                const isHigh = s.priority === 'HIGH';
                const borderLeftColor = isCritical ? '#dc3545' : isHigh ? '#ffc107' : s.priority === 'MEDIUM' ? '#0d6efd' : '#6c757d';
                
                const priorityBadge = isCritical ? 'bg-danger-subtle text-danger' : isHigh ? 'bg-warning-subtle text-warning' : s.priority === 'MEDIUM' ? 'bg-primary-subtle text-primary' : 'bg-light text-secondary border';
                
                // Icon mapping
                let iconHtml = '<i class="bi bi-lightning-fill fs-5"></i>';
                let iconBg = 'bg-primary-subtle text-primary';
                if (s.signal_type === 'LEADERSHIP_CHANGE') {
                    iconHtml = '<i class="bi bi-person-fill-gear fs-5"></i>';
                    iconBg = 'bg-info-subtle text-info';
                } else if (s.signal_type === 'TECH_STACK_MODERNIZATION') {
                    iconHtml = '<i class="bi bi-cpu fs-5"></i>';
                    iconBg = 'bg-accent-primary-soft text-accent-primary';
                } else if (s.signal_type === 'EXPANSION') {
                    iconHtml = '<i class="bi bi-globe fs-5"></i>';
                    iconBg = 'bg-success-subtle text-success';
                } else if (s.signal_type === 'FUNDING') {
                    iconHtml = '<i class="bi bi-cash-stack fs-5"></i>';
                    iconBg = 'bg-warning-subtle text-warning';
                } else if (s.signal_type === 'HIRING_SURGE') {
                    iconHtml = '<i class="bi bi-briefcase fs-5"></i>';
                    iconBg = 'bg-secondary-subtle text-secondary';
                }

                // Intent confidence percentage based on priority
                const confidence = isCritical ? '96%' : isHigh ? '88%' : '74%';

                sigHtml += `
                <div class="card border-0 shadow-sm mb-0 hover-up bg-white p-3" style="border-left: 4px solid ${borderLeftColor} !important; border-radius: 12px;">
                    <div class="d-flex align-items-start gap-3">
                        <div class="rounded-circle ${iconBg} p-2 d-flex align-items-center justify-content-center flex-shrink-0" style="width: 42px; height: 42px;">
                            ${iconHtml}
                        </div>
                        <div class="flex-grow-1 min-w-0">
                            <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-1 mb-1">
                                <strong class="text-dark small text-truncate" style="font-size: 0.9rem; font-weight: 700;">${s.title || s.signal_type || '—'}</strong>
                                <span class="badge ${priorityBadge} text-uppercase" style="font-size: 0.65rem;">${s.priority}</span>
                            </div>
                            <div class="d-flex flex-wrap gap-2 align-items-center text-muted mb-2" style="font-size: 0.72rem;">
                                <span><i class="bi bi-building me-1"></i> ${s.account_name || 'Global Account'}</span>
                                <span class="text-secondary-emphasis">&bull;</span>
                                <span><i class="bi bi-clock me-1"></i> ${s.detected_at ? new Date(s.detected_at).toLocaleDateString() : 'Just now'}</span>
                                <span class="text-secondary-emphasis">&bull;</span>
                                <span class="badge bg-light text-dark border px-1.5" style="font-size: 0.65rem;"><i class="bi bi-shield-check text-success me-1"></i> ${confidence} Intent Strength</span>
                            </div>
                            ${s.summary ? `
                                <p class="text-muted small mb-2 lh-base" style="font-size: 0.8rem;">${s.summary}</p>
                            ` : ''}
                            ${s.recommended_action ? `
                                <div class="alert alert-light border-0 p-2 mb-0 mt-2 small text-primary-emphasis bg-primary-subtle d-flex align-items-center gap-2" style="font-size: 0.78rem; border-radius: 8px;">
                                    <i class="bi bi-arrow-right-circle-fill text-primary flex-shrink-0"></i>
                                    <span><strong>Action Recommendation:</strong> ${s.recommended_action}</span>
                                </div>
                            ` : ''}
                        </div>
                        <div class="ms-2 flex-shrink-0 align-self-center">
                            <button class="btn btn-sm btn-outline-primary px-3 py-1 fw-semibold" style="font-size: 0.75rem; border-radius: 8px;" onclick="App.navigate('signals')">
                                Playbook
                            </button>
                        </div>
                    </div>
                </div>`;
            });
            $('#recentSignalsList').html(sigHtml || '<div class="text-center text-muted py-4 small">No recent signals found</div>');
        } catch (e) {
            $('#mainContent').find('.fade-in').prepend('<div class="alert alert-danger" role="alert">Failed to load dashboard data. Ensure the backend is running.</div>');
        }
    },

    initSearch() {
        let searchTimeout;
        $(document).off('keyup', '#globalSearch').on('keyup', '#globalSearch', function(e) {
            clearTimeout(searchTimeout);
            const query = $(this).val().trim();
            if (e.key === 'Escape') {
                $('#searchResults').addClass('d-none');
                return;
            }
            if (query.length < 2) {
                $('#searchResults').addClass('d-none');
                return;
            }
            searchTimeout = setTimeout(() => DashboardPage.executeSearch(query), 300);
        });

        // Search Category Filters
        $(document).off('click', '#searchCategoryFilters button').on('click', '#searchCategoryFilters button', function(e) {
            e.preventDefault();
            $('#searchCategoryFilters button').removeClass('active');
            $(this).addClass('active');
            DashboardPage.currentFilter = $(this).data('filter');
            DashboardPage.renderSearchResults();
        });

        // Close search results when clicking outside
        $(document).on('click', function(e) {
            if (!$(e.target).closest('#globalSearch, #searchResults').length) {
                $('#searchResults').addClass('d-none');
            }
        });
    },

    async executeSearch(query) {
        if (!query) return;
        DashboardPage.saveHistory(query);
        try {
            const data = await API.get('/dashboard/search', { q: query, limit: 15 });
            DashboardPage.lastSearchResults = data;
            DashboardPage.renderSearchResults();
        } catch (e) {
            $('#searchResultsBody').html('<div class="p-3 text-center text-danger small">Search failed</div>');
            $('#searchResults').removeClass('d-none');
        }
    },

    renderSearchResults() {
        const data = DashboardPage.lastSearchResults;
        if (!data) return;

        let html = '';
        const f = DashboardPage.currentFilter;
        let totalCount = 0;

        // Contacts / People
        if ((f === 'all' || f === 'people') && data.contacts && data.contacts.length > 0) {
            html += '<div class="p-3 border-bottom"><p class="text-xs fw-bold text-muted text-uppercase mb-2"><i class="bi bi-people-fill text-primary"></i> People (' + data.contacts.length + ')</p>';
            data.contacts.forEach(c => {
                const isHot = c.lead_status === 'Hot';
                const isWarm = c.lead_status === 'Warm';
                const statusClass = isHot ? 'bg-danger-subtle text-danger' : isWarm ? 'bg-warning-subtle text-warning' : 'bg-info-subtle text-info';
                html += `
                <div class="d-flex align-items-center gap-3 py-2 px-2 rounded hover-bg-light cursor-pointer" onclick="App.navigate('leads'); setTimeout(() => LeadsPage.showProfile('${c.id}'), 300);">
                    <div class="rounded-circle bg-primary-subtle text-primary d-flex align-items-center justify-content-center fw-bold" style="width: 36px; height: 36px; font-size: 0.85rem;">
                        ${c.avatar_initials || c.full_name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div class="flex-grow-1 min-w-0">
                        <strong class="text-dark d-block truncate" style="font-size: 0.9rem;">${c.full_name}</strong>
                        <span class="text-muted small truncate d-block">${c.title} &bull; ${c.account_name}</span>
                    </div>
                    <div class="d-flex align-items-center gap-2">
                        <span class="badge ${statusClass}">${c.lead_status}</span>
                        <span class="badge bg-secondary">${c.lead_score}</span>
                    </div>
                </div>`;
            });
            html += '</div>';
            totalCount += data.contacts.length;
        }

        // Accounts
        if ((f === 'all' || f === 'accounts') && data.accounts && data.accounts.length > 0) {
            html += '<div class="p-3 border-bottom"><p class="text-xs fw-bold text-muted text-uppercase mb-2"><i class="bi bi-building text-info"></i> Accounts (' + data.accounts.length + ')</p>';
            data.accounts.forEach(a => {
                html += `
                <div class="d-flex align-items-center gap-3 py-2 px-2 rounded hover-bg-light cursor-pointer" onclick="AccountsPage.showDetail('${a.id}');">
                    <div class="rounded bg-info-subtle text-info d-flex align-items-center justify-content-center fw-bold" style="width: 36px; height: 36px; font-size: 0.9rem;">
                        ${a.name[0]}
                    </div>
                    <div class="flex-grow-1 min-w-0">
                        <strong class="text-dark d-block truncate" style="font-size: 0.9rem;">${a.name} ${a.publicly_traded_symbol ? '<span class="text-muted small">(' + a.publicly_traded_symbol + ')</span>' : ''}</strong>
                        <span class="text-muted small truncate d-block">${a.industry || 'Financial Services'} &bull; ${a.employee_count ? a.employee_count.toLocaleString() : '—'} Employees</span>
                    </div>
                    <span class="badge bg-light text-dark border">${a.leads_count || 0} leads</span>
                </div>`;
            });
            html += '</div>';
            totalCount += data.accounts.length;
        }

        // Signals
        if ((f === 'all' || f === 'signals') && data.signals && data.signals.length > 0) {
            html += '<div class="p-3"><p class="text-xs fw-bold text-muted text-uppercase mb-2"><i class="bi bi-lightning-charge-fill text-warning"></i> Signals (' + data.signals.length + ')</p>';
            data.signals.forEach(s => {
                const isCritical = s.priority === 'CRITICAL';
                const isHigh = s.priority === 'HIGH';
                const badgeColor = isCritical ? 'bg-danger' : isHigh ? 'bg-warning text-dark' : 'bg-info';
                html += `
                <div class="d-flex align-items-center gap-3 py-2 px-2 rounded hover-bg-light cursor-pointer" onclick="App.navigate('signals');">
                    <div class="rounded-circle bg-warning-subtle text-warning d-flex align-items-center justify-content-center" style="width: 36px; height: 36px;">
                        <i class="bi bi-lightning-fill"></i>
                    </div>
                    <div class="flex-grow-1 min-w-0">
                        <strong class="text-dark d-block truncate" style="font-size: 0.9rem;">${s.title}</strong>
                        <span class="text-muted small truncate d-block">${s.account_name} &bull; ${s.category || 'Sales Intent'}</span>
                    </div>
                    <span class="badge ${badgeColor}">${s.priority}</span>
                </div>`;
            });
            html += '</div>';
            totalCount += data.signals.length;
        }

        if (totalCount === 0) {
            html = `<div class="p-4 text-center text-muted small"><i class="bi bi-exclamation-circle me-1"></i> No results match the filter "${f}"</div>`;
        }

        $('#searchResultsBody').html(html);
        $('#searchResults').removeClass('d-none');
    },

    loadHistory() {
        try {
            return JSON.parse(localStorage.getItem('sales_ai_search_history')) || [];
        } catch(e) { return []; }
    },

    saveHistory(query) {
        if (!query || query.length < 2) return;
        let history = this.loadHistory();
        history = history.filter(h => h.toLowerCase() !== query.toLowerCase());
        history.unshift(query);
        history = history.slice(0, 5); // Max 5 recent queries
        localStorage.setItem('sales_ai_search_history', JSON.stringify(history));
        this.renderHistory();
    },

    clearHistory() {
        localStorage.removeItem('sales_ai_search_history');
        this.renderHistory();
    },

    renderHistory() {
        const history = this.loadHistory();
        if (history.length === 0) {
            $('#searchHistoryContainer').css('display', 'none');
            return;
        }
        $('#searchHistoryContainer').css('display', 'flex');
        let html = '';
        history.forEach(h => {
            html += `<span class="badge bg-light text-dark border history-tag px-2.5 py-1.5" onclick="DashboardPage.triggerHistorySearch('${h.replace(/'/g, "\\'")}')">${h}</span>`;
        });
        $('#searchHistoryList').html(html);
    },

    triggerHistorySearch(query) {
        $('#globalSearch').val(query);
        DashboardPage.executeSearch(query);
    }
};
