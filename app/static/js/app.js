/**
 * Main Application Controller
 */
const App = {
    currentTab: 'dashboard',

    init() {
        this.setupNavigation();
        this.fetchSystemInfo();
        
        // Initial Tab Load
        this.switchTab('dashboard');

        // Setup Real-time Search debounce
        this.setupSearchListeners();
    },

    setupNavigation() {
        const navButtons = document.querySelectorAll('[data-tab-target]');
        navButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const target = btn.getAttribute('data-tab-target');
                this.switchTab(target);
            });
        });
    },

    switchTab(tabId) {
        this.currentTab = tabId;

        // Update nav buttons styling
        document.querySelectorAll('[data-tab-target]').forEach(btn => {
            const isCurrent = btn.getAttribute('data-tab-target') === tabId;
            if (isCurrent) {
                btn.className = 'flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-semibold bg-slate-900 text-white shadow-sm transition';
            } else {
                btn.className = 'flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition';
            }
        });

        // Toggle Tab Panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.add('hidden');
        });

        const activePanel = document.getElementById(`tab-${tabId}`);
        if (activePanel) {
            activePanel.classList.remove('hidden');
        }

        // Trigger Data Load
        if (tabId === 'dashboard') {
            Dashboard.load();
        } else if (tabId === 'machines') {
            Machines.load();
        } else if (tabId === 'inventory') {
            Inventory.load();
        } else if (tabId === 'maintenance') {
            Maintenance.load();
        }

        lucide.createIcons();
    },

    async fetchSystemInfo() {
        try {
            const info = await API.getSystemInfo();
            const lanBadge = document.getElementById('lan-ip-badge');
            const lanLink = document.getElementById('lan-ip-link');
            if (lanBadge && lanLink) {
                lanLink.textContent = info.lan_url;
                lanLink.href = info.lan_url;
                lanBadge.classList.remove('hidden');
            }
        } catch (e) {}
    },

    setupSearchListeners() {
        // Machines Search
        const mSearch = document.getElementById('machine-search');
        if (mSearch) {
            mSearch.addEventListener('input', () => debounce(() => Machines.load(), 300)());
        }

        // Inventory Search
        const iSearch = document.getElementById('inventory-search');
        if (iSearch) {
            iSearch.addEventListener('input', () => debounce(() => Inventory.load(), 300)());
        }

        // Maintenance Logs Search
        const lSearch = document.getElementById('log-search');
        if (lSearch) {
            lSearch.addEventListener('input', () => debounce(() => Maintenance.load(), 300)());
        }
    },

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            lucide.createIcons();
        }
    },

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
    },

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        const isError = type === 'error';
        const isSuccess = type === 'success';

        const bg = isError ? 'bg-rose-600 text-white' : (isSuccess ? 'bg-slate-900 text-white' : 'bg-blue-600 text-white');
        const icon = isError ? 'alert-circle' : (isSuccess ? 'check-circle' : 'info');

        toast.className = `${bg} px-4 py-3 rounded-xl shadow-xl flex items-center space-x-2 text-sm font-medium transition-all duration-300 transform translate-y-2 opacity-0`;
        toast.innerHTML = `
            <i data-lucide="${icon}" class="w-5 h-5 shrink-0"></i>
            <span>${message}</span>
        `;

        container.appendChild(toast);
        lucide.createIcons();

        // Animate In
        setTimeout(() => {
            toast.classList.remove('translate-y-2', 'opacity-0');
        }, 10);

        // Auto remove
        setTimeout(() => {
            toast.classList.add('opacity-0', 'translate-y-2');
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
};

// Utility debounce
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
