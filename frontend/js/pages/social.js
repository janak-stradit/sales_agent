// Social Intelligence Page - Bootstrap 5 Version
const SocialPage = {
    render() {
        return `
        <div class="fade-in">
            <div class="mb-4">
                <h3 class="h4 fw-bold text-dark mb-1">Social Intelligence</h3>
                <p class="text-muted small mb-0">Executive activity, sentiment, and engagement tracking</p>
            </div>

            <!-- Analytics Summary -->
            <div class="row g-3 mb-4" id="socialAnalytics">
                <div class="col-12 col-md-4">
                    <div class="card border-0 shadow-sm bg-white p-3 mb-0 h-100 d-flex flex-row justify-content-between align-items-center">
                        <div>
                            <span class="text-muted text-uppercase small fw-semibold d-block" style="font-size: 0.7rem;">Total Posts Tracked</span>
                            <strong class="h4 fw-bold text-dark mb-0 mt-1 d-block" id="socialTotal">—</strong>
                        </div>
                        <div class="rounded bg-primary-subtle text-primary p-2 d-flex align-items-center justify-content-center" style="width: 42px; height: 42px;">
                            <i class="bi bi-chat-left-quote fs-5"></i>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-md-4">
                    <div class="card border-0 shadow-sm bg-white p-3 mb-0 h-100 d-flex flex-row justify-content-between align-items-center">
                        <div>
                            <span class="text-muted text-uppercase small fw-semibold d-block" style="font-size: 0.7rem;">Avg Sentiment</span>
                            <strong class="h4 fw-bold text-dark mb-0 mt-1 d-block" id="socialSentiment">—</strong>
                        </div>
                        <div class="rounded bg-success-subtle text-success p-2 d-flex align-items-center justify-content-center" style="width: 42px; height: 42px;">
                            <i class="bi bi-emoji-smile fs-5"></i>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-md-4">
                    <div class="card border-0 shadow-sm bg-white p-3 mb-0 h-100">
                        <span class="text-muted text-uppercase small fw-semibold d-block mb-2" style="font-size: 0.7rem;">Trending Topics</span>
                        <div class="d-flex flex-wrap gap-1" id="socialTopics"></div>
                    </div>
                </div>
            </div>

            <!-- Filters -->
            <div class="card border-0 shadow-sm bg-white mb-4">
                <div class="card-body d-flex flex-wrap gap-3 align-items-center py-3">
                    <select id="socialPlatform" class="form-select form-select-sm w-auto">
                        <option value="">All Platforms</option>
                        <option value="LINKEDIN">LinkedIn</option>
                        <option value="TWITTER">Twitter</option>
                        <option value="NEWS">News</option>
                    </select>
                    <select id="socialSentimentFilter" class="form-select form-select-sm w-auto">
                        <option value="">All Sentiment</option>
                        <option value="POSITIVE">Positive</option>
                        <option value="NEUTRAL">Neutral</option>
                        <option value="NEGATIVE">Negative</option>
                    </select>
                    <select id="socialEntityType" class="form-select form-select-sm w-auto">
                        <option value="">All Types</option>
                        <option value="CORPORATE">Corporate</option>
                        <option value="EXECUTIVE">Executive</option>
                    </select>
                    <input type="text" id="socialSearch" placeholder="Search..." class="form-control form-control-sm w-auto" style="max-width: 180px;">
                    <button onclick="SocialPage.loadFeed()" class="btn btn-sm btn-outline-secondary px-3">Filter</button>
                </div>
            </div>

            <!-- Social Feed -->
            <div class="d-flex flex-column gap-3" id="socialFeed"></div>
        </div>`;
    },

    async load() {
        await Promise.all([SocialPage.loadAnalytics(), SocialPage.loadFeed()]);
    },

    async loadAnalytics() {
        try {
            const data = await API.get('/social/analytics');
            $('#socialTotal').text(data.total_posts || 0);
            $('#socialSentiment').text(data.avg_sentiment || '—');
            const topics = (data.trending_topics || []).slice(0, 6);
            let topicsHtml = '';
            topics.forEach(t => {
                topicsHtml += `<span class="badge bg-primary-subtle text-primary border-0 px-2 py-1">${t}</span>`;
            });
            $('#socialTopics').html(topicsHtml || '<span class="text-muted small">No topics</span>');
        } catch (e) { /* handled */ }
    },

    async loadFeed() {
        const params = {
            platform: $('#socialPlatform').val() || undefined,
            sentiment: $('#socialSentimentFilter').val() || undefined,
            entity_type: $('#socialEntityType').val() || undefined,
            search: $('#socialSearch').val() || undefined,
            limit: 30
        };
        try {
            const posts = await API.get('/social/feed', params);
            let html = '';
            if (!posts || posts.length === 0) {
                html = '<div class="text-center py-5 text-muted small"><i class="bi bi-chat-left-text me-1"></i> No social posts found</div>';
            } else {
                posts.forEach(p => {
                    const sentColor = p.sentiment === 'POSITIVE' ? 'bg-success-subtle text-success' : p.sentiment === 'NEGATIVE' ? 'bg-danger-subtle text-danger' : 'bg-secondary-subtle text-secondary';
                    const platIcon = p.platform === 'LINKEDIN' ? '<i class="bi bi-linkedin text-primary"></i>' : p.platform === 'TWITTER' ? '<i class="bi bi-twitter text-info"></i>' : '<i class="bi bi-newspaper text-muted"></i>';
                    html += `
                    <div class="card border-0 shadow-sm bg-white p-4 mb-0">
                        <div class="d-flex align-items-center justify-content-between mb-3">
                            <div class="d-flex align-items-center gap-2">
                                <span class="fs-5">${platIcon}</span>
                                <div>
                                    <strong class="text-dark small d-block">${p.author || 'Unknown'}</strong>
                                    <span class="text-muted" style="font-size: 0.7rem;">${p.platform || ''} &bull; ${p.entity_type || ''}</span>
                                </div>
                            </div>
                            <span class="badge ${sentColor} text-uppercase" style="font-size: 0.65rem;">${p.sentiment || '—'}</span>
                        </div>
                        <p class="text-dark small mb-3 lh-base" style="font-size: 0.9rem;">${p.content || ''}</p>
                        ${p.topic_tags && p.topic_tags.length ? `
                            <div class="d-flex flex-wrap gap-1">
                                ${p.topic_tags.map(t => `<span class="badge bg-light text-secondary border px-2 py-1" style="font-size: 0.65rem;">#${t}</span>`).join('')}
                            </div>
                        ` : ''}
                    </div>`;
                });
            }
            $('#socialFeed').html(html);
        } catch (e) {
            $('#socialFeed').html('<div class="text-center py-4 text-danger small">Failed to load feed</div>');
        }
    }
};
