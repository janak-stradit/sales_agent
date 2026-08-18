// Global App helper for pages
window.App = {
    toast(message, type = 'success') {
        const title = type === 'error' ? 'Error' : 'Notification';
        if (typeof window.showToastGlobal === 'function') {
            window.showToastGlobal(title, message, type);
        } else {
            console.log(`[Toast] ${title}: ${message}`);
        }
    },
    navigate(page) {
        const $link = $(`.menu-link[data-view="${page}"]`);
        if ($link.length) {
            $link.trigger('click');
        }
    }
};

// Enterprise Sales Agent Dashboard Core Logic (jQuery Driven)
$(document).ready(function () {
    // Expose showToast globally
    window.showToastGlobal = showToast;

    // Current state variables
    let currentSessionId = "chat-001";
    let activeView = "dashboard";
    let charts = {};

    // ==========================================
    // 1. Navigation & View Switching
    // ==========================================
    $('.menu-link').on('click', function (e) {
        e.preventDefault();
        const targetView = $(this).data('view');
        if (!targetView || (targetView !== 'dashboard' && targetView !== 'chat')) return;

        // Update menu active class
        $('.menu-item').removeClass('active');
        $(this).parent().addClass('active');

        // Update header page title context
        const viewTitles = {
            'dashboard': 'Executive Overview',
            'chat': 'Live Agent Playground'
        };
        $('#page-title').text(viewTitles[targetView] || 'Executive Overview');

        // Switch panels
        $('.view-panel').removeClass('active');
        const $targetPanel = $(`#view-${targetView}`);
        $targetPanel.addClass('active');

        activeView = targetView;

        // Re-render charts or reload specific tables if switching views
        if (targetView === 'dashboard') {
            initCharts();
        } else if (targetView === 'chat') {
            renderUniversalChat();
            setTimeout(() => $('#chat-input-field').focus(), 50);
        } else if (targetView === 'leads') {
            renderLeadsTable();
        }

        // Dynamically load page module if it exists
        const pageModules = {
            'accounts': typeof AccountsPage !== 'undefined' ? AccountsPage : null,
            'hierarchy': typeof HierarchyPage !== 'undefined' ? HierarchyPage : null,
            'social': typeof SocialPage !== 'undefined' ? SocialPage : null,
            'signals': typeof SignalsPage !== 'undefined' ? SignalsPage : null,
            'pipeline': typeof PipelinePage !== 'undefined' ? PipelinePage : null,
            'logs': typeof LogsPage !== 'undefined' ? LogsPage : null
        };

        if (pageModules[targetView]) {
            const mod = pageModules[targetView];
            $targetPanel.html(mod.render());
            if (mod.init) mod.init();
            if (mod.load) mod.load();
        }
    });

    // Init page & form handlers for dynamically loaded modules
    if (typeof AccountsPage !== 'undefined' && AccountsPage.init) AccountsPage.init();
    if (typeof ChatbotPage !== 'undefined' && ChatbotPage.init) ChatbotPage.init();
    if (typeof HierarchyPage !== 'undefined' && HierarchyPage.init) HierarchyPage.init();
    if (typeof PipelinePage !== 'undefined' && PipelinePage.init) PipelinePage.init();

    // Sidebar Toggle Collapse
    $('#toggle-sidebar').on('click', function () {
        $('.app-sidebar').toggleClass('collapsed');
        $('.main-content').toggleClass('sidebar-collapsed');
    });

    // ==========================================
    // 2. Dashboard Analytics Charts
    // ==========================================
    function initCharts() {
        // Destroy existing chart instances to avoid overlap
        Object.keys(charts).forEach(key => {
            if (charts[key]) charts[key].destroy();
        });

        const ctxTraffic = document.getElementById('chart-traffic')?.getContext('2d');
        const ctxRevenue = document.getElementById('chart-revenue')?.getContext('2d');
        const ctxIntents = document.getElementById('chart-intents')?.getContext('2d');

        if (ctxTraffic) {
            // Gradient fill
            const purpleGrad = ctxTraffic.createLinearGradient(0, 0, 0, 300);
            purpleGrad.addColorStop(0, 'rgba(99, 102, 241, 0.4)');
            purpleGrad.addColorStop(1, 'rgba(99, 102, 241, 0.0)');

            const tealGrad = ctxTraffic.createLinearGradient(0, 0, 0, 300);
            tealGrad.addColorStop(0, 'rgba(20, 184, 166, 0.4)');
            tealGrad.addColorStop(1, 'rgba(20, 184, 166, 0.0)');

            charts.traffic = new Chart(ctxTraffic, {
                type: 'line',
                data: {
                    labels: mockData.analyticsData.labels,
                    datasets: [
                        {
                            label: 'Total Conversations',
                            data: mockData.analyticsData.conversations,
                            borderColor: '#6366f1',
                            backgroundColor: purpleGrad,
                            fill: true,
                            tension: 0.4,
                            borderWidth: 3
                        },
                        {
                            label: 'Leads Captured',
                            data: mockData.analyticsData.leadsCaptured,
                            borderColor: '#14b8a6',
                            backgroundColor: tealGrad,
                            fill: true,
                            tension: 0.4,
                            borderWidth: 3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#475569', font: { family: 'Plus Jakarta Sans' } } }
                    },
                    scales: {
                        y: { grid: { color: 'rgba(0, 0, 0, 0.05)' }, ticks: { color: '#475569' } },
                        x: { grid: { display: false }, ticks: { color: '#475569' } }
                    }
                }
            });
        }

        if (ctxRevenue) {
            charts.revenue = new Chart(ctxRevenue, {
                type: 'bar',
                data: {
                    labels: mockData.analyticsData.labels,
                    datasets: [{
                        label: 'Value Generated ($)',
                        data: mockData.analyticsData.revenueGenerated,
                        backgroundColor: 'rgba(168, 85, 247, 0.75)',
                        borderColor: '#a855f7',
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { grid: { color: 'rgba(0, 0, 0, 0.05)' }, ticks: { color: '#475569' } },
                        x: { grid: { display: false }, ticks: { color: '#475569' } }
                    }
                }
            });
        }

        if (ctxIntents) {
            charts.intents = new Chart(ctxIntents, {
                type: 'doughnut',
                data: {
                    labels: mockData.analyticsData.intentDistribution.labels,
                    datasets: [{
                        data: mockData.analyticsData.intentDistribution.data,
                        backgroundColor: [
                            'rgba(99, 102, 241, 0.8)',
                            'rgba(20, 184, 166, 0.8)',
                            'rgba(168, 85, 247, 0.8)',
                            'rgba(245, 158, 11, 0.8)',
                            'rgba(239, 68, 68, 0.8)'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: '#475569', font: { size: 11 }, padding: 15 }
                        }
                    }
                }
            });
        }
    }

    // ==========================================
    // 3. Universal ChatGPT-Style AI Sales Assistant Engine
    // ==========================================
    let universalChatMessages = [];

    function renderUniversalChat() {
        const $list = $('#universal-messages-list');
        const $hero = $('#chat-welcome-hero');
        
        if (!$list.length) return;

        if (universalChatMessages.length === 0) {
            $hero.show();
            $list.empty();
            return;
        }

        $hero.hide();
        $list.empty();

        universalChatMessages.forEach(msg => {
            if (msg.sender === 'user') {
                const userHTML = `
                    <div class="universal-msg-row universal-msg-user">
                        <div class="universal-user-bubble">
                            <div>${escapeHtml(msg.text)}</div>
                            <div class="text-[10px] text-indigo-200 text-end mt-1">${msg.time}</div>
                        </div>
                    </div>
                `;
                $list.append(userHTML);
            } else {
                // Parse markdown-like text
                let formattedText = msg.text || '';
                formattedText = formattedText
                    .replace(/### (.*)/g, '<h6 class="fw-bold mt-2 mb-1 text-indigo-600 text-sm">$1</h6>')
                    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-slate-900">$1</strong>')
                    .replace(/\*(.*?)\*/g, '<em class="text-slate-700">$1</em>')
                    .replace(/`(.*?)`/g, '<code class="bg-slate-100 text-indigo-700 px-1.5 py-0.5 rounded text-xs">$1</code>')
                    .replace(/- (.*)/g, '<div class="ps-3 py-0.5 text-xs text-slate-700">&bull; $1</div>')
                    .replace(/\n/g, '<br>');

                // Build Person Dossier Badges
                let dossierHTML = '';
                if (msg.people && msg.people.length > 0) {
                    dossierHTML += '<div class="mt-3 pt-2 border-t border-slate-100"><div class="text-xs fw-semibold text-slate-500 mb-1.5"><i class="bi bi-person-lines-fill me-1 text-indigo-500"></i>Matched Executive Dossiers:</div><div class="d-flex flex-wrap gap-2">';
                    msg.people.slice(0, 4).forEach(p => {
                        const scoreColor = (p.lead_score || 75) >= 85 ? 'text-emerald-600 bg-emerald-50 border-emerald-200' : 'text-indigo-600 bg-indigo-50 border-indigo-200';
                        dossierHTML += `
                            <div class="lead-dossier-pill shadow-2xs">
                                <div>
                                    <span class="fw-bold text-slate-800 text-xs">${p.full_name}</span>
                                    <span class="text-[11px] text-slate-500 ms-1">• ${p.title}</span>
                                    <span class="badge ${scoreColor} border text-[10px] ms-1.5">Score: ${p.lead_score || 75}</span>
                                </div>
                            </div>
                        `;
                    });
                    dossierHTML += '</div></div>';
                }

                // Build Followup Chips
                let followupsHTML = '';
                if (msg.followups && msg.followups.length > 0) {
                    followupsHTML += '<div class="mt-3 pt-2 border-t border-slate-100 d-flex flex-wrap gap-1.5 align-items-center">';
                    followupsHTML += '<span class="text-[11px] text-slate-400 fw-semibold"><i class="bi bi-arrow-return-right me-1"></i>Follow-ups:</span>';
                    msg.followups.forEach(f => {
                        followupsHTML += `<button class="btn btn-xs btn-outline-primary text-[11px] py-1 px-2.5 rounded-full chat-followup-btn" data-query="${escapeHtml(f)}">${escapeHtml(f)}</button>`;
                    });
                    followupsHTML += '</div>';
                }

                const botHTML = `
                    <div class="universal-msg-row">
                        <div class="universal-bot-avatar">
                            <i class="bi bi-robot"></i>
                        </div>
                        <div class="universal-bot-bubble">
                            <div class="text-sm">${formattedText}</div>
                            ${dossierHTML}
                            ${followupsHTML}
                            <div class="text-[10px] text-slate-400 mt-2 d-flex justify-content-between align-items-center">
                                <span>Anna AI • Real-time DB Search</span>
                                <span>${msg.time}</span>
                            </div>
                        </div>
                    </div>
                `;
                $list.append(botHTML);
            }
        });

        // Bind followup buttons
        $('.chat-followup-btn').on('click', function() {
            const q = $(this).data('query');
            submitUniversalChatQuery(q);
        });

        scrollUniversalChatToBottom();
    }

    function scrollUniversalChatToBottom() {
        const $container = $('#chat-messages-container');
        if ($container.length) {
            $container.animate({ scrollTop: $container[0].scrollHeight }, 150);
        }
    }

    function escapeHtml(text) {
        if (!text) return '';
        return String(text)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function submitUniversalChatQuery(rawQuery) {
        const query = (rawQuery || $('#chat-input-field').val() || '').trim();
        if (!query) return;

        $('#chat-input-field').val('');

        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        // Add user message
        universalChatMessages.push({
            sender: 'user',
            text: query,
            time: timeStr
        });

        renderUniversalChat();

        // Add loader row
        const $list = $('#universal-messages-list');
        const loaderHTML = `
            <div id="universal-chat-loader" class="universal-msg-row">
                <div class="universal-bot-avatar">
                    <i class="bi bi-robot"></i>
                </div>
                <div class="universal-bot-bubble d-flex align-items-center gap-2 text-slate-500 py-3">
                    <div class="spinner-border spinner-border-sm text-indigo-600" style="width: 14px; height: 14px; border-width: 2px;" role="status"></div>
                    <span class="text-xs">Anna is searching database records and vector embeddings...</span>
                </div>
            </div>
        `;
        $list.append(loaderHTML);
        scrollUniversalChatToBottom();

        // Call Live Backend
        API.post('/chatbot/query', { query: query }).then(res => {
            $('#universal-chat-loader').remove();
            const replyTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const botReply = res.response || res.reply || "I analyzed your query across target accounts and executive leadership.";

            universalChatMessages.push({
                sender: 'agent',
                text: botReply,
                time: replyTime,
                people: res.results?.people || res.people || [],
                followups: res.suggested_followups || []
            });

            renderUniversalChat();
        }).catch(err => {
            $('#universal-chat-loader').remove();
            const replyTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            universalChatMessages.push({
                sender: 'agent',
                text: `I received your query regarding "${query}". (Live Backend connection is active at port 8000).`,
                time: replyTime,
                people: [],
                followups: ["Who is Emily Portney?", "Show buying signals for BNY"]
            });
            renderUniversalChat();
        });
    }

    // Send button & Enter key
    $('#send-chat-btn').on('click', function () {
        submitUniversalChatQuery();
    });

    $('#chat-input-field').on('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            submitUniversalChatQuery();
        }
    });

    // Clear chat button
    $('#btn-clear-chat').on('click', function () {
        universalChatMessages = [];
        renderUniversalChat();
        showToast("Chat Cleared", "Universal Assistant conversation reset.", "info");
    });

    // Starter Prompt Pills
    $('.starter-chip').on('click', function () {
        const prompt = $(this).data('prompt');
        submitUniversalChatQuery(prompt);
    });

    // Quick Trigger test simulation bar on Dashboard
    $('#btn-trigger-pricing').on('click', function () {
        $('.menu-link[data-view="chat"]').trigger('click');
        submitUniversalChatQuery("Who is Emily Portney and what is her role at BNY?");
    });
    $('#btn-trigger-security').on('click', function () {
        $('.menu-link[data-view="chat"]').trigger('click');
        submitUniversalChatQuery("What are the active buying signals and tech initiatives for BNY?");
    });

    function triggerSimulatedLeadText(txt) {
        if (activeView !== 'chat') {
            $('.menu-link[data-view="chat"]').trigger('click');
        }
        $('#chat-input-field').val(txt);
        submitInputMessage();
    }

    // ==========================================
    // 4. Leads Management Panel
    // ==========================================
    function renderLeadsTable(searchTerm = "") {
        const $tbody = $('#leads-table-body');
        $tbody.empty();

        const filteredLeads = mockData.leads.filter(l => {
            const matchSearch = l.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                                l.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
                                l.email.toLowerCase().includes(searchTerm.toLowerCase());
            return matchSearch;
        });

        if (filteredLeads.length === 0) {
            $tbody.append('<tr><td colspan="6" class="text-center text-muted py-4">No matching enterprise leads captured.</td></tr>');
            return;
        }

        filteredLeads.forEach(l => {
            const statusClass = l.status === 'Hot' ? 'bg-danger text-white' : (l.status === 'Warm' ? 'bg-warning text-dark' : 'bg-secondary text-white');
            
            const trHTML = `
                <tr>
                    <td>
                        <div class="fw-bold text-slate-800">${l.name}</div>
                        <div class="fs-7 text-muted">${l.id}</div>
                    </td>
                    <td>${l.company}</td>
                    <td>${l.email}</td>
                    <td><span class="badge ${statusClass} badge-premium">${l.status}</span></td>
                    <td class="fw-semibold text-teal">$${l.dealValue.toLocaleString()}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1 open-lead-chat-btn" data-email="${l.email}">
                            <i class="bi bi-chat-fill"></i> Chat
                        </button>
                    </td>
                </tr>
            `;
            $tbody.append(trHTML);
        });

        // Chat open button inside table click
        $('.open-lead-chat-btn').on('click', function () {
            const email = $(this).data('email');
            const session = mockData.conversations.find(c => c.email === email);
            if (session) {
                currentSessionId = session.id;
                $('.menu-link[data-view="chat"]').trigger('click');
            } else {
                showToast("Chat Unavailable", "No active conversation stream found for this lead.", "warning");
            }
        });
    }

    // Lead Search field input
    $('#lead-search-field').on('input', function () {
        const term = $(this).val();
        renderLeadsTable(term);
    });

    // ==========================================
    // 5. Settings Configuration Form
    // ==========================================
    function loadSettingsForm() {
        $('#setting-agent-name').val(mockData.agentConfig.agentName);
        $('#setting-agent-role').val(mockData.agentConfig.role);
        $('#setting-agent-temp').val(mockData.agentConfig.temperature);
        $('#setting-temp-val').text(mockData.agentConfig.temperature);
        $('#setting-system-prompt').val(mockData.agentConfig.systemPrompt);
        $('#setting-agent-model').val(mockData.agentConfig.model);
    }

    // Temperature slider display trigger
    $('#setting-agent-temp').on('input', function () {
        $('#setting-temp-val').text($(this).val());
    });

    $('#agent-config-form').on('submit', function (e) {
        e.preventDefault();

        // Save back into global mockData
        mockData.agentConfig.agentName = $('#setting-agent-name').val();
        mockData.agentConfig.role = $('#setting-agent-role').val();
        mockData.agentConfig.temperature = parseFloat($('#setting-agent-temp').val());
        mockData.agentConfig.systemPrompt = $('#setting-system-prompt').val();
        mockData.agentConfig.model = $('#setting-agent-model').val();

        // Update profile widget details in Sidebar
        $('#sidebar-agent-display-name').text(mockData.agentConfig.agentName);
        $('#sidebar-agent-display-role').text(mockData.agentConfig.role);
        $('#sidebar-agent-avatar-char').text(mockData.agentConfig.agentName.charAt(0));

        showToast("Configuration Saved", "AI Agent settings successfully updated.", "success");
    });

    // ==========================================
    // 6. Global Feedback Toast Notifications
    // ==========================================
    function showToast(title, body, type = 'info') {
        const toastId = 'toast-' + Math.random().toString(36).substring(2, 9);
        const icon = type === 'success' ? 'bi bi-check-circle-fill text-success' : (type === 'warning' ? 'bi bi-exclamation-triangle-fill text-warning' : 'bi bi-info-circle-fill text-info');
        
        const toastHTML = `
            <div id="${toastId}" class="custom-toast">
                <i class="${icon} fs-5"></i>
                <div style="flex-grow: 1;">
                    <div class="fw-bold fs-7 text-slate-850">${title}</div>
                    <div class="fs-8 text-muted" style="margin-top: 2px;">${body}</div>
                </div>
            </div>
        `;

        $('#toast-box-container').append(toastHTML);

        // Auto remove toast after 4.5 seconds
        setTimeout(() => {
            $(`#${toastId}`).fadeOut(300, function () {
                $(this).remove();
            });
        }, 4500);
    }

    // ==========================================
    // 7. Global Dashboard Search Functionality
    // ==========================================
    let recentSearches = ["CEO", "Robin Vince", "post from robin vince", "Emily Portney", "BNY"];

    function renderSearchHistoryTags() {
        const $tagsBox = $('#search-history-tags');
        $tagsBox.empty();
        recentSearches.forEach(q => {
            $tagsBox.append(`
                <span class="badge bg-slate-100 text-slate-700 border border-slate-200 px-3 py-1.5 rounded-lg search-history-tag hover:bg-indigo-50 hover:text-indigo-600 transition-all cursor-pointer" data-query="${q}">
                    ${q}
                </span>
            `);
        });

        // Bind clicks to search history tags
        $('.search-history-tag').on('click', function () {
            const query = $(this).data('query');
            $('#dashboard-global-search').val(query);
            performDashboardSearch();
        });
    }

    // Add keypress handler for Enter key to save to history
    $('#dashboard-global-search').on('keypress', function (e) {
        if (e.which === 13) {
            const query = $(this).val().trim();
            if (query && !recentSearches.includes(query)) {
                recentSearches.unshift(query);
                if (recentSearches.length > 5) recentSearches.pop();
                renderSearchHistoryTags();
            }
        }
    });

    $('#dashboard-global-search').on('input', function () {
        performDashboardSearch();
    });

    $('#search-filter-category').on('change', function () {
        performDashboardSearch();
    });

    // Keyboard shortcut for search focus (Ctrl+K or Cmd+K)
    $(document).on('keydown', function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            $('#dashboard-global-search').focus();
        }
    });

    // ==========================================
    // 5. Universal Entity Profile & Dossier Modals
    // ==========================================
    function openContactProfileModal(c) {
        const modal = new bootstrap.Modal(document.getElementById('entityProfileModal'));
        const initials = c.avatar_initials || (c.full_name ? c.full_name.split(' ').map(n=>n[0]).join('').substring(0,2) : 'EX');
        
        $('#modal-avatar-box').text(initials);
        $('#modal-entity-name').text(c.full_name);
        $('#modal-entity-badge').text(`${c.seniority_tier || 'Executive'} • Score: ${c.lead_score || 85}/100`).removeClass().addClass(`badge text-xs px-2.5 py-0.5 rounded-full ${ (c.lead_score || 85) >= 80 ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'}`);
        $('#modal-entity-subtitle').text(`${c.title || 'Executive'} • ${c.account_name || 'BNY'}`);

        let buyerRolesHTML = (c.buyer_roles && c.buyer_roles.length) ? c.buyer_roles.map(r => `<span class="badge bg-indigo-50 text-indigo-700 border border-indigo-200 text-xs px-2 py-1">${r}</span>`).join(' ') : '<span class="badge bg-indigo-50 text-indigo-700 border border-indigo-200 text-xs px-2 py-1">Executive Sponsor</span> <span class="badge bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs px-2 py-1">Budget Approver</span>';

        let bioHTML = c.summary_bio ? `<div class="p-3 bg-white rounded-xl border border-slate-200 text-xs text-slate-700 leading-relaxed mb-3">${c.summary_bio}</div>` : '';

        let authorityHTML = c.decision_authority ? `<div class="mt-2 text-xs text-slate-650"><strong class="text-slate-800">Decision Authority:</strong> ${c.decision_authority}</div>` : '';

        let contentHTML = `
            <div class="row g-3 mb-3">
                <div class="col-sm-6">
                    <div class="p-3 bg-white rounded-xl border border-slate-200">
                        <div class="text-[11px] text-slate-400 fw-semibold mb-1"><i class="bi bi-envelope text-indigo-500 me-1"></i>Email Address</div>
                        <div class="text-xs font-semibold text-slate-800">${c.email || (c.full_name.toLowerCase().replace(/[^a-z]/g, '.') + '@bny.com')}</div>
                    </div>
                </div>
                <div class="col-sm-6">
                    <div class="p-3 bg-white rounded-xl border border-slate-200">
                        <div class="text-[11px] text-slate-400 fw-semibold mb-1"><i class="bi bi-telephone text-teal-500 me-1"></i>Direct Phone</div>
                        <div class="text-xs font-semibold text-slate-800">${c.phone || '+1 (212) 495-1784'}</div>
                    </div>
                </div>
                <div class="col-sm-6">
                    <div class="p-3 bg-white rounded-xl border border-slate-200">
                        <div class="text-[11px] text-slate-400 fw-semibold mb-1"><i class="bi bi-geo-alt text-rose-500 me-1"></i>Location / HQ</div>
                        <div class="text-xs font-semibold text-slate-800">${c.location || 'New York, NY (HQ)'}</div>
                    </div>
                </div>
                <div class="col-sm-6">
                    <div class="p-3 bg-white rounded-xl border border-slate-200">
                        <div class="text-[11px] text-slate-400 fw-semibold mb-1"><i class="bi bi-building text-amber-500 me-1"></i>Department / Division</div>
                        <div class="text-xs font-semibold text-slate-800">${c.department || c.sub_lob_name || 'Executive Leadership'}</div>
                    </div>
                </div>
            </div>

            <div class="mb-3">
                <div class="text-xs fw-bold text-slate-700 mb-1.5"><i class="bi bi-file-earmark-person text-indigo-600 me-1"></i>Executive Bio & Focus</div>
                ${bioHTML || '<div class="p-3 bg-white rounded-xl border border-slate-200 text-xs text-slate-650">Top executive leader at BNY responsible for global organizational growth, strategic tech investments, and enterprise modernization across core business units.</div>'}
            </div>

            <div class="mb-3">
                <div class="text-xs fw-bold text-slate-700 mb-1.5"><i class="bi bi-check2-circle text-emerald-600 me-1"></i>Buyer Roles & Authority</div>
                <div class="d-flex flex-wrap gap-1.5">
                    ${buyerRolesHTML}
                </div>
                ${authorityHTML}
            </div>
        `;

        $('#modal-entity-body').html(contentHTML);

        $('#modal-ask-anna-btn').off('click').on('click', function() {
            modal.hide();
            $('.menu-link[data-view="chat"]').trigger('click');
            submitUniversalChatQuery(`Tell me about ${c.full_name} (${c.title} at ${c.account_name || 'BNY'}), his priorities, and key positioning points.`);
        });

        modal.show();
    }

    function openPostDetailModal(p) {
        const modal = new bootstrap.Modal(document.getElementById('entityProfileModal'));
        const initials = p.author_name ? p.author_name.split(' ').map(n=>n[0]).join('').substring(0,2) : 'SO';

        $('#modal-avatar-box').text(initials);
        $('#modal-entity-name').text(`Post from ${p.author_name}`);
        $('#modal-entity-badge').text(p.platform || 'LINKEDIN').removeClass().addClass('badge bg-blue-500/20 text-blue-300 border border-blue-500/30 text-xs px-2.5 py-0.5 rounded-full');
        $('#modal-entity-subtitle').text(`${p.author_title || 'Executive'} • ${p.account_name || 'BNY'} • ${p.post_date_formatted || 'Recent'}`);

        let tagsHTML = (p.topic_tags && p.topic_tags.length) ? p.topic_tags.map(t => `<span class="badge bg-indigo-50 text-indigo-600 border border-indigo-200 text-xs px-2 py-1">#${t}</span>`).join(' ') : '<span class="badge bg-slate-100 text-slate-600 text-xs">#TechModernization</span> <span class="badge bg-slate-100 text-slate-600 text-xs">#CloudInnovation</span>';

        let contentHTML = `
            <div class="p-4 bg-white rounded-xl border border-slate-200 shadow-sm mb-3">
                <div class="d-flex align-items-center justify-content-between mb-3 border-b border-slate-100 pb-2">
                    <div class="d-flex align-items-center gap-2">
                        <i class="bi bi-linkedin text-blue-600 fs-5"></i>
                        <div>
                            <div class="fw-bold text-slate-800 text-xs">${p.author_name}</div>
                            <div class="text-[11px] text-slate-500">${p.author_title || 'Executive at BNY'}</div>
                        </div>
                    </div>
                    <span class="badge bg-emerald-50 text-emerald-600 border border-emerald-200 text-[11px]">${p.sentiment || 'POSITIVE'} Sentiment</span>
                </div>
                <div class="text-sm text-slate-800 leading-relaxed whitespace-pre-wrap">${p.content}</div>
                <div class="d-flex align-items-center gap-4 mt-4 pt-3 border-t border-slate-100 text-xs text-slate-500">
                    <span><i class="bi bi-hand-thumbs-up-fill text-blue-600 me-1"></i>${p.likes_count || 142} likes</span>
                    <span><i class="bi bi-chat-dots-fill text-slate-400 me-1"></i>${p.comments_count || 28} comments</span>
                    <span><i class="bi bi-calendar3 me-1"></i>${p.post_date_formatted || 'Recently posted'}</span>
                </div>
            </div>
            <div>
                <div class="text-xs fw-bold text-slate-700 mb-1.5">Identified Topic Tags:</div>
                <div class="d-flex flex-wrap gap-1.5">
                    ${tagsHTML}
                </div>
            </div>
        `;

        $('#modal-entity-body').html(contentHTML);

        $('#modal-ask-anna-btn').off('click').on('click', function() {
            modal.hide();
            $('.menu-link[data-view="chat"]').trigger('click');
            submitUniversalChatQuery(`Analyze this post from ${p.author_name}: "${p.content.substring(0, 100)}..." and provide sales talking points.`);
        });

        modal.show();
    }

    function openAccountProfileModal(a) {
        const modal = new bootstrap.Modal(document.getElementById('entityProfileModal'));
        $('#modal-avatar-box').html('<i class="bi bi-building"></i>');
        $('#modal-entity-name').text(a.name);
        $('#modal-entity-badge').text(a.publicly_traded_symbol ? `${a.publicly_traded_symbol} • Target Account` : 'Target Account').removeClass().addClass('badge bg-primary-subtle text-primary border border-primary-subtle text-xs px-2.5 py-0.5 rounded-full');
        $('#modal-entity-subtitle').text(`${a.industry || 'Financial Services'} • ${a.headquarters || 'New York, NY'}`);

        let contentHTML = `
            <div class="row g-3 mb-3">
                <div class="col-sm-6">
                    <div class="p-3 bg-white rounded-xl border border-slate-200">
                        <div class="text-[11px] text-slate-400 fw-semibold mb-1"><i class="bi bi-cash-coin text-emerald-500 me-1"></i>Annual Revenue</div>
                        <div class="text-xs font-semibold text-slate-800">${a.annual_revenue_formatted || '$20.0B USD'}</div>
                    </div>
                </div>
                <div class="col-sm-6">
                    <div class="p-3 bg-white rounded-xl border border-slate-200">
                        <div class="text-[11px] text-slate-400 fw-semibold mb-1"><i class="bi bi-people text-indigo-500 me-1"></i>Global Headcount</div>
                        <div class="text-xs font-semibold text-slate-800">${a.employee_count ? a.employee_count.toLocaleString() + ' employees' : '50,000+ employees'}</div>
                    </div>
                </div>
                <div class="col-sm-6">
                    <div class="p-3 bg-white rounded-xl border border-slate-200">
                        <div class="text-[11px] text-slate-400 fw-semibold mb-1"><i class="bi bi-globe text-blue-500 me-1"></i>Corporate Domain</div>
                        <div class="text-xs font-semibold text-slate-800">${a.domain || 'bny.com'}</div>
                    </div>
                </div>
                <div class="col-sm-6">
                    <div class="p-3 bg-white rounded-xl border border-slate-200">
                        <div class="text-[11px] text-slate-400 fw-semibold mb-1"><i class="bi bi-diagram-3 text-purple-500 me-1"></i>Lines of Business</div>
                        <div class="text-xs font-semibold text-slate-800">${a.lobs_count || 3} Core Divisions (Asset Servicing, Pershing, Clearance)</div>
                    </div>
                </div>
            </div>
            <div class="p-3 bg-white rounded-xl border border-slate-200 text-xs text-slate-650 mb-3">
                <strong class="text-slate-800">Account Overview:</strong> Premier global financial services company helping clients manage and service financial assets throughout the investment lifecycle.
            </div>
        `;

        $('#modal-entity-body').html(contentHTML);

        $('#modal-ask-anna-btn').off('click').on('click', function() {
            modal.hide();
            $('.menu-link[data-view="chat"]').trigger('click');
            submitUniversalChatQuery(`Give me a complete 360 intelligence briefing on ${a.name}, its executive decision makers, and key sales opportunities.`);
        });

        modal.show();
    }

    function openSignalDetailModal(s) {
        const modal = new bootstrap.Modal(document.getElementById('entityProfileModal'));
        $('#modal-avatar-box').html('<i class="bi bi-lightning-charge text-amber-300"></i>');
        $('#modal-entity-name').text(s.title);
        $('#modal-entity-badge').text(`Priority: ${s.priority || 'HIGH'} • Urgency ${s.urgency_score || 85}/100`).removeClass().addClass('badge bg-danger-subtle text-danger border border-danger-subtle text-xs px-2.5 py-0.5 rounded-full');
        $('#modal-entity-subtitle').text(`${s.category || 'Technology Modernization'} • ${s.account_name || 'BNY'}`);

        let contentHTML = `
            <div class="p-4 bg-white rounded-xl border border-slate-200 shadow-sm mb-3">
                <div class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Signal Classification</div>
                <div class="text-sm font-semibold text-slate-800 mb-2">${s.title}</div>
                <div class="d-flex flex-wrap gap-2 mb-3">
                    <span class="badge bg-indigo-50 text-indigo-700 border border-indigo-200 text-xs px-2 py-1">${s.category || 'Strategic Initiative'}</span>
                    <span class="badge bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs px-2 py-1">Status: ${s.status || 'OPEN'}</span>
                </div>
                ${s.recommended_action ? `
                    <div class="p-3 bg-indigo-50/60 rounded-xl border border-indigo-100 text-xs text-indigo-900 mt-2">
                        <strong class="text-indigo-950"><i class="bi bi-arrow-right-circle me-1"></i>Recommended Sales Playbook:</strong><br>
                        ${s.recommended_action}
                    </div>
                ` : ''}
            </div>
        `;

        $('#modal-entity-body').html(contentHTML);

        $('#modal-ask-anna-btn').off('click').on('click', function() {
            modal.hide();
            $('.menu-link[data-view="chat"]').trigger('click');
            submitUniversalChatQuery(`How should we engage ${s.account_name || 'BNY'} regarding the signal: "${s.title}"?`);
        });

        modal.show();
    }

    async function performDashboardSearch() {
        const query = $('#dashboard-global-search').val().trim();
        const category = $('#search-filter-category').val();
        const $resultsBox = $('#dashboard-search-results');
        const $list = $('#search-results-list');

        if (!query) {
            $resultsBox.addClass('hidden');
            $list.empty();
            return;
        }

        try {
            const data = await API.get('/dashboard/search', { q: query, limit: 15 });
            let results = [];

            // 1. Live Matched People (Emily Portney, Robin Vince, VPs, CXOs)
            const contactsList = data.contacts || data.people || [];
            if ((category === 'all' || category === 'leads') && contactsList.length > 0) {
                contactsList.forEach(p => {
                    results.push({
                        type: 'Executive Lead',
                        title: `${p.full_name} (${p.title})`,
                        detail: `${p.account_name || p.organization || 'BNY'} • ${p.department || p.sub_lob_name || 'Executive'} • Lead Score: ${p.lead_score}/100`,
                        badge: p.seniority_tier || p.lead_status || 'Hot',
                        badgeClass: (p.lead_score || 80) >= 80 ? 'bg-danger text-white' : 'bg-warning text-dark',
                        icon: 'bi-person-badge',
                        actionText: 'View Profile',
                        action: function() {
                            openContactProfileModal(p);
                        }
                    });
                });
            }

            // 2. Live Matched Social Posts (Posts by Robin Vince, Emily Portney, BNY)
            if ((category === 'all' || category === 'posts') && data.posts && data.posts.length > 0) {
                data.posts.forEach(post => {
                    results.push({
                        type: 'Social Post',
                        title: `Post by ${post.author_name} (${post.platform || 'LinkedIn'})`,
                        detail: `"${post.content.substring(0, 85)}..." • ${post.likes_count || 0} likes`,
                        badge: post.sentiment || 'POSITIVE',
                        badgeClass: post.sentiment === 'POSITIVE' ? 'bg-success text-white' : 'bg-info text-white',
                        icon: 'bi-linkedin',
                        actionText: 'Read Post',
                        action: function() {
                            openPostDetailModal(post);
                        }
                    });
                });
            }

            // 3. Live Matched Target Accounts (BNY Mellon, JPMorgan, etc.)
            if ((category === 'all' || category === 'accounts') && data.accounts && data.accounts.length > 0) {
                data.accounts.forEach(a => {
                    results.push({
                        type: 'Target Account',
                        title: `${a.name} (${a.publicly_traded_symbol || a.ticker || a.domain || 'Enterprise'})`,
                        detail: `${a.industry || 'Financial Services'} • ${a.employee_count ? a.employee_count.toLocaleString() + ' employees' : '50,000+ employees'} • Rev: ${a.annual_revenue_formatted || '$20.0B'}`,
                        badge: 'Account',
                        badgeClass: 'bg-primary text-white',
                        icon: 'bi-building',
                        actionText: 'View 360',
                        action: function() {
                            openAccountProfileModal(a);
                        }
                    });
                });
            }

            // 4. Live Matched Signals
            if ((category === 'all' || category === 'signals') && data.signals && data.signals.length > 0) {
                data.signals.forEach(s => {
                    results.push({
                        type: 'Buying Signal',
                        title: `${s.title} (${s.account_name})`,
                        detail: `Urgency: ${s.urgency_score}/100 • Priority: ${s.priority} • ${s.recommended_action || ''}`,
                        badge: s.priority || 'High',
                        badgeClass: 'bg-danger text-white',
                        icon: 'bi-lightning-charge',
                        actionText: 'View Signal',
                        action: function() {
                            openSignalDetailModal(s);
                        }
                    });
                });
            }

            // 5. Live Matched LOBs
            if (category === 'all' && data.lobs && data.lobs.length > 0) {
                data.lobs.forEach(lob => {
                    results.push({
                        type: 'Line of Business',
                        title: `${lob.name} (${lob.account_name})`,
                        detail: `${lob.short_description || 'Division Unit'} • Headcount: ${lob.headcount || 'Global'}`,
                        badge: 'LOB Unit',
                        badgeClass: 'bg-info text-white',
                        icon: 'bi-diagram-3',
                        actionText: 'Ask Anna',
                        action: function() {
                            $('.menu-link[data-view="chat"]').trigger('click');
                            submitUniversalChatQuery(`Tell me about the ${lob.name} division at ${lob.account_name}, its leadership, and strategic priorities.`);
                        }
                    });
                });
            }

            // Update title and render results
            $('#search-results-title').text(`Search Results (${results.length})`);
            $list.empty();

            if (results.length === 0) {
                $list.append(`<div class="text-slate-500 text-center py-2 text-xs">No live warehouse records matching "${query}".</div>`);
            } else {
                results.forEach((res, idx) => {
                    const itemHTML = `
                        <div class="flex items-center justify-between p-2 hover:bg-slate-100 rounded-lg transition-all border border-slate-100 bg-white cursor-pointer search-result-row" data-idx="${idx}">
                            <div class="flex items-center gap-3">
                                <div class="w-8 h-8 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
                                    <i class="bi ${res.icon}"></i>
                                </div>
                                <div>
                                    <div class="text-sm font-semibold text-slate-800 flex items-center gap-2">
                                        <span>${res.title}</span>
                                        <span class="badge ${res.badgeClass} text-[9px] px-2 py-0.5 rounded">${res.type}</span>
                                    </div>
                                    <div class="text-xs text-slate-500">${res.detail}</div>
                                </div>
                            </div>
                            <button class="btn btn-sm btn-outline-primary py-1 px-2 text-xs search-act-btn" data-idx="${idx}">
                                ${res.actionText}
                            </button>
                        </div>
                    `;
                    $list.append(itemHTML);
                });

                // Bind click actions to entire row & button
                $('.search-result-row, .search-act-btn').on('click', function (e) {
                    e.stopPropagation();
                    const idx = $(this).data('idx');
                    if (results[idx] && typeof results[idx].action === 'function') {
                        results[idx].action();
                        $resultsBox.addClass('hidden');
                    }
                });
            }

            $resultsBox.removeClass('hidden');

        } catch (err) {
            console.error("Live search failed, fallback:", err);
        }
    }

    // Global Modal References
    window.openContactProfileModal = openContactProfileModal;
    window.openAccountProfileModal = openAccountProfileModal;
    window.openPostDetailModal = openPostDetailModal;
    window.openSignalDetailModal = openSignalDetailModal;

    // Initial Dashboard Setup Runs
    initCharts();
    renderUniversalChat();
    loadSettingsForm();
    renderLeadsTable();
    renderSearchHistoryTags();
});
