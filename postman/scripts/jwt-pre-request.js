// Postman Pre-request Script for JWT Authentication
// This script automatically manages token refresh for C2M API requests

// Configuration - Set these in your Postman environment
const config = {
    // Use authUrl for authentication endpoints, fallback to baseUrl for compatibility
    authUrl: pm.environment.get('authUrl') || pm.environment.get('baseUrl') || 'http://localhost:4010',
    baseUrl: pm.environment.get('baseUrl') || 'http://localhost:4010',
    clientId: pm.environment.get('clientId'),
    clientSecret: pm.environment.get('clientSecret'),
    longTokenVar: 'longTermToken',
    shortTokenVar: 'shortTermToken',
    tokenExpiryVar: 'tokenExpiry',
    tokenIdVar: 'currentTokenId'
};

// Helper function to check if token is expired
function isTokenExpired(expiryTime) {
    if (!expiryTime) return true;
    const now = new Date().getTime();
    const expiry = new Date(expiryTime).getTime();
    const bufferTime = 60 * 1000; // 1 minute buffer
    return (expiry - now) <= bufferTime;
}

// Helper function to get long-term token
async function getLongTermToken() {
    console.log('Obtaining new long-term token...');
    
    const request = {
        url: `${config.authUrl}/auth/tokens/long`,
        method: 'POST',
        header: {
            'Content-Type': 'application/json',
            'X-Client-Id': config.clientId
        },
        body: {
            mode: 'raw',
            raw: JSON.stringify({
                grant_type: 'client_credentials',
                client_id: config.clientId,
                client_secret: config.clientSecret,
                scopes: ['jobs:submit', 'templates:read', 'tokens:revoke'],
                ttl_seconds: 2592000 // 30 days
            })
        }
    };
    
    return new Promise((resolve, reject) => {
        pm.sendRequest(request, (err, response) => {
            if (err) {
                console.error('Failed to get long-term token:', err);
                reject(err);
                return;
            }
            
            if (response.code === 200 || response.code === 201) {
                const data = response.json();
                pm.environment.set(config.longTokenVar, data.access_token);
                pm.environment.set('longTokenId', data.token_id);
                pm.environment.set('longTokenExpiry', data.expires_at);
                console.log(`Long-term token obtained: ${data.token_id}`);
                resolve(data.access_token);
            } else {
                console.error('Failed to get long-term token:', response.text());
                reject(new Error(`HTTP ${response.code}: ${response.text()}`));
            }
        });
    });
}

// Helper function to get short-term token
async function getShortTermToken(longTermToken) {
    console.log('Exchanging for short-term token...');
    
    const request = {
        url: `${config.authUrl}/auth/tokens/short`,
        method: 'POST',
        header: {
            'Authorization': `Bearer ${longTermToken}`,
            'Content-Type': 'application/json'
        },
        body: {
            mode: 'raw',
            raw: JSON.stringify({
                scopes: ['jobs:submit'] // Narrow scope for actual API calls
            })
        }
    };
    
    return new Promise((resolve, reject) => {
        pm.sendRequest(request, (err, response) => {
            if (err) {
                console.error('Failed to get short-term token:', err);
                reject(err);
                return;
            }
            
            if (response.code === 200 || response.code === 201) {
                const data = response.json();
                pm.environment.set(config.shortTokenVar, data.access_token);
                pm.environment.set(config.tokenExpiryVar, data.expires_at);
                pm.environment.set(config.tokenIdVar, data.token_id);
                console.log(`Short-term token obtained: ${data.token_id}, expires: ${data.expires_at}`);
                resolve(data.access_token);
            } else {
                console.error('Failed to get short-term token:', response.text());
                reject(new Error(`HTTP ${response.code}: ${response.text()}`));
            }
        });
    });
}

// Main authentication flow
async function authenticate() {
    try {
        // Skip auth for token endpoints
        const currentPath = pm.request.url.getPath();
        if (currentPath.includes('/auth/tokens/')) {
            console.log('Skipping auth for token endpoint');
            return;
        }
        
        // Check if we need client credentials
        if (!config.clientId || !config.clientSecret) {
            console.warn('Client credentials not configured. Set clientId and clientSecret in environment.');
            return;
        }
        
        // Get current tokens from environment
        let longTermToken = pm.environment.get(config.longTokenVar);
        const shortTermToken = pm.environment.get(config.shortTokenVar);
        const tokenExpiry = pm.environment.get(config.tokenExpiryVar);
        
        // Check if we need to refresh tokens
        if (!longTermToken) {
            // No long-term token, get one
            longTermToken = await getLongTermToken();
        }
        
        if (!shortTermToken || isTokenExpired(tokenExpiry)) {
            // No short-term token or it's expired, get a new one
            await getShortTermToken(longTermToken);
        } else {
            console.log('Using existing valid short-term token');
        }
        
        // Set the Authorization header with the short-term token
        const currentShortToken = pm.environment.get(config.shortTokenVar);

        // FIX: Check URL host (resolved) OR baseUrl variable (for templates)
        const requestUrl = pm.request.url.toString();
        const urlHost = Array.isArray(pm.request.url.host) ? pm.request.url.host.join('.') : (pm.request.url.host || '');
        const baseUrlVar = pm.environment.get('baseUrl') || '';

        // Check both the resolved host AND the baseUrl variable
        const isMockServer = urlHost.includes('mock.pstmn.io') ||
                           urlHost.includes('localhost') ||
                           baseUrlVar.includes('mock.pstmn.io') ||
                           baseUrlVar.includes('localhost:4010') ||
                           pm.environment.get('isMockServer') === 'true';

        // Enhanced logging for debugging
        console.log('=== JWT AUTH DEBUG ===');
        console.log('Request URL:', requestUrl);
        console.log('URL Host (resolved):', urlHost);
        console.log('BaseUrl variable:', baseUrlVar);
        console.log('Is mock server:', isMockServer);
        console.log('Short-term token (last 20 chars):', currentShortToken ? '...' + currentShortToken.slice(-20) : 'NONE');

        if (!isMockServer) {
            pm.request.headers.add({
                key: 'Authorization',
                value: `Bearer ${currentShortToken}`
            });
            console.log('✅ Authorization header ADDED (real API detected)');
        } else {
            console.log('⏭️  Authorization header SKIPPED (mock server detected)');
        }
        console.log('=== END DEBUG ===');
        
    } catch (error) {
        console.error('Authentication failed:', error);
        throw error;
    }
}

// Execute authentication
authenticate().catch(error => {
    // Set an error variable that tests can check
    pm.environment.set('authError', error.toString());
    console.error('Pre-request script failed:', error);
});

// Utility functions for manual token management (can be called from Tests tab)
pm.globals.set('revokeCurrentToken', async function() {
    const tokenId = pm.environment.get(config.tokenIdVar);
    const token = pm.environment.get(config.shortTokenVar);
    
    if (!tokenId || !token) {
        console.log('No token to revoke');
        return;
    }
    
    const request = {
        url: `${config.authUrl}/auth/tokens/${tokenId}/revoke`,
        method: 'POST',
        header: {
            'Authorization': `Bearer ${token}`
        }
    };
    
    pm.sendRequest(request, (err, response) => {
        if (err) {
            console.error('Failed to revoke token:', err);
        } else if (response.code === 200 || response.code === 204) {
            console.log(`Token ${tokenId} revoked successfully`);
            pm.environment.unset(config.shortTokenVar);
            pm.environment.unset(config.tokenExpiryVar);
            pm.environment.unset(config.tokenIdVar);
        } else {
            console.error('Failed to revoke token:', response.text());
        }
    });
});

pm.globals.set('refreshTokens', async function() {
    try {
        const longTermToken = pm.environment.get(config.longTokenVar) || await getLongTermToken();
        await getShortTermToken(longTermToken);
        console.log('Tokens refreshed successfully');
    } catch (error) {
        console.error('Failed to refresh tokens:', error);
    }
});