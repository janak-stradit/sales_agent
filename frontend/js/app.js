// Main Application Controller
const App = {
    currentPage: 'dashboard',

    pages: {
        dashboard: { title: 'Executive Dashboard', module: DashboardPage },
        chatbot: { title: 'AI Assistant Hub', module: ChatbotPage },
        accounts: { title: 'Target Accounts', module: AccountsPage },
        leads: { title: 'Executive Leads', module: LeadsPage },
        hierarchy: { title: 'Organizational Hierarchy', module: HierarchyPage },
        social: { title: 'Social Intelligence', module: SocialPage },
        signals: { title: 'Sales Signals', module: SignalsPage },
        pipeline: { title: 'Pipeline Engine', module: PipelinePage },
        logs: { title: 'Execution Logs', module: LogsPage },
    },

    init() {
        // Sidebar navigation
        $(document).on('click', '.sidebar-link', function(e) {
            e.preventDefault();
            const page = $(this).data('page');
            if (page) {
                App.navigate(page);
                // Hide sidebar on mobile after clicking
                $('#sidebar').removeClass('show');
            }
        });

        // Sidebar toggle (mobile)
        $('#sidebarToggle').on('click', () => {
            $('#sidebar').toggleClass('show');
        });

        // Refresh button
        $('#refreshBtn').on('click', () => {
            App.loadCurrentPage();
        });

        // Init page & form handlers
        if (AccountsPage.init) AccountsPage.init();
        if (ChatbotPage.init) ChatbotPage.init();

        // Load initial page
        App.navigate('dashboard');
    },

    navigate(page, param) {
        if (!App.pages[page]) return;

        App.currentPage = page;

        // Update sidebar active state
        $('.sidebar-link').removeClass('active');
        $(`.sidebar-link[data-page="${page}"]`).addClass('active');

        // Update page title
        $('#pageTitle').text(App.pages[page].title);

        // Render page HTML
        const module = App.pages[page].module;
        $('#mainContent').html(module.render());

        // Load page data
        App.loadCurrentPage(param);

        // Update timestamp
        $('#lastUpdated').text('Updated ' + new Date().toLocaleTimeString());
    },

    loadCurrentPage(param) {
        const module = App.pages[App.currentPage].module;
        if (module.load) module.load(param);
    },

    toast(message, type = 'success') {
        const $toast = $('#toast');
        $toast.text(message)
            .removeClass('d-none bg-danger bg-dark')
            .addClass(type === 'error' ? 'bg-danger' : 'bg-dark');
        $toast.removeClass('d-none');
        setTimeout(() => $toast.addClass('d-none'), 3000);
    }
};

// Boot
$(document).ready(() => {
    App.init();
});
