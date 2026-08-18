// Hierarchy Page - Bootstrap 5 Version
const HierarchyPage = {
    render() {
        return `
        <div class="fade-in">
            <div class="mb-4">
                <h3 class="h4 fw-bold text-dark mb-1">Organizational Hierarchy</h3>
                <p class="text-muted small mb-0">Reporting structures and span of control</p>
            </div>

            <!-- Account Selector -->
            <div class="card border-0 shadow-sm bg-white mb-4">
                <div class="card-body d-flex flex-wrap gap-3 align-items-center py-3">
                    <label for="hierarchyAccount" class="form-label mb-0 fw-semibold text-muted small">Select Target Account:</label>
                    <select id="hierarchyAccount" class="form-select form-select-sm w-auto" style="min-width: 250px;">
                        <option value="">Select an account...</option>
                    </select>
                    <button onclick="HierarchyPage.loadTree()" class="btn btn-sm btn-primary px-3">
                        <i class="bi bi-diagram-3"></i> Load Hierarchy
                    </button>
                </div>
            </div>

            <!-- Span Metrics -->
            <div class="row g-3 mb-4" id="spanMetrics" style="display:none">
                <div class="col-6 col-md-3">
                    <div class="card border-0 shadow-sm bg-white p-3 text-center mb-0">
                        <h4 class="fw-bold text-primary mb-1" id="spanTotal">0</h4>
                        <span class="text-muted small" style="font-size: 0.75rem;">Total People</span>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="card border-0 shadow-sm bg-white p-3 text-center mb-0">
                        <h4 class="fw-bold text-purple mb-1" id="spanDepth" style="color: #6f42c1;">0</h4>
                        <span class="text-muted small" style="font-size: 0.75rem;">Max Depth</span>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="card border-0 shadow-sm bg-white p-3 text-center mb-0">
                        <h4 class="fw-bold text-success mb-1" id="spanAvg">0</h4>
                        <span class="text-muted small" style="font-size: 0.75rem;">Avg Span</span>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="card border-0 shadow-sm bg-white p-3 text-center mb-0">
                        <h4 class="fw-bold text-warning mb-1" id="spanDMs">0</h4>
                        <span class="text-muted small" style="font-size: 0.75rem;">Decision Makers</span>
                    </div>
                </div>
            </div>

            <!-- Tree View -->
            <div class="card border-0 shadow-sm bg-white mb-0" id="hierarchyTreeContainer" style="display:none">
                <div class="card-header bg-white border-0 py-3">
                    <h5 class="card-title h6 fw-bold mb-0"><i class="bi bi-diagram-3-fill text-primary"></i> Organization Tree</h5>
                </div>
                <div class="card-body pt-0">
                    <div id="hierarchyTree" class="ps-2"></div>
                </div>
            </div>
        </div>`;
    },

    async load() {
        // Load accounts for selector
        try {
            const accounts = await API.get('/accounts', { limit: 100 });
            let opts = '<option value="">Select an account...</option>';
            (accounts || []).forEach(a => {
                opts += `<option value="${a.id}">${a.name}</option>`;
            });
            $('#hierarchyAccount').html(opts);
        } catch (e) { /* handled */ }
    },

    async loadTree() {
        const accountId = $('#hierarchyAccount').val();
        if (!accountId) { App.toast('Please select an account'); return; }

        try {
            // Load span metrics
            const spans = await API.get(`/hierarchy/spans/${accountId}`);
            $('#spanTotal').text(spans.total_nodes || 0);
            $('#spanDepth').text(spans.max_depth || 0);
            $('#spanAvg').text(spans.avg_span_of_control ? spans.avg_span_of_control.toFixed(1) : 0);
            $('#spanDMs').text(spans.decision_makers_count || 0);
            $('#spanMetrics').show();

            // Load tree
            const tree = await API.get(`/hierarchy/tree/${accountId}`);
            if (!tree || tree.length === 0) {
                $('#hierarchyTree').html('<p class="text-muted text-center py-4 small">No hierarchy data available</p>');
            } else {
                $('#hierarchyTree').html(HierarchyPage.renderTree(tree));
            }
            $('#hierarchyTreeContainer').show();
        } catch (e) {
            $('#hierarchyTree').html('<p class="text-danger small py-3 text-center">Failed to load hierarchy</p>');
            $('#hierarchyTreeContainer').show();
        }
    },

    renderTree(nodes, depth = 0) {
        let html = '';
        nodes.forEach(node => {
            const indent = depth * 24;
            const hasChildren = node.children && node.children.length > 0;
            html += `
            <div class="py-2 d-flex align-items-center gap-2 border-bottom border-light" style="padding-left:${indent}px">
                ${hasChildren ? '<i class="bi bi-chevron-down text-muted" style="font-size: 0.75rem;"></i>' : '<span style="width: 12px; display:inline-block"></span>'}
                <div class="rounded-circle bg-primary-subtle text-primary fw-bold d-flex align-items-center justify-content-center" style="width: 30px; height: 30px; font-size: 0.8rem;">
                    ${(node.name || '?')[0]}
                </div>
                <div>
                    <strong class="text-dark small d-block">${node.name || '—'}</strong>
                    <span class="text-muted" style="font-size: 0.75rem;">${node.title || ''} ${node.decision_authority ? '&bull; ' + node.decision_authority : ''}</span>
                </div>
            </div>`;
            if (hasChildren) {
                html += HierarchyPage.renderTree(node.children, depth + 1);
            }
        });
        return html;
    }
};
