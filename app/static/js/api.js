/**
 * API Wrapper for Backend Requests
 */
const API = {
    async request(url, options = {}) {
        const defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
        options.headers = { ...defaultHeaders, ...options.headers };

        try {
            const response = await fetch(url, options);
            const data = await response.json().catch(() => ({}));
            
            if (!response.ok) {
                const message = data.detail || 'Bir hata oluştu.';
                throw new Error(message);
            }
            return data;
        } catch (error) {
            console.error(`API Error (${url}):`, error);
            App.showToast(error.message, 'error');
            throw error;
        }
    },

    // System
    getSystemInfo() {
        return this.request('/api/system-info');
    },

    // Dashboard
    getDashboardSummary() {
        return this.request('/api/dashboard/summary');
    },
    getDashboardCharts() {
        return this.request('/api/dashboard/charts');
    },

    // Machines
    getMachines(search = '', status = '') {
        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (status) params.append('status', status);
        return this.request(`/api/machines?${params.toString()}`);
    },
    getMachine(id) {
        return this.request(`/api/machines/${id}`);
    },
    createMachine(data) {
        return this.request('/api/machines', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    updateMachine(id, data) {
        return this.request(`/api/machines/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    deleteMachine(id) {
        return this.request(`/api/machines/${id}`, {
            method: 'DELETE'
        });
    },

    // Inventory
    getInventory(search = '', category = '', onlyCritical = false) {
        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (category) params.append('category', category);
        if (onlyCritical) params.append('only_critical', 'true');
        return this.request(`/api/inventory?${params.toString()}`);
    },
    getPart(id) {
        return this.request(`/api/inventory/${id}`);
    },
    createPart(data) {
        return this.request('/api/inventory', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    updatePart(id, data) {
        return this.request(`/api/inventory/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    adjustStock(id, adjustment, reason = '') {
        return this.request(`/api/inventory/${id}/adjust-stock`, {
            method: 'POST',
            body: JSON.stringify({ adjustment, reason })
        });
    },
    deletePart(id) {
        return this.request(`/api/inventory/${id}`, {
            method: 'DELETE'
        });
    },

    // Maintenance
    getMaintenanceLogs(params = {}) {
        const searchParams = new URLSearchParams();
        if (params.machine_id) searchParams.append('machine_id', params.machine_id);
        if (params.part_id) searchParams.append('part_id', params.part_id);
        if (params.search) searchParams.append('search', params.search);
        if (params.limit) searchParams.append('limit', params.limit);
        return this.request(`/api/maintenance?${searchParams.toString()}`);
    },
    createMaintenanceLog(data) {
        return this.request('/api/maintenance', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    deleteMaintenanceLog(id, restoreStock = false) {
        return this.request(`/api/maintenance/${id}?restore_stock=${restoreStock}`, {
            method: 'DELETE'
        });
    }
};
