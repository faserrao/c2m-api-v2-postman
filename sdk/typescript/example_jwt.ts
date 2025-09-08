/**
 * C2M API TypeScript SDK Example with JWT Authentication
 */

import { Configuration, DefaultApi } from 'c2m-api-ts';
import axios from 'axios';

interface TokenResponse {
    access_token: string;
    token_id: string;
    expires_at: string;
}

class C2MClient {
    private clientId: string;
    private clientSecret: string;
    private baseUrl: string;
    private authUrl: string;
    private longToken: string | null = null;
    private shortToken: string | null = null;
    private tokenExpiry: Date | null = null;
    
    constructor(clientId: string, clientSecret: string, baseUrl = 'https://api.c2m.com/v2') {
        this.clientId = clientId;
        this.clientSecret = clientSecret;
        this.baseUrl = baseUrl;
        this.authUrl = baseUrl;
    }
    
    private async getLongToken(): Promise<string> {
        const response = await axios.post<TokenResponse>(`${this.authUrl}/auth/tokens/long`, {
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
    
    private async getShortToken(): Promise<string> {
        if (!this.longToken) {
            await this.getLongToken();
        }
        
        const response = await axios.post<TokenResponse>(
            `${this.authUrl}/auth/tokens/short`,
            { scopes: ['jobs:submit'] },
            { headers: { Authorization: `Bearer ${this.longToken}` } }
        );
        
        this.shortToken = response.data.access_token;
        this.tokenExpiry = new Date(response.data.expires_at);
        console.log(`Short-term token obtained: ${response.data.token_id}`);
        return this.shortToken;
    }
    
    private async ensureAuthenticated(): Promise<string> {
        const now = new Date();
        const buffer = new Date(now.getTime() + 60000); // 1 minute buffer
        
        if (!this.shortToken || !this.tokenExpiry || buffer >= this.tokenExpiry) {
            await this.getShortToken();
        }
        
        return this.shortToken!;
    }
    
    private async getConfiguration(): Promise<Configuration> {
        const token = await this.ensureAuthenticated();
        
        return new Configuration({
            basePath: this.baseUrl,
            accessToken: token
        });
    }
    
    public async submitJob(jobParams: any): Promise<any> {
        const config = await this.getConfiguration();
        const api = new DefaultApi(config);
        
        try {
            return await api.submitSingleDocWithTemplateParams(jobParams);
        } catch (error: any) {
            if (error.response?.status === 401 || error.response?.status === 403) {
                // Token expired, refresh and retry
                this.shortToken = null;
                const newConfig = await this.getConfiguration();
                const newApi = new DefaultApi(newConfig);
                return await newApi.submitSingleDocWithTemplateParams(jobParams);
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
    main().catch(console.error);
}

export default C2MClient;
