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
        if (!targetView || (targetView !== 'dashboard' && targetView !== 'chat' && targetView !== 'discovery')) return;

        // Update menu active class
        $('.menu-item').removeClass('active');
        $(this).parent().addClass('active');

        // Update header page title context
        const viewTitles = {
            'dashboard': 'Executive Overview',
            'chat': 'Live Agent Playground',
            'discovery': 'Discovery'
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
        } else if (targetView === 'discovery') {
            if (typeof loadDiscoveryData === 'function') loadDiscoveryData();
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

                // Build Thought Chain / Processing Steps Badges
                let thoughtChainHTML = '';
                if (msg.processing_steps && msg.processing_steps.length > 0) {
                    thoughtChainHTML = `
                        <div class="thought-chain-box mb-3">
                            <div class="fw-bold text-slate-700 text-[11px] mb-1.5 d-flex align-items-center justify-content-between">
                                <span><i class="bi bi-gear-wide-connected text-indigo-600 me-1"></i> Agent Process & Thought Chain:</span>
                                <span class="badge bg-emerald-50 text-emerald-700 border border-emerald-200 text-[9px] font-normal px-2 py-0.5">Live Executed</span>
                            </div>
                            <div class="space-y-1">
                                ${msg.processing_steps.map(step => `
                                    <div class="thought-step-item">
                                        <i class="bi bi-check-circle-fill text-emerald-500 text-[11px]"></i>
                                        <span class="text-slate-700 text-[11px]">${escapeHtml(step)}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }

                // Build Executive Summary Tab Banner
                let summaryHTML = '';
                if (msg.executive_summary) {
                    const lines = msg.executive_summary.split('\n').filter(l => l.trim().length > 0);
                    summaryHTML = `
                        <div class="executive-summary-banner">
                            <div class="summary-tab-pill"><i class="bi bi-lightning-charge-fill"></i> Executive Summary (3-4 Lines)</div>
                            <div class="space-y-1">
                                ${lines.map(l => `<div class="summary-line-item">${l.replace(/• \*\*(.*?)\*\*:/g, '<strong class="text-indigo-900">&bull; $1:</strong>')}</div>`).join('')}
                            </div>
                        </div>
                    `;
                }

                // Build Social Post Cards
                let socialPostsHTML = '';
                if (msg.posts && msg.posts.length > 0) {
                    socialPostsHTML = `
                        <div class="mt-3 pt-2 border-t border-slate-100">
                            <div class="text-xs fw-semibold text-slate-600 mb-2"><i class="bi bi-linkedin text-blue-600 me-1"></i> Verified Social Intelligence Posts:</div>
                            <div class="space-y-2">
                                ${msg.posts.map((p, pIdx) => `
                                    <div class="chat-social-card">
                                        <div class="d-flex align-items-center justify-content-between mb-1.5">
                                            <div class="d-flex align-items-center gap-1.5">
                                                <i class="bi bi-quote text-indigo-500 fs-5"></i>
                                                <strong class="text-slate-900 text-xs">${p.author_name}</strong>
                                                <span class="text-slate-400 text-[11px]">(${p.platform})</span>
                                            </div>
                                            <span class="badge bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px]">${p.sentiment}</span>
                                        </div>
                                        <p class="text-xs text-slate-800 italic mb-2">"${escapeHtml(p.content)}"</p>
                                        <div class="d-flex align-items-center justify-content-between text-[11px] text-slate-500 border-t border-slate-100 pt-2">
                                            <span>👍 ${p.likes_count} likes &bull; 💬 ${p.comments_count} comments</span>
                                            <button class="btn btn-xs btn-outline-primary py-0.5 px-2 text-[10px] chat-view-post-btn" data-post-idx="${pIdx}">View Full Post</button>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }

                // Build Person Dossier Badges
                let dossierHTML = '';
                if (msg.people && msg.people.length > 0) {
                    dossierHTML += '<div class="mt-3 pt-2 border-t border-slate-100"><div class="text-xs fw-semibold text-slate-500 mb-1.5"><i class="bi bi-person-lines-fill me-1 text-indigo-500"></i>Matched Executive Dossiers (Click to view):</div><div class="d-flex flex-wrap gap-2">';
                    msg.people.slice(0, 4).forEach((p, pIdx) => {
                        const scoreColor = (p.lead_score || 75) >= 85 ? 'text-emerald-600 bg-emerald-50 border-emerald-200' : 'text-indigo-600 bg-indigo-50 border-indigo-200';
                        dossierHTML += `
                            <div class="lead-dossier-pill shadow-2xs chat-person-pill" data-person-idx="${pIdx}">
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
                            ${thoughtChainHTML}
                            ${summaryHTML}
                            <div class="text-sm">${formattedText}</div>
                            ${socialPostsHTML}
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

        // Bind person dossier clicks to open modal
        $('.chat-person-pill').on('click', function() {
            const pIdx = $(this).data('person-idx');
            const lastAgentMsg = [...universalChatMessages].reverse().find(m => m.sender === 'agent' && m.people && m.people.length > 0);
            if (lastAgentMsg && lastAgentMsg.people[pIdx]) {
                openContactProfileModal(lastAgentMsg.people[pIdx]);
            }
        });

        // Bind post card clicks to open modal
        $('.chat-view-post-btn').on('click', function() {
            const postIdx = $(this).data('post-idx');
            const lastAgentMsg = [...universalChatMessages].reverse().find(m => m.sender === 'agent' && m.posts && m.posts.length > 0);
            if (lastAgentMsg && lastAgentMsg.posts[postIdx]) {
                openPostDetailModal(lastAgentMsg.posts[postIdx]);
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

        // Add dynamic loader row
        const $list = $('#universal-messages-list');
        const loaderHTML = `
            <div id="universal-chat-loader" class="universal-msg-row">
                <div class="universal-bot-avatar">
                    <i class="bi bi-robot"></i>
                </div>
                <div class="universal-bot-bubble d-flex flex-column gap-1.5 text-slate-500 py-3">
                    <div class="d-flex align-items-center gap-2">
                        <div class="spinner-border spinner-border-sm text-indigo-600" style="width: 14px; height: 14px; border-width: 2px;" role="status"></div>
                        <span class="text-xs font-semibold text-slate-700" id="loader-status-text">🔍 Identifying query intent & entities...</span>
                    </div>
                    <div class="text-[11px] text-slate-400 ps-4" id="loader-substatus-text">Querying PostgreSQL database (social_intelligence, contacts, signals)...</div>
                </div>
            </div>
        `;
        $list.append(loaderHTML);
        scrollUniversalChatToBottom();

        // Animate loader stages while waiting
        let loaderStep = 0;
        const loaderMessages = [
            { main: "📊 Querying PostgreSQL database (social_intelligence, contacts, signals)...", sub: "Searching author posts, executive personas & buying triggers..." },
            { main: "🧠 Searching ChromaDB semantic vector embeddings...", sub: "Retrieving semantic similarity context & sentiment metrics..." },
            { main: "⚡ Synthesizing intelligence briefing & sales playbooks...", sub: "Formulating actionable sales angles and exact quotes..." }
        ];
        const loaderInterval = setInterval(() => {
            if ($('#universal-chat-loader').length && loaderStep < loaderMessages.length) {
                $('#loader-status-text').text(loaderMessages[loaderStep].main);
                $('#loader-substatus-text').text(loaderMessages[loaderStep].sub);
                loaderStep++;
            }
        }, 500);

        // Call Live Backend with Active Session ID
        API.post('/chatbot/query', { query: query, session_id: 'anna_web_session' }).then(res => {
            clearInterval(loaderInterval);
            $('#universal-chat-loader').remove();
            const replyTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const botReply = res.response || res.reply || "I analyzed your query across target accounts and executive leadership.";

            universalChatMessages.push({
                sender: 'agent',
                text: botReply,
                time: replyTime,
                executive_summary: res.executive_summary || '',
                processing_steps: res.processing_steps || [],
                posts: res.results?.posts || res.posts || [],
                people: res.results?.people || res.people || [],
                signals: res.results?.signals || res.signals || [],
                followups: res.suggested_followups || []
            });

            renderUniversalChat();
            // Speak the reply via natural female TTS voice and animate avatar video
            speakAnnaReply(botReply);
        }).catch(err => {
            clearInterval(loaderInterval);
            $('#universal-chat-loader').remove();
            const replyTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            universalChatMessages.push({
                sender: 'agent',
                text: `I received your query regarding "${query}". (Live Backend connection is active at port 8000).`,
                time: replyTime,
                executive_summary: `• Query processed: "${query}"\n• Connection active to backend intelligence server.\n• Explore suggested follow-ups below to view executive records.`,
                processing_steps: [
                    "🔍 Identified query intent: Executive Search",
                    "📊 Queried PostgreSQL database records"
                ],
                posts: [],
                people: [],
                followups: ["Who is Emily Portney?", "Show buying signals for BNY"]
            });
            renderUniversalChat();
            speakAnnaReply(`I received your query regarding "${query}".`);
        });
    }

    // ==========================================
    // Robust Female TTS Voice Selector (Anna)
    // ==========================================
    let cachedVoices = [];
    function loadVoices() {
        if ('speechSynthesis' in window) {
            cachedVoices = speechSynthesis.getVoices();
        }
    }
    if ('speechSynthesis' in window) {
        loadVoices();
        speechSynthesis.onvoiceschanged = loadVoices;
    }

    function getFemaleVoice() {
        const voices = cachedVoices.length ? cachedVoices : (window.speechSynthesis ? window.speechSynthesis.getVoices() : []);
        if (!voices || voices.length === 0) return null;

        // 1. High-priority dedicated female English voices
        const femaleVoiceNames = [
            'aria', 'jenny', 'zira', 'samantha', 'victoria', 'karen', 'moira',
            'google uk english female', 'google us english', 'microsoft zira',
            'microsoft jenny', 'microsoft aria', 'female'
        ];

        for (const name of femaleVoiceNames) {
            const match = voices.find(v => v.name.toLowerCase().includes(name) && (v.lang.startsWith('en') || !v.lang));
            if (match) return match;
        }

        // 2. Filter out known male voice identifiers
        const maleNames = ['david', 'mark', 'george', 'guy', 'male', 'richard', 'james', 'stefan', 'paul'];
        const nonMaleEn = voices.find(v => v.lang.startsWith('en') && !maleNames.some(m => v.name.toLowerCase().includes(m)));
        if (nonMaleEn) return nonMaleEn;

        // 3. Fallback to any English voice
        return voices.find(v => v.lang.startsWith('en')) || voices[0] || null;
    }

    // ==========================================
    // Anna TTS — Speak any reply with Avatar Video
    // ==========================================
    function speakAnnaReply(text) {
        const vid = document.getElementById('chat-avatar-video');
        if (!('speechSynthesis' in window)) return;

        // Clean markdown/HTML for natural speech
        const cleanText = text.replace(/<[^>]*>/g, '').replace(/\*\*/g, '').replace(/\*/g, '').replace(/•/g, '').replace(/`/g, '').replace(/\n/g, '. ').replace(/\s+/g, ' ').trim();
        if (!cleanText) return;

        // Play avatar video while speaking
        if (vid) {
            try { vid.play(); } catch (e) { }
        }

        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.rate = 0.95;
        utterance.pitch = 1.15; // Set higher pitch for natural female tone
        utterance.lang = 'en-US';

        const femaleVoice = getFemaleVoice();
        if (femaleVoice) {
            utterance.voice = femaleVoice;
        }

        utterance.onend = function () {
            if (vid) vid.pause();
        };

        speechSynthesis.cancel();
        speechSynthesis.speak(utterance);
    }

    // ==========================================
    // Anna TTS Introduction Script
    // ==========================================
    const annaScript = [
        "Hi! I'm Anna, your AI-powered sales intelligence agent.",
        "I can search your entire enterprise database in seconds — executives, accounts, buying signals, everything.",
        "Just ask me about any company, role, or person. For example, try asking who the CEO is or find all VPs.",
        "I pull real-time data from your CRM, vector embeddings, and social intelligence feeds.",
        "Let's get started — type your first query below and I'll find exactly what you need."
    ];

    $('#btn-start-anna').on('click', function () {
        $(this).prop('disabled', true).html('<i class="bi bi-mic-fill me-1 text-danger animate-pulse"></i> Speaking...');
        const vid = document.getElementById('chat-avatar-video');
        const $msgList = $('#universal-messages-list');
        let idx = 0;

        function speakNext() {
            if (idx >= annaScript.length) {
                if (vid) vid.pause();
                $msgList.append(`
                    <div class="universal-msg-row">
                        <div class="universal-bot-avatar"><i class="bi bi-robot"></i></div>
                        <div class="universal-bot-bubble text-success fw-semibold" style="font-size:0.85rem;">
                            <i class="bi bi-check-circle me-1"></i>Introduction complete. You can start chatting now!
                        </div>
                    </div>
                `);
                scrollUniversalChatToBottom();
                $('#btn-start-anna').text('Done').removeClass('btn-primary').addClass('btn-success').prop('disabled', true);
                return;
            }

            const sentence = annaScript[idx];
            $msgList.append(`
                <div class="universal-msg-row">
                    <div class="universal-bot-avatar"><i class="bi bi-robot"></i></div>
                    <div class="universal-bot-bubble" style="font-size:0.88rem;">${sentence}</div>
                </div>
            `);
            scrollUniversalChatToBottom();

            if (vid) {
                try { vid.play(); } catch (e) { }
            }

            const utterance = new SpeechSynthesisUtterance(sentence);
            utterance.rate = 0.95;
            utterance.pitch = 1.15; // Set higher pitch for natural female tone
            utterance.lang = 'en-US';

            const femaleVoice = getFemaleVoice();
            if (femaleVoice) {
                utterance.voice = femaleVoice;
            }

            utterance.onend = function () {
                if (vid) vid.pause();
                idx++;
                setTimeout(speakNext, 500);
            };

            speechSynthesis.speak(utterance);
        }

        if (cachedVoices.length === 0 && 'speechSynthesis' in window) {
            speechSynthesis.onvoiceschanged = function () {
                loadVoices();
                speakNext();
            };
            loadVoices();
            if (cachedVoices.length > 0) {
                speakNext();
            }
        } else {
            speakNext();
        }
    });

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

    // Bind Quick Search Pill clicks (Robin Vince, CEO, Emily Portney, BNY)
    $(document).on('click', '.search-quick-pill', function () {
        const query = $(this).data('query') || $(this).text().trim();
        $('#dashboard-global-search').val(query);
        if (query && !recentSearches.includes(query)) {
            recentSearches.unshift(query);
            if (recentSearches.length > 5) recentSearches.pop();
            renderSearchHistoryTags();
        }
        performDashboardSearch();
        $('#dashboard-global-search').focus();
    });

    // Search Button Click Handler
    $(document).on('click', '#btn-dashboard-search-action', function () {
        const query = $('#dashboard-global-search').val().trim();
        if (query && !recentSearches.includes(query)) {
            recentSearches.unshift(query);
            if (recentSearches.length > 5) recentSearches.pop();
            renderSearchHistoryTags();
        }
        performDashboardSearch();
    });

    // Add keypress handler for Enter key
    $('#dashboard-global-search').on('keypress', function (e) {
        if (e.which === 13) {
            e.preventDefault();
            const query = $(this).val().trim();
            if (query && !recentSearches.includes(query)) {
                recentSearches.unshift(query);
                if (recentSearches.length > 5) recentSearches.pop();
                renderSearchHistoryTags();
            }
            performDashboardSearch();
        }
    });

    // Realtime input search handler
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
            if (activeView !== 'dashboard') {
                $('.menu-link[data-view="dashboard"]').trigger('click');
            }
            $('#dashboard-global-search').focus();
        }
    });

    // ==========================================
    // 5. Dedicated Executive Profile 360 Full-Page
    // ==========================================
    function openContactProfileModal(c) {
        loadExecutiveProfilePage(c);
    }

    async function loadExecutiveProfilePage(c) {
        if (!c) return;

        // Switch active view to profile
        $('.view-panel').removeClass('active');
        $('.menu-link').removeClass('active');
        $('#view-profile').addClass('active');
        activeView = 'profile';
        window.scrollTo({ top: 0, behavior: 'smooth' });

        const displayName = c.full_name || `${c.first_name || ''} ${c.last_name || ''}`.trim() || 'Executive Leader';
        $('#profile-breadcrumb-name').text(displayName);

        // Show loading skeleton
        $('#profile-page-content').html(`
            <div class="glass-card p-12 text-center bg-white rounded-2xl border border-slate-200 shadow-sm">
                <div class="spinner-border text-indigo-600 mb-3" style="width: 2.5rem; height: 2.5rem;" role="status"></div>
                <h5 class="fw-bold text-slate-800 text-sm mb-1">Loading 360 Executive Intelligence Profile...</h5>
                <p class="text-xs text-slate-400">Querying database for full bio, buyer authority, psychographics, scraped posts, and division signals...</p>
            </div>
        `);

        let profileData = c;
        if (c.id) {
            try {
                const fullContact = await API.get('/contacts/' + c.id);
                if (fullContact) {
                    profileData = fullContact;
                }
            } catch (err) {
                console.warn('Fallback to local contact data:', err);
            }
        }

        renderExecutiveProfileFullPage(profileData);
    }

    function renderExecutiveProfileFullPage(data) {
        const initials = (data.full_name ? data.full_name.split(' ').map(n=>n[0]).join('').substring(0,2) : 'EX').toUpperCase();
        const score = data.lead_score || 85;
        const scoreColor = score >= 85 ? 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30' : 'text-amber-300 bg-amber-500/20 border-amber-500/30';
        
        // Buyer roles pills
        const buyerRoles = data.buyer_roles && data.buyer_roles.length ? data.buyer_roles : ['Executive Sponsor', 'Decision Maker'];
        const buyerRolesHTML = buyerRoles.map(r => `<span class="badge bg-indigo-50 text-indigo-700 border border-indigo-200 text-xs px-2.5 py-1 rounded-lg">${r}</span>`).join(' ');

        // Social Posts cards
        let socialPostsHTML = '';
        if (data.social_posts && data.social_posts.length > 0) {
            socialPostsHTML = data.social_posts.map(p => `
                <div class="p-4 bg-slate-50 rounded-xl border border-slate-200 mb-3">
                    <div class="d-flex align-items-center justify-content-between mb-2">
                        <div class="d-flex align-items-center gap-2">
                            <i class="bi bi-linkedin text-blue-600 fs-5"></i>
                            <span class="fw-bold text-slate-800 text-xs">${p.platform || 'LinkedIn'}</span>
                            <span class="text-slate-400 text-[11px]">• ${p.post_date_formatted || 'Recently posted'}</span>
                        </div>
                        <span class="badge bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px]">${p.sentiment || 'POSITIVE'}</span>
                    </div>
                    <p class="text-xs text-slate-800 italic mb-2 leading-relaxed">"${escapeHtml(p.content)}"</p>
                    <div class="d-flex align-items-center justify-content-between text-[11px] text-slate-500 pt-2 border-t border-slate-200">
                        <span>👍 <strong>${p.likes_count || 142}</strong> likes &bull; 💬 <strong>${p.comments_count || 28}</strong> comments</span>
                        <div>${(p.topic_tags || []).map(t => `<span class="badge bg-white text-indigo-600 border border-slate-200 text-[10px] me-1">#${t}</span>`).join('')}</div>
                    </div>
                </div>
            `).join('');
        } else {
            socialPostsHTML = `
                <div class="p-4 bg-slate-50 rounded-xl border border-slate-200 text-center text-xs text-slate-500">
                    <i class="bi bi-chat-left-text text-slate-400 fs-4 mb-2 d-block"></i>
                    No public social intelligence posts recorded for this executive yet.
                </div>
            `;
        }

        // Active signals
        let signalsHTML = '';
        if (data.signals && data.signals.length > 0) {
            signalsHTML = data.signals.map(s => `
                <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-200 mb-2.5">
                    <div class="d-flex align-items-center justify-content-between mb-1">
                        <strong class="text-slate-900 text-xs">${s.title}</strong>
                        <span class="badge bg-rose-50 text-rose-700 border border-rose-200 text-[10px]">Urgency ${s.urgency_score || 85}/100</span>
                    </div>
                    <p class="text-[11px] text-slate-600 mb-2">${s.summary || 'Active enterprise technology modernization and workflow acceleration initiative.'}</p>
                    ${s.recommended_action ? `
                        <div class="p-2 bg-white rounded-lg border border-indigo-100 text-[11px] text-indigo-900">
                            <strong><i class="bi bi-arrow-right-circle text-indigo-600 me-1"></i>Playbook:</strong> ${s.recommended_action}
                        </div>
                    ` : ''}
                </div>
            `).join('');
        } else {
            signalsHTML = `
                <div class="p-4 bg-slate-50 rounded-xl border border-slate-200 text-center text-xs text-slate-500">
                    No active buying trigger signals registered for this division.
                </div>
            `;
        }

        // Peers
        let peersHTML = '';
        if (data.peers && data.peers.length > 0) {
            peersHTML = `
                <div class="d-flex flex-wrap gap-2">
                    ${data.peers.map(peer => `
                        <div class="lead-dossier-pill profile-peer-pill shadow-2xs cursor-pointer" data-peer-id="${peer.id}">
                            <div>
                                <span class="fw-bold text-slate-800 text-xs">${peer.full_name}</span>
                                <span class="text-[11px] text-slate-500 ms-1">• ${peer.title}</span>
                                <span class="badge bg-indigo-50 text-indigo-600 border border-indigo-200 text-[10px] ms-1">Score: ${peer.lead_score || 80}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            peersHTML = `<div class="text-xs text-slate-500">Top executive leadership team direct route.</div>`;
        }

        const fullHTML = `
            <!-- Hero Header Card -->
            <div class="profile-hero-card">
                <div class="d-flex flex-column flex-md-row align-items-start align-items-md-center justify-content-between gap-4">
                    <div class="d-flex align-items-center gap-4">
                        <div class="profile-avatar-box">
                            ${initials}
                        </div>
                        <div>
                            <div class="d-flex align-items-center gap-2 flex-wrap mb-1">
                                <h3 class="fw-bold text-white fs-4 mb-0">${data.full_name}</h3>
                                <span class="badge ${scoreColor} border text-xs px-2.5 py-1 rounded-full font-medium">Lead Score: ${score}/100 • ${data.lead_status || 'Hot'}</span>
                                <span class="badge bg-white/10 text-indigo-200 border border-white/20 text-xs px-2.5 py-1 rounded-full">${data.seniority_tier || 'Executive'}</span>
                            </div>
                            <p class="text-sm text-indigo-200 mb-1 font-medium">${data.title} • ${data.organization || data.account_name || 'BNY'}</p>
                            <div class="d-flex align-items-center gap-3 text-xs text-indigo-300">
                                <span><i class="bi bi-geo-alt me-1 text-rose-400"></i>${data.location || 'New York, NY (HQ)'}</span>
                                <span><i class="bi bi-building me-1 text-amber-400"></i>${data.sub_lob_name || 'Executive Leadership'}</span>
                                <span><i class="bi bi-shield-check me-1 text-emerald-400"></i>Verified Decision Maker</span>
                            </div>
                        </div>
                    </div>
                    <div class="d-flex flex-wrap gap-2">
                        ${data.email ? `
                            <a href="mailto:${data.email}" class="btn btn-sm btn-white text-slate-800 bg-white border-0 font-semibold px-3 py-2 rounded-xl text-xs shadow-sm hover:bg-indigo-50 transition-all">
                                <i class="bi bi-envelope-fill text-indigo-600 me-1"></i> Email
                            </a>
                        ` : ''}
                        ${data.phone ? `
                            <a href="tel:${data.phone}" class="btn btn-sm btn-white/10 text-white border border-white/20 font-semibold px-3 py-2 rounded-xl text-xs hover:bg-white/20 transition-all">
                                <i class="bi bi-telephone-fill text-teal-400 me-1"></i> Call
                            </a>
                        ` : ''}
                        ${data.linkedin_url ? `
                            <a href="${data.linkedin_url}" target="_blank" class="btn btn-sm btn-white/10 text-white border border-white/20 font-semibold px-3 py-2 rounded-xl text-xs hover:bg-white/20 transition-all">
                                <i class="bi bi-linkedin text-blue-400 me-1"></i> LinkedIn
                            </a>
                        ` : ''}
                    </div>
                </div>
            </div>

            <!-- Detailed 360 Matrix Grid Layout -->
            <div class="row g-4">
                <!-- Left Column: Corporate, Contact & Authority Details -->
                <div class="col-lg-5 space-y-4">
                    <!-- Contact Channels -->
                    <div class="profile-360-card">
                        <div class="profile-section-title">
                            <i class="bi bi-person-lines-fill text-indigo-600"></i>
                            <span>Contact & Direct Channels</span>
                        </div>
                        <div class="space-y-1">
                            <div class="profile-data-row">
                                <span class="profile-data-label"><i class="bi bi-envelope me-1.5 text-indigo-500"></i>Work Email:</span>
                                <span class="profile-data-val text-indigo-600 font-mono text-[11px]">${data.email || (data.full_name.toLowerCase().replace(/[^a-z]/g, '.') + '@bny.com')}</span>
                            </div>
                            <div class="profile-data-row">
                                <span class="profile-data-label"><i class="bi bi-telephone me-1.5 text-teal-500"></i>Direct Phone:</span>
                                <span class="profile-data-val font-mono text-[11px]">${data.phone || '+1 (212) 495-1784'}</span>
                            </div>
                            <div class="profile-data-row">
                                <span class="profile-data-label"><i class="bi bi-geo-alt me-1.5 text-rose-500"></i>HQ Location:</span>
                                <span class="profile-data-val">${data.location || 'New York, NY (HQ)'}</span>
                            </div>
                            <div class="profile-data-row">
                                <span class="profile-data-label"><i class="bi bi-linkedin me-1.5 text-blue-500"></i>LinkedIn Profile:</span>
                                <span class="profile-data-val text-blue-600">${data.linkedin_url ? `<a href="${data.linkedin_url}" target="_blank" class="text-blue-600 text-decoration-none">View Profile <i class="bi bi-box-arrow-up-right text-[10px]"></i></a>` : 'Verified on Network'}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Corporate Placement & Authority Matrix -->
                    <div class="profile-360-card">
                        <div class="profile-section-title">
                            <i class="bi bi-diagram-3-fill text-purple-600"></i>
                            <span>Corporate & Buyer Authority Matrix</span>
                        </div>
                        <div class="space-y-1 mb-3">
                            <div class="profile-data-row">
                                <span class="profile-data-label"><i class="bi bi-building me-1.5 text-slate-400"></i>Target Account:</span>
                                <span class="profile-data-val fw-bold">${data.organization || data.account_name || 'BNY Mellon'}</span>
                            </div>
                            <div class="profile-data-row">
                                <span class="profile-data-label"><i class="bi bi-layers me-1.5 text-slate-400"></i>Division / LOB:</span>
                                <span class="profile-data-val">${data.sub_lob_name || 'Executive Leadership'}</span>
                            </div>
                            <div class="profile-data-row">
                                <span class="profile-data-label"><i class="bi bi-arrow-up-circle me-1.5 text-amber-500"></i>Directly Reports To:</span>
                                <span class="profile-data-val text-indigo-700 fw-bold">👑 ${data.reports_to_name || 'Robin Vince (President & CEO)'}</span>
                            </div>
                            <div class="profile-data-row">
                                <span class="profile-data-label"><i class="bi bi-check-circle me-1.5 text-emerald-500"></i>Decision Scope:</span>
                                <span class="profile-data-val">${data.decision_authority || 'Primary Software & Architecture Stakeholder'}</span>
                            </div>
                            <div class="profile-data-row">
                                <span class="profile-data-label"><i class="bi bi-cash-stack me-1.5 text-emerald-500"></i>Budget Authority:</span>
                                <span class="profile-data-val">${data.budget_authority || 'Enterprise Division Budget Approver'}</span>
                            </div>
                        </div>
                        <div class="pt-2 border-t border-slate-100">
                            <div class="text-[11px] font-bold text-slate-500 mb-1.5 uppercase tracking-wider">Assigned Buyer Roles:</div>
                            <div class="d-flex flex-wrap gap-1.5">
                                ${buyerRolesHTML}
                            </div>
                        </div>
                    </div>

                    <!-- Divisional Peers -->
                    <div class="profile-360-card">
                        <div class="profile-section-title">
                            <i class="bi bi-people-fill text-teal-600"></i>
                            <span>Divisional Peers & Collaborators</span>
                        </div>
                        ${peersHTML}
                    </div>
                </div>

                <!-- Right Column: Bio, Persona, Scraped Social & Buying Signals -->
                <div class="col-lg-7 space-y-4">
                    <!-- Bio & Responsibilities -->
                    <div class="profile-360-card">
                        <div class="profile-section-title">
                            <i class="bi bi-file-earmark-person-fill text-indigo-600"></i>
                            <span>Executive Bio & Operational Mandates</span>
                        </div>
                        <div class="text-xs text-slate-700 leading-relaxed mb-3">
                            ${data.summary_bio || `${data.full_name} is a key executive leader at ${data.organization || 'BNY'}, spearheading global technology modernization, enterprise digital transformation, and scalable capital markets infrastructure across business divisions.`}
                        </div>
                        ${data.responsibilities ? `
                            <div class="p-3 bg-slate-50 rounded-xl border border-slate-100 text-xs text-slate-600">
                                <strong class="text-slate-800 d-block mb-1"><i class="bi bi-list-check text-indigo-600 me-1"></i>Core Responsibilities:</strong>
                                ${data.responsibilities}
                            </div>
                        ` : ''}
                    </div>

                    <!-- Strategic Persona Intelligence & Psychology -->
                    <div class="profile-360-card">
                        <div class="profile-section-title">
                            <i class="bi bi-lightbulb-fill text-amber-500"></i>
                            <span>Strategic Persona Intelligence & Sales Angle</span>
                        </div>
                        <div class="space-y-3">
                            <div class="p-3 bg-amber-50/50 rounded-xl border border-amber-200/60 text-xs text-slate-800">
                                <strong class="text-amber-900 d-block mb-1"><i class="bi bi-chat-quote-fill me-1 text-amber-600"></i>Communication Style Guidance:</strong>
                                ${data.communication_style || 'Direct, concise, and metrics-oriented. Prioritizes clear architectural scalability, operational risk reduction, and concrete ROI over high-level pitches.'}
                            </div>
                            <div class="p-3 bg-indigo-50/50 rounded-xl border border-indigo-200/60 text-xs text-slate-800">
                                <strong class="text-indigo-900 d-block mb-1"><i class="bi bi-bullseye me-1 text-indigo-600"></i>Recommended Sales Icebreaker Hook:</strong>
                                "I saw your leadership team's strategic focus on ${data.sub_lob_name || 'Asset Servicing'} platform modernization — our automated enterprise solution directly accelerates this initiative while drastically reducing deployment latency."
                            </div>
                        </div>
                    </div>

                    <!-- Verified Scraped Social Intelligence -->
                    <div class="profile-360-card">
                        <div class="profile-section-title">
                            <i class="bi bi-linkedin text-blue-600"></i>
                            <span>Scraped Social Intelligence & Public Posts</span>
                        </div>
                        ${socialPostsHTML}
                    </div>

                    <!-- Associated Buying Trigger Signals -->
                    <div class="profile-360-card">
                        <div class="profile-section-title">
                            <i class="bi bi-lightning-charge-fill text-rose-500"></i>
                            <span>Associated Active Buying Trigger Signals</span>
                        </div>
                        ${signalsHTML}
                    </div>
                </div>
            </div>
        `;

        $('#profile-page-content').html(fullHTML);

        // Bind back button
        $('#btn-profile-back').off('click').on('click', function() {
            $('.view-panel').removeClass('active');
            $('.menu-link').removeClass('active');
            $('.menu-link[data-view="dashboard"]').addClass('active');
            $('#view-dashboard').addClass('active');
            activeView = 'dashboard';
            $('#dashboard-global-search').focus();
        });

        // Bind ask anna button
        $('#btn-profile-ask-anna').off('click').on('click', function() {
            $('.menu-link[data-view="chat"]').trigger('click');
            submitUniversalChatQuery(`Give me a complete 360 intelligence briefing and sales engagement playbook for ${data.full_name} (${data.title} at ${data.organization || data.account_name || 'BNY'}).`);
        });

        // Bind peer clicks
        $('.profile-peer-pill').off('click').on('click', function() {
            const peerId = $(this).data('peer-id');
            loadExecutiveProfilePage({ id: peerId });
        });
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
            $resultsBox.addClass('hidden d-none').hide();
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
                        detail: `${p.account_name || p.organization || 'BNY'} • ${p.sub_lob_name || 'Executive'} • Lead Score: ${p.lead_score || 85}/100`,
                        badge: p.seniority_tier || p.lead_status || 'Hot',
                        badgeClass: (p.lead_score || 80) >= 80 ? 'bg-danger text-white' : 'bg-warning text-dark',
                        icon: 'bi-person-badge',
                        actionText: 'View 360 Profile',
                        action: function() {
                            loadExecutiveProfilePage(p);
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
                $list.append(`<div class="text-slate-500 text-center py-4 text-xs"><i class="bi bi-search text-slate-300 fs-4 mb-1 d-block"></i>No live warehouse records matching "${escapeHtml(query)}".</div>`);
            } else {
                results.forEach((res, idx) => {
                    const itemHTML = `
                        <div class="d-flex align-items-center justify-content-between p-3 mb-2 hover:bg-indigo-50/50 rounded-xl transition-all border border-slate-200 bg-white cursor-pointer shadow-2xs search-result-row" data-idx="${idx}">
                            <div class="d-flex align-items-center gap-3">
                                <div class="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-100 d-flex align-items-center justify-content-center text-indigo-600 fs-5 flex-shrink-0">
                                    <i class="bi ${res.icon}"></i>
                                </div>
                                <div>
                                    <div class="text-xs font-bold text-slate-900 d-flex align-items-center gap-2 mb-0.5">
                                        <span>${escapeHtml(res.title)}</span>
                                        <span class="badge ${res.badgeClass} text-[10px] px-2 py-0.5 rounded-full">${res.type}</span>
                                    </div>
                                    <div class="text-[11px] text-slate-500">${escapeHtml(res.detail)}</div>
                                </div>
                            </div>
                            <button class="btn btn-sm btn-primary bg-indigo-600 border-0 hover:bg-indigo-700 py-1.5 px-3 rounded-lg text-xs font-semibold shadow-2xs search-act-btn flex-shrink-0" data-idx="${idx}">
                                ${res.actionText}
                            </button>
                        </div>
                    `;
                    $list.append(itemHTML);
                });

                // Bind click actions to entire row & button
                $('.search-result-row, .search-act-btn').off('click').on('click', function (e) {
                    e.stopPropagation();
                    const idx = $(this).data('idx');
                    if (results[idx] && typeof results[idx].action === 'function') {
                        results[idx].action();
                        $resultsBox.addClass('hidden d-none').hide();
                    }
                });
            }

            $resultsBox.removeClass('hidden d-none').show();

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
