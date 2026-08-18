// Chatbot Page - Bootstrap 5 Version
const ChatbotPage = {
    render() {
        return `
        <div class="fade-in h-100 d-flex flex-column">
            <div class="mb-4 d-flex justify-content-between align-items-center">
                <div>
                    <h3 class="h4 fw-bold text-dark mb-1"><i class="bi bi-robot text-primary me-2"></i>AI Assistant Hub</h3>
                    <p class="text-muted small mb-0">Search target companies, executive leads, role definitions, and team alignments using natural language.</p>
                </div>
                <button class="btn btn-sm btn-outline-danger d-flex align-items-center gap-2" style="border-radius: 8px;" onclick="ChatbotPage.clearChat()">
                    <i class="bi bi-trash3-fill"></i>
                    <span>Clear Chat</span>
                </button>
            </div>

            <div class="row g-4 flex-grow-1" style="min-height: 520px;">
                <!-- Left Sidebar: Session Info & History -->
                <div class="col-12 col-lg-4">
                    <div class="d-flex flex-column gap-3 h-100">
                        <!-- Session Profile Card -->
                        <div class="card border-0 shadow-sm bg-white p-4">
                            <h5 class="card-title h6 fw-bold mb-3 d-flex align-items-center gap-2">
                                <i class="bi bi-cpu text-primary"></i>AI Session Profile
                            </h5>
                            <div class="d-flex flex-column gap-2 text-dark" style="font-size: 0.8rem;">
                                <div class="d-flex justify-content-between py-1 border-bottom border-light">
                                    <span class="text-muted">Active Model</span>
                                    <span class="fw-semibold text-primary">SalesGPT-4o</span>
                                </div>
                                <div class="d-flex justify-content-between py-1 border-bottom border-light">
                                    <span class="text-muted">Response Mode</span>
                                    <span class="fw-semibold">Structured Profile</span>
                                </div>
                                <div class="d-flex justify-content-between py-1 border-bottom border-light">
                                    <span class="text-muted">Target Sync</span>
                                    <span class="text-success"><i class="bi bi-patch-check-fill me-1"></i>Live DB Connection</span>
                                </div>
                                <div class="d-flex justify-content-between py-1">
                                    <span class="text-muted">Search Mode</span>
                                    <span class="fw-semibold text-secondary">Natural Language</span>
                                </div>
                            </div>
                        </div>

                        <!-- Recent Queries Card -->
                        <div class="card border-0 shadow-sm bg-white p-4 flex-grow-1 mb-0">
                            <h5 class="card-title h6 fw-bold mb-3 d-flex align-items-center gap-2">
                                <i class="bi bi-clock-history text-secondary"></i>Recent Queries
                            </h5>
                            <div id="chatHistoryList" class="d-flex flex-column gap-2 overflow-y-auto" style="max-height: 280px;">
                                <!-- Dynamic History -->
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Chat Workspace -->
                <div class="col-12 col-lg-8 d-flex flex-column">
                    <div class="card border-0 shadow-sm bg-white mb-0 d-flex flex-column flex-grow-1" style="height: 100%; min-height: 480px; border-radius: 16px;">
                        <!-- Messages Area -->
                        <div class="card-body bg-light p-4 overflow-y-auto d-flex flex-column gap-3" id="pageChatbotMessages" style="flex-grow: 1; height: 400px; border-top-left-radius: 16px; border-top-right-radius: 16px;">
                            <div class="chat-message bot-message bg-white p-3 rounded-3 shadow-sm text-dark align-self-start" style="max-width: 80%; font-size: 0.88rem; border-bottom-left-radius: 0 !important; border-radius: 12px; line-height: 1.5;">
                                <div class="d-flex align-items-center gap-2 mb-2">
                                    <div class="bg-primary text-white rounded-circle p-1 d-flex align-items-center justify-content-center" style="width: 24px; height: 24px;">
                                        <i class="bi bi-robot" style="font-size: 0.8rem;"></i>
                                    </div>
                                    <strong style="font-size: 0.85rem;">Sales AI Agent</strong>
                                </div>
                                Hello! I am your Sales AI Assistant. Ask me anything about target accounts, executive leads, seniority tiers, buying signals, or team roles.
                            </div>
                        </div>

                        <!-- Form Area -->
                        <div class="card-footer bg-white border-top p-3" style="border-bottom-left-radius: 16px; border-bottom-right-radius: 16px;">
                            <form id="pageChatbotForm" class="d-flex gap-2 mb-0">
                                <input type="text" id="pageChatbotInput" class="form-control" placeholder="Type a company, role, employee name, or team lead..." style="border-radius: 10px; padding: 0.75rem 1rem;" required autocomplete="off">
                                <button type="submit" class="btn btn-primary px-4 fw-semibold d-flex align-items-center gap-2" style="border-radius: 10px;">
                                    <i class="bi bi-send-fill"></i>
                                    <span>Send</span>
                                </button>
                            </form>
                            <div class="d-flex justify-content-between align-items-center mt-2 px-1 text-muted" style="font-size: 0.7rem;">
                                <span>Powered by <strong class="text-primary">SalesGPT-4o</strong></span>
                                <span>Model Status: <span class="text-success"><i class="bi bi-check-circle-fill"></i> Active</span></span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>`;
    },

    init() {
        ChatbotPage.renderHistory();

        $(document).off('submit', '#pageChatbotForm').on('submit', '#pageChatbotForm', async function(e) {
            e.preventDefault();
            const $input = $('#pageChatbotInput');
            const query = $input.val().trim();
            if (!query) return;

            $input.val('');
            ChatbotPage.addMessage(query, 'user');
            ChatbotPage.saveHistory(query);

            // Add typing indicator
            const $loader = $(`
                <div id="pageChatbotTyping" class="chat-message bot-message bg-white p-3 rounded-3 shadow-sm text-muted align-self-start d-flex align-items-center gap-2 mb-2" style="max-width: 80%; font-size: 0.88rem; border-bottom-left-radius: 0 !important; border-radius: 12px;">
                    <div class="spinner-border spinner-border-sm text-primary" role="status" style="width: 14px; height: 14px; border-width: 2px;"></div>
                    <span>AI is searching records...</span>
                </div>
            `);
            $('#pageChatbotMessages').append($loader);
            ChatbotPage.scrollToBottom();

            try {
                const res = await API.post('/chatbot/query', { query });
                $loader.remove();

                let text = res.response || 'No matches found.';
                text = text.replace(/### (.*)/g, '<h6 class="fw-bold mt-3 text-primary" style="font-size: 0.92rem;">$1</h6>')
                           .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                           .replace(/\*(.*?)\*/g, '<em>$1</em>')
                           .replace(/`(.*?)`/g, '<code class="bg-light px-1.5 py-0.5 rounded text-danger" style="font-size: 0.8rem;">$1</code>')
                           .replace(/- (.*)/g, '<div class="ps-2 py-1">&bull; $1</div>')
                           .replace(/\n/g, '<br>');

                ChatbotPage.addMessage(text, 'bot', res.results);
            } catch (err) {
                $loader.remove();
                ChatbotPage.addMessage('Failed to connect to Sales AI Assistant. Ensure the backend is active.', 'error');
            }
        });
    },

    load() {
        ChatbotPage.renderHistory();
        ChatbotPage.scrollToBottom();
    },

    sendPrompt(text) {
        $('#pageChatbotInput').val(text);
        $('#pageChatbotForm').submit();
    },

    clearChat() {
        $('#pageChatbotMessages').html(`
            <div class="chat-message bot-message bg-white p-3 rounded-3 shadow-sm text-dark align-self-start" style="max-width: 80%; font-size: 0.88rem; border-bottom-left-radius: 0 !important; border-radius: 12px; line-height: 1.5;">
                <div class="d-flex align-items-center gap-2 mb-2">
                    <div class="bg-primary text-white rounded-circle p-1 d-flex align-items-center justify-content-center" style="width: 24px; height: 24px;">
                        <i class="bi bi-robot" style="font-size: 0.8rem;"></i>
                    </div>
                    <strong style="font-size: 0.85rem;">Sales AI Agent</strong>
                </div>
                Hello! I am your Sales AI Assistant. Ask me anything about target accounts, executive leads, seniority tiers, buying signals, or team roles.
            </div>
        `);
    },

    saveHistory(query) {
        let history = JSON.parse(localStorage.getItem('sales_ai_chat_history') || '[]');
        if (!history.includes(query)) {
            history.unshift(query);
            if (history.length > 8) history.pop();
            localStorage.setItem('sales_ai_chat_history', JSON.stringify(history));
            ChatbotPage.renderHistory();
        }
    },

    renderHistory() {
        const history = JSON.parse(localStorage.getItem('sales_ai_chat_history') || '[]');
        let html = '';
        if (history.length === 0) {
            html = '<div class="text-center text-muted small py-3">No recent queries</div>';
        } else {
            history.forEach(q => {
                html += `
                <button class="btn btn-outline-secondary text-start text-truncate py-1.5 px-3 border border-light-subtle rounded-3 small text-dark d-flex align-items-center justify-content-between w-100" style="font-size: 0.78rem;" onclick="ChatbotPage.sendPrompt('${q.replace(/'/g, "\\'")}')">
                    <span class="text-truncate me-2"><i class="bi bi-search text-muted me-2" style="font-size: 0.72rem;"></i>${q}</span>
                    <i class="bi bi-chevron-right text-muted small" style="font-size: 0.65rem;"></i>
                </button>`;
            });
        }
        $('#chatHistoryList').html(html);
    },

    addMessage(text, sender, results) {
        const container = $('#pageChatbotMessages');
        if (sender === 'user') {
            container.append(`
                <div class="chat-message user-message bg-primary text-white p-3 rounded-3 align-self-end text-end mb-2 shadow-sm" style="max-width: 80%; font-size: 0.88rem; border-bottom-right-radius: 0 !important; border-radius: 12px; line-height: 1.5;">
                    <div class="fw-bold mb-1" style="font-size: 0.75rem; opacity: 0.85;">You</div>
                    ${text}
                </div>
            `);
        } else if (sender === 'bot') {
            let resultsHtml = '';
            if (results) {
                // Render structured cards if results exist
                if (results.contacts && results.contacts.length > 0) {
                    results.contacts.forEach(c => {
                        const first = c.full_name ? c.full_name.split(' ')[0] : '';
                        const last = c.full_name && c.full_name.split(' ').length > 1 ? c.full_name.split(' ')[1] : '';
                        const initials = ((first[0] || '') + (last[0] || '')).toUpperCase() || 'EX';
                        resultsHtml += `
                        <div class="card border-0 shadow-sm mb-2 p-3 bg-white hover-up w-100" style="border-left: 4px solid #0d6efd !important; border-radius: 12px; max-width: 100%; cursor: pointer;" onclick="App.navigate('leads')">
                            <div class="d-flex align-items-center gap-3">
                                <div class="rounded-circle bg-primary text-white p-2 d-flex align-items-center justify-content-center fw-bold flex-shrink-0" style="width: 38px; height: 38px; font-size: 0.85rem;">
                                    ${initials}
                                </div>
                                <div class="flex-grow-1 min-w-0">
                                    <h6 class="mb-0 fw-bold text-dark text-truncate" style="font-size: 0.85rem;">${c.full_name}</h6>
                                    <div class="text-muted small text-truncate" style="font-size: 0.75rem;">${c.title} @ ${c.account_name}</div>
                                    <div class="mt-1 d-flex flex-wrap gap-1">
                                        <span class="badge bg-primary-subtle text-primary" style="font-size: 0.6rem; padding: 0.15rem 0.3rem;">${c.seniority_tier || 'CXO'}</span>
                                        <span class="badge bg-success-subtle text-success" style="font-size: 0.6rem; padding: 0.15rem 0.3rem;">Lead Score: ${c.lead_score}</span>
                                    </div>
                                </div>
                                <div class="text-primary flex-shrink-0">
                                    <i class="bi bi-arrow-right-circle fs-5"></i>
                                </div>
                            </div>
                        </div>`;
                    });
                }

                if (results.accounts && results.accounts.length > 0) {
                    results.accounts.forEach(a => {
                        resultsHtml += `
                        <div class="card border-0 shadow-sm mb-2 p-3 bg-white hover-up w-100" style="border-left: 4px solid #198754 !important; border-radius: 12px; max-width: 100%; cursor: pointer;" onclick="App.navigate('accounts')">
                            <div class="d-flex align-items-center gap-3">
                                <div class="rounded-circle bg-success-subtle text-success p-2 d-flex align-items-center justify-content-center flex-shrink-0" style="width: 38px; height: 38px;">
                                    <i class="bi bi-building fs-5"></i>
                                </div>
                                <div class="flex-grow-1 min-w-0">
                                    <h6 class="mb-0 fw-bold text-dark text-truncate" style="font-size: 0.85rem;">${a.name}</h6>
                                    <div class="text-muted small text-truncate" style="font-size: 0.75rem;">${a.industry || 'Technology'} &bull; ${a.employee_count || '5,000+'} employees</div>
                                </div>
                                <div class="text-success flex-shrink-0">
                                    <i class="bi bi-arrow-right-circle fs-5"></i>
                                </div>
                            </div>
                        </div>`;
                    });
                }

                if (results.signals && results.signals.length > 0) {
                    results.signals.forEach(s => {
                        resultsHtml += `
                        <div class="card border-0 shadow-sm mb-2 p-3 bg-white hover-up w-100" style="border-left: 4px solid #dc3545 !important; border-radius: 12px; max-width: 100%; cursor: pointer;" onclick="App.navigate('signals')">
                            <div class="d-flex align-items-center gap-3">
                                <div class="rounded-circle bg-danger-subtle text-danger p-2 d-flex align-items-center justify-content-center flex-shrink-0" style="width: 38px; height: 38px;">
                                    <i class="bi bi-lightning-charge fs-5"></i>
                                </div>
                                <div class="flex-grow-1 min-w-0">
                                    <h6 class="mb-0 fw-bold text-dark text-truncate" style="font-size: 0.85rem;">${s.title}</h6>
                                    <div class="text-muted small text-truncate" style="font-size: 0.75rem;">Priority: <span class="text-danger fw-bold">${s.priority}</span></div>
                                </div>
                                <div class="text-danger flex-shrink-0">
                                    <i class="bi bi-arrow-right-circle fs-5"></i>
                                </div>
                            </div>
                        </div>`;
                    });
                }

                if (results.social && results.social.length > 0) {
                    results.social.forEach(s => {
                        let platformIcon = '<i class="bi bi-link-45deg"></i>';
                        let badgeColor = 'bg-secondary';
                        if (s.platform === 'LINKEDIN') {
                            platformIcon = '<i class="bi bi-linkedin"></i>';
                            badgeColor = 'bg-primary';
                        } else if (s.platform === 'TWITTER') {
                            platformIcon = '<i class="bi bi-twitter-x"></i>';
                            badgeColor = 'bg-dark';
                        }
                        
                        let sentimentBadge = 'bg-success-subtle text-success';
                        if (s.sentiment === 'NEGATIVE') {
                            sentimentBadge = 'bg-danger-subtle text-danger';
                        } else if (s.sentiment === 'NEUTRAL') {
                            sentimentBadge = 'bg-warning-subtle text-warning';
                        }

                        resultsHtml += `
                        <div class="card border-0 shadow-sm mb-2 p-3 bg-white hover-up w-100" style="border-left: 4px solid #0dcaf0 !important; border-radius: 12px; max-width: 100%; cursor: pointer;" onclick="App.navigate('social')">
                            <div class="d-flex align-items-start gap-3">
                                <div class="rounded-circle bg-info-subtle text-info p-2 d-flex align-items-center justify-content-center flex-shrink-0" style="width: 38px; height: 38px;">
                                    ${platformIcon}
                                </div>
                                <div class="flex-grow-1 min-w-0">
                                    <div class="d-flex justify-content-between align-items-center mb-1">
                                        <h6 class="mb-0 fw-bold text-dark text-truncate" style="font-size: 0.85rem;">${s.author_name}</h6>
                                        <span class="badge ${badgeColor} text-white" style="font-size: 0.6rem; padding: 0.15rem 0.3rem;">${s.platform}</span>
                                    </div>
                                    <div class="text-muted small mb-2 text-truncate" style="font-size: 0.75rem;">${s.author_title || ''}</div>
                                    <p class="text-dark mb-2 small text-truncate" style="font-size: 0.8rem; white-space: normal; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">${s.content}</p>
                                    <div class="d-flex flex-wrap gap-1">
                                        <span class="badge ${sentimentBadge}" style="font-size: 0.6rem; padding: 0.15rem 0.3rem;">${s.sentiment} Sentiment</span>
                                        ${s.engagement ? `<span class="badge bg-light text-dark border" style="font-size: 0.6rem; padding: 0.15rem 0.3rem;">${s.engagement}</span>` : ''}
                                    </div>
                                </div>
                                <div class="text-info flex-shrink-0 align-self-center">
                                    <i class="bi bi-arrow-right-circle fs-5"></i>
                                </div>
                            </div>
                        </div>`;
                    });
                }
            }

            container.append(`
                <div class="chat-message bot-message bg-white p-3 rounded-3 shadow-sm text-dark align-self-start mb-2" style="max-width: 80%; font-size: 0.88rem; border-bottom-left-radius: 0 !important; border-radius: 12px; line-height: 1.5;">
                    <div class="d-flex align-items-center gap-2 mb-2">
                        <div class="bg-primary text-white rounded-circle p-1 d-flex align-items-center justify-content-center" style="width: 24px; height: 24px;">
                            <i class="bi bi-robot" style="font-size: 0.8rem;"></i>
                        </div>
                        <strong style="font-size: 0.85rem;">Sales AI Agent</strong>
                    </div>
                    <div>${text}</div>
                    ${resultsHtml ? `<div class="mt-3 d-flex flex-column gap-2">${resultsHtml}</div>` : ''}
                </div>
            `);
        } else {
            container.append(`
                <div class="chat-message bot-message bg-danger-subtle text-danger p-3 rounded-3 shadow-sm align-self-start mb-2" style="max-width: 80%; font-size: 0.88rem; border-bottom-left-radius: 0 !important; border-radius: 12px;">
                    ${text}
                </div>
            `);
        }
        ChatbotPage.scrollToBottom();
    },

    scrollToBottom() {
        const container = document.getElementById('pageChatbotMessages');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }
};

window.ChatbotPage = ChatbotPage;
