// API Helper Module
const API = {
    _url(endpoint) {
        let ep = endpoint || '';
        if (!ep.startsWith('/')) ep = '/' + ep;
        const base = (typeof CONFIG !== 'undefined' && CONFIG && CONFIG.API_BASE) ? CONFIG.API_BASE : '/api/v1';
        return `${base}${ep}`;
    },

    async get(endpoint, params = {}) {
        let url = this._url(endpoint);
        const queryParams = new URLSearchParams();
        Object.entries(params).forEach(([k, v]) => {
            if (v !== null && v !== undefined && v !== '') queryParams.append(k, v);
        });
        const qs = queryParams.toString();
        if (qs) url += (url.includes('?') ? '&' : '?') + qs;

        try {
            const res = await $.ajax({ url: url, method: 'GET', dataType: 'json', timeout: 15000 });
            return res;
        } catch (err) {
            console.error(`GET ${endpoint} failed:`, err);
            App.toast('API request failed', 'error');
            throw err;
        }
    },

    async post(endpoint, data = {}) {
        const url = this._url(endpoint);
        try {
            const res = await $.ajax({
                url: url,
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(data),
                dataType: 'json',
                timeout: 15000
            });
            return res;
        } catch (err) {
            console.error(`POST ${endpoint} failed:`, err);
            App.toast('API request failed', 'error');
            throw err;
        }
    },

    async patch(endpoint, data = {}) {
        const url = this._url(endpoint);
        try {
            const res = await $.ajax({
                url: url,
                method: 'PATCH',
                contentType: 'application/json',
                data: JSON.stringify(data),
                dataType: 'json',
                timeout: 15000
            });
            return res;
        } catch (err) {
            console.error(`PATCH ${endpoint} failed:`, err);
            App.toast('API request failed', 'error');
            throw err;
        }
    },

    async put(endpoint, data = {}) {
        const url = this._url(endpoint);
        try {
            const res = await $.ajax({
                url: url,
                method: 'PUT',
                contentType: 'application/json',
                data: JSON.stringify(data),
                dataType: 'json',
                timeout: 15000
            });
            return res;
        } catch (err) {
            console.error(`PUT ${endpoint} failed:`, err);
            App.toast('API request failed', 'error');
            throw err;
        }
    },

    async delete(endpoint) {
        const url = this._url(endpoint);
        try {
            const res = await $.ajax({
                url: url,
                method: 'DELETE',
                dataType: 'json',
                timeout: 15000
            });
            return res;
        } catch (err) {
            console.error(`DELETE ${endpoint} failed:`, err);
            App.toast('API request failed', 'error');
            throw err;
        }
    }
};
