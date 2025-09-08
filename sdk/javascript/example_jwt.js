/**
 * C2M API JavaScript SDK Example with JWT Authentication
 */

const C2mApi = require('c2m_api');
const axios = require('axios');

class C2MClient {
    constructor(clientId, clientSecret, baseUrl = 'https://api.c2m.com/v2') {
        this.clientId = clientId;
        this.clientSecret = clientSecret;
        this.baseUrl = baseUrl;
        this.authUrl = baseUrl;
        this.longToken = null;
        this.shortToken = null;
        this.tokenExpiry = null;
    }
    
    async getLongToken() {
        const response = await axios.post(`${this.authUrl}/auth/tokens/long`, {
            grant_type: 'client_credentials',
            client_id: this.clientId,
            client_secret: this.clientSecret,
            scopes: ['jobs:submit', 'jobs:read', 'templates:read'],
            ttl_seconds: 2592000 // 30 days
        });
        
        this.longToken = response.data.access_token;
        console.log(`Long-term token obtained: ${response.data.token_id}`);
        return this.longToken;
    }
    
    async getShortToken() {
        if (!this.longToken) {
            await this.getLongToken();
        }
        
        const response = await axios.post(
            `${this.authUrl}/auth/tokens/short`,
            { scopes: ['jobs:submit'] },
            { headers: { Authorization: `Bearer ${this.longToken}` } }
        );
        
        this.shortToken = response.data.access_token;
        this.tokenExpiry = new Date(response.data.expires_at);
        console.log(`Short-term token obtained: ${response.data.token_id}`);
        return this.shortToken;
    }
    
    async ensureAuthenticated() {
        const now = new Date();
        const buffer = new Date(now.getTime() + 60000); // 1 minute buffer
        
        if (!this.shortToken || buffer >= this.tokenExpiry) {
            await this.getShortToken();
        }
        
        return this.shortToken;
    }
    
    async configureClient() {
        const token = await this.ensureAuthenticated();
        
        const defaultClient = C2mApi.ApiClient.instance;
        const bearerAuth = defaultClient.authentications['bearerAuth'];
        bearerAuth.accessToken = token;
        defaultClient.basePath = this.baseUrl;
        
        return defaultClient;
    }
    
    async submitJob(jobParams) {
        await this.configureClient();
        const jobsApi = new C2mApi.DefaultApi();
        
        try {
            return await jobsApi.submitSingleDocWithTemplateParams(jobParams);
        } catch (error) {
            if (error.status === 401 || error.status === 403) {
                // Token expired, refresh and retry
                this.shortToken = null;
                await this.configureClient();
                return await jobsApi.submitSingleDocWithTemplateParams(jobParams);
            }
            throw error;
        }
    }
}

// Usage example
async function main() {
    const client = new C2MClient(
        'your-client-id',
        'your-client-secret'
    );
    
    const jobParams = {
        templateId: 'standard-letter',
        documentUrl: 'https://example.com/document.pdf',
        recipients: [{
            name: 'John Doe',
            address: {
                line1: '123 Main St',
                city: 'New York',
                state: 'NY',
                zip: '10001'
            }
        }]
    };
    
    try {
        const result = await client.submitJob(jobParams);
        console.log('Job submitted:', result);
    } catch (error) {
        console.error('Error:', error);
    }
}

// Run if called directly
if (require.main === module) {
    main();
}

module.exports = C2MClient;
