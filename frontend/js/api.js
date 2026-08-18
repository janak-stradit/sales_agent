// API Helper Module
const API = {
    async get(endpoint, params = {}) {
        const url = new URL(`${CONFIG.API_BASE}${endpoint}`);
        Object.entries(params).forEach(([k, v]) => {
            if (v !== null && v !== undefined && v !== '') url.searchParams.append(k, v);
        });
        try {
            const res = await $.ajax({ url: url.toString(), method: 'GET', dataType: 'json' });
            return res;
        } catch (err) {
            console.error(`GET ${endpoint} failed:`, err);
            App.toast('API request failed', 'error');
            throw err;
        }
    },

    async post(endpoint, data = {}) {
        try {
            const res = await $.ajax({
                url: `${CONFIG.API_BASE}${endpoint}`,
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(data),
                dataType: 'json'
            });
            return res;
        } catch (err) {
            console.error(`POST ${endpoint} failed:`, err);
            App.toast('API request failed', 'error');
            throw err;
        }
    },

    async patch(endpoint, data = {}) {
        try {
            const res = await $.ajax({
                url: `${CONFIG.API_BASE}${endpoint}`,
                method: 'PATCH',
                contentType: 'application/json',
                data: JSON.stringify(data),
                dataType: 'json'
            });
            return res;
        } catch (err) {
            console.error(`PATCH ${endpoint} failed:`, err);
            App.toast('API request failed', 'error');
            throw err;
        }
    },

    async put(endpoint, data = {}) {
        try {
            const res = await $.ajax({
                url: `${CONFIG.API_BASE}${endpoint}`,
                method: 'PUT',
                contentType: 'application/json',
                data: JSON.stringify(data),
                dataType: 'json'
            });
            return res;
        } catch (err) {
            console.error(`PUT ${endpoint} failed:`, err);
            App.toast('API request failed', 'error');
            throw err;
        }
    },

    async delete(endpoint) {
        try {
            const res = await $.ajax({
                url: `${CONFIG.API_BASE}${endpoint}`,
                method: 'DELETE',
                dataType: 'json'
            });
            return res;
        } catch (err) {
            console.error(`DELETE ${endpoint} failed:`, err);
            App.toast('API request failed', 'error');
            throw err;
        }
    }
};
