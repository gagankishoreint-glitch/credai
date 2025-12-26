// API Configuration and Utilities

const API_BASE_URL = 'http://localhost:8000';

class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    // Applications endpoints
    async createApplication(applicationData) {
        return this.request('/api/applications/', {
            method: 'POST',
            body: JSON.stringify(applicationData)
        });
    }

    async getApplications(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/api/applications/${queryString ? '?' + queryString : ''}`);
    }

    async getApplication(id) {
        return this.request(`/api/applications/${id}`);
    }

    async evaluateApplication(id) {
        return this.request(`/api/applications/${id}/evaluate`, {
            method: 'POST'
        });
    }

    // Evaluations endpoints
    async getEvaluation(id) {
        return this.request(`/api/evaluations/${id}`);
    }

    async getDetailedEvaluation(id) {
        return this.request(`/api/evaluations/${id}/detailed`);
    }

    async getEvaluationByApplication(applicationId) {
        return this.request(`/api/evaluations/application/${applicationId}`);
    }

    // Health check
    async healthCheck() {
        return this.request('/health');
    }
}

// Global API client instance
const api = new APIClient(API_BASE_URL);
