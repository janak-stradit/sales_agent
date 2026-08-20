// Discovery Page — Loads Accounts, LOBs, Sub LOBs, Personas with time filters
$(document).ready(function () {
    let currentFilter = 'daily';

    // Time filter buttons
    $(document).on('click', '.discovery-time-filter', function () {
        $('.discovery-time-filter').removeClass('active').css({ 'border-color': '#e2e8f0', 'color': '#64748b', 'background-color': '' });
        $(this).addClass('active');
        currentFilter = $(this).data('filter');
        $('#disc-account-filter-label, #disc-lob-filter-label, #disc-sublob-filter-label, #disc-persona-filter-label, #disc-posts-filter-label')
            .text('Filter: ' + currentFilter.charAt(0).toUpperCase() + currentFilter.slice(1));
        loadDiscoveryData();
    });

    // Load all tabs
    window.loadDiscoveryData = function () {
        loadAccounts();
        loadLOBs();
        loadSubLOBs();
        loadPersonas();
        loadLinkedInPosts();
    };

    async function loadAccounts() {
        const $body = $('#disc-account-body');
        $body.html('<tr><td colspan="5" class="text-center text-muted py-3"><div class="spinner-border spinner-border-sm me-2"></div>Loading...</td></tr>');
        try {
            const res = await API.get('/chatbot/search/organizations');
            const accounts = Array.isArray(res) ? res : (res.items || []);
            if (accounts.length === 0) {
                $body.html('<tr><td colspan="5" class="text-center text-muted py-3">No accounts found</td></tr>');
                return;
            }
            $body.empty();
            accounts.forEach(a => {
                $body.append(`
                    <tr>
                        <td class="fw-semibold">${a.name || '—'}</td>
                        <td>${a.industry || '—'}</td>
                        <td>${a.employee_count ? Number(a.employee_count).toLocaleString() : '—'}</td>
                        <td>${a.annual_revenue || '—'}</td>
                        <td>${a.headquarters || '—'}</td>
                    </tr>
                `);
            });
        } catch (err) {
            $body.html('<tr><td colspan="5" class="text-center text-danger py-3">Failed to load accounts</td></tr>');
        }
    }

    async function loadLOBs() {
        const $body = $('#disc-lob-body');
        $body.html('<tr><td colspan="5" class="text-center text-muted py-3"><div class="spinner-border spinner-border-sm me-2"></div>Loading...</td></tr>');
        try {
            // Use chatbot query to fetch LOBs
            const res = await API.post('/chatbot/query', { message: 'Show all lines of business', limit: 20 });
            const lobs = res.lobs || [];
            if (lobs.length === 0) {
                $body.html('<tr><td colspan="5" class="text-center text-muted py-3">No LOBs found</td></tr>');
                return;
            }
            $body.empty();
            lobs.forEach(l => {
                $body.append(`
                    <tr>
                        <td class="fw-semibold">${l.name || '—'}</td>
                        <td>${l.account_name || '—'}</td>
                        <td>${l.business_head || '—'}</td>
                        <td>${l.tech_leader || '—'}</td>
                        <td><span class="text-xs">${l.key_platforms || '—'}</span></td>
                    </tr>
                `);
            });
        } catch (err) {
            $body.html('<tr><td colspan="5" class="text-center text-danger py-3">Failed to load LOBs</td></tr>');
        }
    }

    async function loadSubLOBs() {
        const $body = $('#disc-sublob-body');
        $body.html('<tr><td colspan="5" class="text-center text-muted py-3"><div class="spinner-border spinner-border-sm me-2"></div>Loading...</td></tr>');
        try {
            const res = await API.post('/chatbot/query', { message: 'Show sub lines of business', limit: 20 });
            const sublobs = res.lobs || [];
            if (sublobs.length === 0) {
                $body.html('<tr><td colspan="5" class="text-center text-muted py-3">No Sub LOBs found</td></tr>');
                return;
            }
            $body.empty();
            sublobs.forEach(s => {
                $body.append(`
                    <tr>
                        <td class="fw-semibold">${s.name || '—'}</td>
                        <td>${s.node_type || '—'}</td>
                        <td>${s.account_name || '—'}</td>
                        <td>${s.business_head || s.tech_leader || '—'}</td>
                        <td><span class="text-xs">${s.intelligence_notes || '—'}</span></td>
                    </tr>
                `);
            });
        } catch (err) {
            $body.html('<tr><td colspan="5" class="text-center text-danger py-3">Failed to load Sub LOBs</td></tr>');
        }
    }

    async function loadPersonas() {
        const $body = $('#disc-persona-body');
        $body.html('<tr><td colspan="6" class="text-center text-muted py-3"><div class="spinner-border spinner-border-sm me-2"></div>Loading...</td></tr>');
        try {
            const res = await API.post('/chatbot/search/people', { limit: 50 });
            const contacts = res.items || [];
            if (contacts.length === 0) {
                $body.html('<tr><td colspan="6" class="text-center text-muted py-3">No personas found</td></tr>');
                return;
            }
            $body.empty();
            contacts.forEach(c => {
                const name = c.full_name || '—';
                $body.append(`
                    <tr>
                        <td class="fw-semibold">${name}</td>
                        <td>${c.title || '—'}</td>
                        <td>${c.organization || '—'}</td>
                        <td><span class="badge bg-indigo-50 text-indigo-700 border border-indigo-200 text-[10px]">${c.seniority_tier || 'Executive'}</span></td>
                        <td><span class="fw-bold ${(c.lead_score||0) >= 80 ? 'text-success' : 'text-warning'}">${c.lead_score || '—'}</span></td>
                        <td class="text-xs">${c.email || '—'}</td>
                    </tr>
                `);
            });
        } catch (err) {
            $body.html('<tr><td colspan="6" class="text-center text-danger py-3">Failed to load personas</td></tr>');
        }
    }

    async function loadLinkedInPosts() {
        const $container = $('#disc-posts-content');
        $container.html('<div class="text-center text-muted py-4"><div class="spinner-border spinner-border-sm me-2"></div>Loading LinkedIn posts...</div>');
        try {
            let posts = [];
            try {
                const res = await API.post('/chatbot/query', { message: 'Show latest LinkedIn posts', limit: 20 });
                posts = res.posts || res.results?.posts || [];
            } catch (qErr) {
                const feed = await API.get('/social/feed');
                posts = Array.isArray(feed) ? feed : (feed.items || feed.posts || []);
            }
            if (posts.length === 0) {
                const feed = await API.get('/social/feed');
                posts = Array.isArray(feed) ? feed : (feed.items || feed.posts || []);
            }
            if (posts.length === 0) {
                $container.html('<div class="text-center text-muted py-4">No LinkedIn posts found</div>');
                return;
            }
            $container.empty();
            posts.forEach(p => {
                const sentimentColor = (p.sentiment || '').toUpperCase() === 'POSITIVE' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : ((p.sentiment || '').toUpperCase() === 'NEGATIVE' ? 'bg-rose-50 text-rose-700 border-rose-200' : 'bg-amber-50 text-amber-700 border-amber-200');
                $container.append(`
                    <div class="p-4 bg-white rounded-xl border border-slate-200 shadow-sm">
                        <div class="d-flex align-items-center justify-content-between mb-2">
                            <div class="d-flex align-items-center gap-2">
                                <i class="bi bi-linkedin text-blue-600 fs-5"></i>
                                <div>
                                    <span class="fw-bold text-slate-800 text-sm">${p.author_name || 'Executive'}</span>
                                    <span class="text-slate-400 text-xs ms-2">${p.author_title || ''}</span>
                                </div>
                            </div>
                            <div class="d-flex align-items-center gap-2">
                                <span class="badge ${sentimentColor} border text-[10px]">${p.sentiment || 'POSITIVE'}</span>
                                <span class="text-xs text-slate-400">${p.post_date_formatted || 'Recent'}</span>
                            </div>
                        </div>
                        <p class="text-sm text-slate-700 mb-2" style="line-height:1.6;">${p.content || '—'}</p>
                        <div class="d-flex align-items-center justify-content-between text-xs text-slate-500 pt-2 border-top border-slate-100">
                            <span>👍 ${p.likes_count || 0} likes &bull; 💬 ${p.comments_count || 0} comments &bull; 🔄 ${p.shares_count || 0} shares</span>
                            <div class="d-flex gap-1">
                                ${(p.topic_tags || []).map(t => `<span class="badge bg-slate-100 text-slate-600 border text-[9px]">#${t}</span>`).join('')}
                            </div>
                        </div>
                    </div>
                `);
            });
        } catch (err) {
            $container.html('<div class="text-center text-danger py-4">Failed to load LinkedIn posts</div>');
        }
    }
});
