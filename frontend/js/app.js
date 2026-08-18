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
        if (!targetView) return;

        // Update menu active class
        $('.menu-item').removeClass('active');
        $(this).parent().addClass('active');

        // Update header page title context
        const viewTitles = {
            'dashboard': 'Executive Overview',
            'chat': 'Live Agent Playground',
            'accounts': 'Target Accounts',
            'leads': 'Sales Leads Pipeline',
            'hierarchy': 'Organizational Hierarchy',
            'social': 'Social Intelligence',
            'signals': 'Sales Signals',
            'pipeline': 'Pipeline Engine',
            'logs': 'Execution Logs',
            'settings': 'Agent Profile & Personality'
        };
        $('#page-title').text(viewTitles[targetView] || 'Enterprise Sales Agent');

        // Switch panels
        $('.view-panel').removeClass('active');
        const $targetPanel = $(`#view-${targetView}`);
        $targetPanel.addClass('active');

        activeView = targetView;

        // Re-render charts or reload specific tables if switching views
        if (targetView === 'dashboard') {
            initCharts();
        } else if (targetView === 'chat') {
            loadChatSession(currentSessionId);
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
    // 3. Live Chat Simulator Engine
    // ==========================================
    function loadChatSessionsList() {
        const $list = $('#sessions-list');
        $list.empty();

        mockData.conversations.forEach(c => {
            const lastMsgObj = c.messages[c.messages.length - 1];
            const lastMsgText = lastMsgObj ? lastMsgObj.text : 'No messages yet';
            const isActive = c.id === currentSessionId ? 'active' : '';
            const statusClass = c.status === 'hot' ? 'badge-danger' : (c.status === 'warm' ? 'badge-warning' : 'badge-secondary');
            
            const itemHTML = `
                <div class="session-card ${isActive}" data-id="${c.id}">
                    <div class="session-header">
                        <div class="session-name">${c.leadName}</div>
                        <div class="session-time">${lastMsgObj ? lastMsgObj.time : ''}</div>
                    </div>
                    <div class="session-last-msg">${lastMsgText}</div>
                    <div class="session-meta-row">
                        <span class="intent-badge">${c.intent.replace('_', ' ')}</span>
                        <span class="confidence-score"><i class="bi bi-cpu me-1"></i>${Math.round(c.confidence * 100)}%</span>
                    </div>
                </div>
            `;
            $list.append(itemHTML);
        });

        // Click handler
        $('.session-card').on('click', function () {
            const id = $(this).data('id');
            currentSessionId = id;
            $('.session-card').removeClass('active');
            $(this).addClass('active');
            loadChatSession(id);
        });
    }

    function loadChatSession(id) {
        const session = mockData.conversations.find(c => c.id === id);
        if (!session) return;

        // Header and Meta Panels
        $('#active-lead-name').text(session.leadName);
        $('#active-lead-company').text(session.company);
        $('#active-lead-avatar').text(session.leadName.split(' ').map(n => n[0]).join(''));
        
        // Right Side Intelligence Panel
        $('#intel-lead-name').text(session.leadName);
        $('#intel-lead-company').text(session.company);
        $('#intel-lead-email').text(session.email);
        $('#intel-lead-phone').text(session.phone);
        $('#intel-deal-value').text(`$${session.dealValue.toLocaleString()}`);
        $('#intel-lead-status').html(`<span class="badge bg-${session.status === 'hot' ? 'danger' : (session.status === 'warm' ? 'warning' : 'secondary')}">${session.status.toUpperCase()}</span>`);
        
        $('#intel-intent').text(session.intent.replace('_', ' ').toUpperCase());
        $('#intel-sentiment').text(session.sentiment);
        $('#intel-confidence').text(`${Math.round(session.confidence * 100)}%`);

        // Checkbox human mode takeover state
        $('#human-takeover-toggle').prop('checked', session.agentMode === 'manual');
        updateTakeoverUI(session.agentMode === 'manual');

        // Load Messages
        const $msgBox = $('#chat-messages');
        $msgBox.empty();

        session.messages.forEach(m => {
            const isAI = m.sender === 'agent';
            const msgHTML = `
                <div class="chat-msg-row ${isAI ? 'ai-message' : 'user-message'}">
                    <div class="msg-bubble">
                        <div>${m.text}</div>
                        <div class="msg-meta">
                            <span class="msg-sender ${isAI ? 'ai-name' : 'user-name'}">${isAI ? mockData.agentConfig.agentName : session.leadName}</span>
                            <span>${m.time}</span>
                        </div>
                    </div>
                </div>
            `;
            $msgBox.append(msgHTML);
        });

        // Load Suggested Replies
        const $suggestedBox = $('#suggested-replies-list');
        $suggestedBox.empty();
        
        if (session.suggestedReplies && session.suggestedReplies.length > 0) {
            session.suggestedReplies.forEach((r, idx) => {
                const repHTML = `
                    <div class="suggested-reply-card" data-idx="${idx}">
                        <div class="suggested-action-tag bg-primary text-white">${r.tag}</div>
                        <div class="text-slate-650 opacity-90">${r.text}</div>
                    </div>
                `;
                $suggestedBox.append(repHTML);
            });
            
            // Suggest reply card click handler
            $('.suggested-reply-card').on('click', function () {
                const idx = $(this).data('idx');
                const reply = session.suggestedReplies[idx];
                sendAgentMessage(reply.text, "Suggested Preset Action Applied");
                // Remove this preset from suggestions after send
                session.suggestedReplies.splice(idx, 1);
                loadChatSession(currentSessionId);
            });
        } else {
            $suggestedBox.html('<div class="text-muted text-center py-3 fs-7">No automated templates suggested. Type custom response.</div>');
        }

        // Scroll chat to bottom
        scrollToBottom();
    }

    function scrollToBottom() {
        const $msgBox = $('#chat-messages');
        $msgBox.animate({ scrollTop: $msgBox[0].scrollHeight }, 200);
    }

    // Toggle manual takeover
    $('#human-takeover-toggle').on('change', function () {
        const isManual = $(this).is(':checked');
        const session = mockData.conversations.find(c => c.id === currentSessionId);
        if (session) {
            session.agentMode = isManual ? 'manual' : 'auto';
            updateTakeoverUI(isManual);
            showToast(
                isManual ? 'Human Agent Joined' : 'AI Autopilot Resumed',
                isManual ? `You took manual control of conversation with ${session.leadName}.` : `Autopilot enabled. ${mockData.agentConfig.agentName} will now respond.`,
                isManual ? 'warning' : 'success'
            );
        }
    });

    function updateTakeoverUI(isManual) {
        if (isManual) {
            $('#agent-mode-badge').text('HUMAN ACTIVE').removeClass('bg-success').addClass('bg-warning text-dark');
            $('#chat-input-field').attr('placeholder', 'Type a reply as Representative...');
        } else {
            $('#agent-mode-badge').text('AI AUTOPILOT').removeClass('bg-warning text-dark').addClass('bg-success');
            $('#chat-input-field').attr('placeholder', 'Send simulated message as customer...');
        }
    }

    // Send customer message / User message typing simulator
    $('#send-chat-btn').on('click', function () {
        submitInputMessage();
    });

    $('#chat-input-field').on('keypress', function (e) {
        if (e.which === 13) {
            submitInputMessage();
        }
    });

    function submitInputMessage() {
        const text = $('#chat-input-field').val().trim();
        if (!text) return;

        const session = mockData.conversations.find(c => c.id === currentSessionId);
        if (!session) return;

        const timeString = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        if (session.agentMode === 'manual') {
            // Human agent is responding, add as agent message
            sendAgentMessage(text, "Manual Reply Sent");
        } else {
            // Autopilot mode: Add message as Customer user, trigger AI response
            session.messages.push({
                sender: "user",
                text: text,
                time: timeString
            });

            // Refresh chat viewport
            loadChatSession(currentSessionId);
            loadChatSessionsList();

            // Trigger AI Automated Response Simulation
            simulateAIResponse(text);
        }

        $('#chat-input-field').val('');
    }

    function sendAgentMessage(text, actionType) {
        const session = mockData.conversations.find(c => c.id === currentSessionId);
        if (!session) return;

        const timeString = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        session.messages.push({
            sender: "agent",
            text: text,
            time: timeString,
            intelligence: {
                intent: session.intent,
                sentiment: "Assisted",
                confidence: 1.0,
                retrievedKnowledge: "custom_manual_entry"
            }
        });

        loadChatSession(currentSessionId);
        loadChatSessionsList();
        showToast(actionType, `Message sent to ${session.leadName}.`, 'success');
    }

    function simulateAIResponse(customerText) {
        const session = mockData.conversations.find(c => c.id === currentSessionId);
        if (!session) return;

        const $msgBox = $('#chat-messages');

        // Append Typing indicator bubble
        const typingHTML = `
            <div id="ai-typing" class="chat-msg-row ai-message">
                <div class="msg-bubble">
                    <div class="typing-indicator">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
            </div>
        `;
        $msgBox.append(typingHTML);
        scrollToBottom();

        // 1.5 second delay simulation
        setTimeout(() => {
            $('#ai-typing').remove();

            const timeString = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            
            // Craft intelligence mapping & responsive text
            let aiText = `Thank you for details regarding "${customerText.substring(0, 20)}...". I have noted this in our system log. Let me retrieve custom enterprise SLA details for you.`;
            let intent = "general_query";
            let confidence = 0.85;
            let retrieved = "general_faq_rules";

            const lowTxt = customerText.toLowerCase();
            if (lowTxt.includes('price') || lowTxt.includes('cost') || lowTxt.includes('quote') || lowTxt.includes('pricing') || lowTxt.includes('$')) {
                aiText = `Our pricing ranges from a standard professional growth model at $49/user/month to full custom SLA packages tailored for Enterprise needs starting at $1,200/month. Shall I draft a custom contract estimate?`;
                intent = "pricing_inquiry";
                confidence = 0.96;
                retrieved = "enterprise_pricing_tiers, contract_guidelines";
            } else if (lowTxt.includes('soc') || lowTxt.includes('security') || lowTxt.includes('compliance') || lowTxt.includes('hipaa') || lowTxt.includes('gdpr')) {
                aiText = `We host all customer files under AES-256 encryption standards. We hold an active SOC2 Type II certification, GDPR readiness certificates, and can execute standard BAAs for HIPAA compliance. Would you like our security sheet?`;
                intent = "security_compliance";
                confidence = 0.98;
                retrieved = "security_encryption_levels, soc2_cert, hipaa_baa";
            } else if (lowTxt.includes('compet') || lowTxt.includes('versus') || lowTxt.includes('compared') || lowTxt.includes('mixpanel') || lowTxt.includes('hubspot')) {
                aiText = `Our primary distinction from general CRMs is our advanced AI deflection engine combined with unified data streams, which captures conversion insights at 3x efficiency. No manual sales entry required.`;
                intent = "product_comparison";
                confidence = 0.91;
                retrieved = "vs_mixpanel, sales_automation_advantages";
            } else if (lowTxt.includes('bug') || lowTxt.includes('error') || lowTxt.includes('fail') || lowTxt.includes('broken')) {
                aiText = `I apologize for this issue. I have checked our system logging channels and flagged our Tier 3 support queue. A live engineer is reviewing your profile log telemetry.`;
                intent = "support_issue";
                confidence = 0.89;
                retrieved = "support_escalation_protocol, engineering_on_call";
            }

            // Append to session messages
            session.messages.push({
                sender: "agent",
                text: aiText,
                time: timeString,
                intelligence: {
                    intent: intent,
                    sentiment: "Helpful",
                    confidence: confidence,
                    retrievedKnowledge: retrieved
                }
            });

            // Update session status metrics
            session.intent = intent;
            session.confidence = confidence;
            session.sentiment = "Positive (" + (Math.random() * 0.4 + 0.6).toFixed(2) + ")";

            // Refresh views
            loadChatSession(currentSessionId);
            loadChatSessionsList();
            showToast("AI Agent Replied", `${mockData.agentConfig.agentName} replied to ${session.leadName}.`, 'success');
        }, 1500);
    }

    // Quick Trigger test simulation bar
    $('#btn-trigger-pricing').on('click', function () {
        triggerSimulatedLeadText("Could you outline how much the setup will cost for 300 licenses?");
    });
    $('#btn-trigger-security').on('click', function () {
        triggerSimulatedLeadText("Can you send your SOC2 Type II compliance reports and privacy agreements?");
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
    let recentSearches = ["Sarah Jenkins", "SOC2 compliance", "Pricing", "Hot"];

    function renderSearchHistoryTags() {
        const $tagsBox = $('#search-history-tags');
        $tagsBox.empty();
        recentSearches.forEach(q => {
            $tagsBox.append(`
                <span class="badge bg-light text-slate-700 border border-slate-200 px-2.5 py-1.5 rounded-pill search-history-tag me-1 mb-1" data-query="${q}" style="cursor: pointer; transition: all 0.2s;">
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

        const queryLower = query.toLowerCase();
        let results = [];

        // 1. Search Mock Leads
        if (category === 'all' || category === 'leads') {
            mockData.leads.forEach(l => {
                const leadRole = l.role || "";
                if (l.name.toLowerCase().includes(queryLower) || 
                    l.company.toLowerCase().includes(queryLower) || 
                    l.email.toLowerCase().includes(queryLower) ||
                    leadRole.toLowerCase().includes(queryLower) ||
                    l.status.toLowerCase().includes(queryLower)) {
                    results.push({
                        type: 'Lead (Mock)',
                        title: `${l.name} (${leadRole})`,
                        detail: `${l.company} • ${l.email} • $${l.dealValue.toLocaleString()}`,
                        badge: l.status,
                        badgeClass: l.status === 'Hot' ? 'bg-danger text-white' : (l.status === 'Warm' ? 'bg-warning text-dark' : 'bg-secondary text-white'),
                        icon: 'bi-people',
                        actionText: 'View Pipeline',
                        action: function() {
                            $('.menu-link[data-view="leads"]').trigger('click');
                            $('#lead-search-field').val(l.name).trigger('input');
                        }
                    });
                }
            });
        }

        // 2. Search Mock System Activities
        if (category === 'all' || category === 'activities') {
            const activities = [
                { title: 'Lead Qualified (Hot)', detail: 'Sarah Jenkins (Apex Global Solutions) - $48,000 value', icon: 'bi-activity' },
                { title: 'Security Query Resolved', detail: 'SOC2 Type II documentation dispatched to Elena Rostova', icon: 'bi-shield-check' },
                { title: 'Human Assist Triggered', detail: 'Elena Rostova requested custom SLA review. Autonomous agent paused.', icon: 'bi-exclamation-triangle' },
                { title: 'New Lead Registered', detail: 'Marcus Thorne logged via documentation query flow', icon: 'bi-person-plus' }
            ];
            activities.forEach(act => {
                if (act.title.toLowerCase().includes(queryLower) || act.detail.toLowerCase().includes(queryLower)) {
                    results.push({
                        type: 'Activity',
                        title: act.title,
                        detail: act.detail,
                        badge: 'System Log',
                        badgeClass: 'bg-info text-white',
                        icon: act.icon,
                        actionText: 'See Activity',
                        action: function() {
                            showToast('Activity Details', act.detail, 'info');
                        }
                    });
                }
            });
        }

        // 3. Search Mock NLP Intents / Conversations
        if (category === 'all' || category === 'intents') {
            mockData.conversations.forEach(c => {
                const convRole = c.role || "";
                if (c.leadName.toLowerCase().includes(queryLower) || 
                    c.company.toLowerCase().includes(queryLower) ||
                    convRole.toLowerCase().includes(queryLower) ||
                    c.intent.toLowerCase().includes(queryLower) ||
                    c.sentiment.toLowerCase().includes(queryLower)) {
                    results.push({
                        type: 'Intent / Chat',
                        title: `${c.leadName} (${convRole})`,
                        detail: `${c.company} • Sentiment: ${c.sentiment} • Confidence: ${Math.round(c.confidence * 100)}%`,
                        badge: 'Live Chat',
                        badgeClass: 'bg-primary text-white',
                        icon: 'bi-chat-right-dots',
                        actionText: 'Open Chat',
                        action: function() {
                            currentSessionId = c.id;
                            $('.menu-link[data-view="chat"]').trigger('click');
                        }
                    });
                }
            });
        }

        // Show loading status indicator in list
        $resultsBox.removeClass('hidden');
        $list.html('<div class="text-slate-500 text-center py-3 text-xs"><i class="bi bi-arrow-repeat animate-spin me-2"></i>Querying live enterprise database...</div>');

        // 4. Fetch Real API Results (Organizations and People)
        try {
            const orgsPromise = (category === 'all' || category === 'leads') ? 
                API.get('/chatbot/search/organizations', { q: query }).catch(() => []) : 
                Promise.resolve([]);

            const peoplePromise = (category === 'all' || category === 'leads') ? 
                API.post('/chatbot/search/people', { person_name: query, limit: 10 }).catch(() => ({ items: [] })) : 
                Promise.resolve({ items: [] });

            const peopleOrgPromise = (category === 'all' || category === 'leads') ? 
                API.post('/chatbot/search/people', { organization: query, limit: 10 }).catch(() => ({ items: [] })) : 
                Promise.resolve({ items: [] });

            const [orgs, peopleByName, peopleByOrg] = await Promise.all([
                orgsPromise,
                peoplePromise.then(res => res?.items || []),
                peopleOrgPromise.then(res => res?.items || [])
            ]);

            // Append Organizations
            orgs.forEach(org => {
                results.push({
                    type: 'Organization',
                    title: `${org.name} (${org.ticker || 'N/A'}:${org.exchange || 'N/A'})`,
                    detail: `${org.industry || 'Financial Services'} • ${org.employee_count || 0} employees • Rev: ${org.annual_revenue || 'N/A'}`,
                    badge: 'DB Account',
                    badgeClass: 'bg-indigo-600 text-white',
                    icon: 'bi-building',
                    actionText: 'View Account',
                    action: function() {
                        App.navigate('accounts');
                        setTimeout(() => {
                            $('#account-search-field').val(org.name).trigger('input');
                        }, 150);
                    }
                });
            });

            // Merge and Deduplicate People
            const peopleMap = new Map();
            peopleByName.forEach(p => peopleMap.set(p.id, p));
            peopleByOrg.forEach(p => peopleMap.set(p.id, p));

            peopleMap.forEach(p => {
                results.push({
                    type: 'Executive',
                    title: `${p.full_name} (${p.title || 'Executive'})`,
                    detail: `${p.organization} • ${p.location || 'New York, USA'} • Lead Score: ${p.lead_score || 0}`,
                    badge: p.lead_status || 'Hot',
                    badgeClass: 'bg-teal-600 text-white',
                    icon: 'bi-person-badge',
                    actionText: 'Interactive Dossier',
                    action: function() {
                        App.navigate('hierarchy');
                        setTimeout(() => {
                            if (p.account_id) {
                                $('#hierarchy-account-select').val(p.account_id).trigger('change');
                            }
                        }, 150);
                    }
                });
            });

        } catch (apiErr) {
            console.error("Failed to fetch API search results:", apiErr);
        }

        // Update title and render results
        $('#search-results-title').text(`Search Results (${results.length})`);
        $list.empty();

        if (results.length === 0) {
            $list.append('<div class="text-slate-500 text-center py-3 text-xs">No matching enterprise entities found.</div>');
        } else {
            results.forEach((res, idx) => {
                const itemHTML = `
                    <div class="flex items-center justify-between p-2 hover:bg-slate-100 rounded-lg transition-all border border-slate-100 bg-white">
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

            // Bind click actions
            $('.search-act-btn').off('click').on('click', function () {
                const idx = $(this).data('idx');
                if (results[idx] && typeof results[idx].action === 'function') {
                    results[idx].action();
                }
            });
        }

        $resultsBox.removeClass('hidden');
    }

    // Initial Dashboard Setup Runs
    initCharts();
    loadChatSessionsList();
    loadSettingsForm();
    renderLeadsTable();
    renderSearchHistoryTags();
});
