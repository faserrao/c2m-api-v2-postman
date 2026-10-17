// Postman Pre-request Script for AWS Cognito Authentication
// This script authenticates directly with AWS Cognito and manages token refresh

// Configuration - Set these in your Postman environment
const config = {
    // AWS Cognito Configuration
    cognitoDomain: pm.environment.get('cognitoDomain'), // e.g., 'your-domain.auth.us-east-1.amazoncognito.com'
    cognitoRegion: pm.environment.get('cognitoRegion') || 'us-east-1',
    clientId: pm.environment.get('cognitoClientId'),
    clientSecret: pm.environment.get('cognitoClientSecret'),
    scope: pm.environment.get('cognitoScope') || 'c2m-api/read c2m-api/write',
    
    // Token storage variables
    accessTokenVar: 'cognitoAccessToken',
    tokenExpiryVar: 'cognitoTokenExpiry',
    tokenTypeVar: 'cognitoTokenType',
    
    // API Configuration
    apiGatewayUrl: pm.environment.get('apiGatewayUrl') // Your API Gateway URL
};

// Helper function to encode credentials for Basic Auth
function encodeCredentials(clientId, clientSecret) {
    const credentials = `${clientId}:${clientSecret}`;
    return btoa(credentials);
}

// Helper function to check if token is expired
function isTokenExpired(expiryTime) {
    if (!expiryTime) return true;
    const now = Math.floor(Date.now() / 1000); // Current time in seconds
    const bufferTime = 60; // 1 minute buffer
    return (expiryTime - now) <= bufferTime;
}

// Function to get token from Cognito
async function getCognitoToken() {
    console.log('Obtaining new token from AWS Cognito...');
    
    // Cognito token endpoint
    const tokenUrl = `https://${config.cognitoDomain}/oauth2/token`;
    
    // Create form data for client credentials grant
    const formData = {
        grant_type: 'client_credentials',
        scope: config.scope
    };
    
    // Convert to URL-encoded format
    const formBody = Object.keys(formData)
        .map(key => encodeURIComponent(key) + '=' + encodeURIComponent(formData[key]))
        .join('&');
    
    const request = {
        url: tokenUrl,
        method: 'POST',
        header: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': `Basic ${encodeCredentials(config.clientId, config.clientSecret)}`
        },
        body: {
            mode: 'raw',
            raw: formBody
        }
    };
    
    return new Promise((resolve, reject) => {
        pm.sendRequest(request, (err, response) => {
            if (err) {
                console.error('Failed to get Cognito token:', err);
                reject(err);
                return;
            }
            
            if (response.code === 200) {
                const data = response.json();
                
                // Calculate expiry time
                const expiresIn = data.expires_in || 3600; // Default 1 hour
                const expiryTime = Math.floor(Date.now() / 1000) + expiresIn;
                
                // Store token data in environment
                pm.environment.set(config.accessTokenVar, data.access_token);
                pm.environment.set(config.tokenExpiryVar, expiryTime.toString());
                pm.environment.set(config.tokenTypeVar, data.token_type || 'Bearer');
                
                console.log(`Cognito token obtained, expires in ${expiresIn} seconds`);
                console.log(`Token type: ${data.token_type}`);
                console.log(`Scope: ${data.scope || config.scope}`);
                
                // Decode token to extract customer context
                try {
                    const tokenParts = data.access_token.split('.');
                    if (tokenParts.length === 3) {
                        const payload = JSON.parse(atob(tokenParts[1]));
                        
                        // Extract customer context if present
                        const customerId = payload['custom:customerId'] || payload['customerId'];
                        const customerName = payload['custom:customerName'] || payload['customerName'];
                        
                        if (customerId) {
                            pm.environment.set('currentCustomerId', customerId);
                            pm.environment.set('currentCustomerName', customerName || '');
                            
                            console.log('=== Customer Context ===');
                            console.log(`Customer ID: ${customerId}`);
                            console.log(`Customer Name: ${customerName || 'N/A'}`);
                            console.log(`Client ID: ${payload.client_id}`);
                        }
                    }
                } catch (e) {
                    console.warn('Could not decode token for customer context:', e.message);
                }
                
                resolve({
                    accessToken: data.access_token,
                    tokenType: data.token_type || 'Bearer',
                    expiresIn: expiresIn
                });
            } else {
                console.error('Failed to get Cognito token:', response.text());
                console.error('Response code:', response.code);
                reject(new Error(`HTTP ${response.code}: ${response.text()}`));
            }
        });
    });
}

// Function to validate configuration
function validateConfig() {
    const missing = [];
    
    if (!config.cognitoDomain) missing.push('cognitoDomain');
    if (!config.clientId) missing.push('cognitoClientId');
    if (!config.clientSecret) missing.push('cognitoClientSecret');
    
    if (missing.length > 0) {
        throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }
}

// Main authentication flow
async function authenticate() {
    try {
        // Skip auth for certain endpoints if needed
        const currentPath = pm.request.url.getPath();
        const skipPaths = ['/health', '/status', '/public'];
        
        if (skipPaths.some(path => currentPath.includes(path))) {
            console.log(`Skipping auth for public endpoint: ${currentPath}`);
            return;
        }
        
        // Validate configuration
        validateConfig();
        
        // Get current token from environment
        const accessToken = pm.environment.get(config.accessTokenVar);
        const tokenExpiry = parseInt(pm.environment.get(config.tokenExpiryVar) || '0');
        const tokenType = pm.environment.get(config.tokenTypeVar) || 'Bearer';
        
        // Check if we need to refresh the token
        if (!accessToken || isTokenExpired(tokenExpiry)) {
            console.log('Token missing or expired, obtaining new token...');
            const tokenData = await getCognitoToken();
            
            // Update the Authorization header with new token
            pm.request.headers.upsert({
                key: 'Authorization',
                value: `${tokenData.tokenType} ${tokenData.accessToken}`
            });
        } else {
            console.log('Using existing valid Cognito token');
            // Set the Authorization header with existing token
            pm.request.headers.upsert({
                key: 'Authorization',
                value: `${tokenType} ${accessToken}`
            });
        }
        
        // Add additional headers if needed
        pm.request.headers.upsert({
            key: 'X-Client-Id',
            value: config.clientId
        });
        
        console.log('Authentication complete, Authorization header set');
        
    } catch (error) {
        console.error('Authentication failed:', error);
        
        // Set error in environment for test assertions
        pm.environment.set('authError', error.toString());
        
        // Clear invalid tokens
        pm.environment.unset(config.accessTokenVar);
        pm.environment.unset(config.tokenExpiryVar);
        
        // Re-throw to fail the request
        throw error;
    }
}

// Execute authentication
authenticate().catch(error => {
    console.error('Pre-request script failed:', error);
    console.error('Please check your Cognito configuration in the environment variables');
});

// Utility functions for manual token management
pm.globals.set('clearCognitoTokens', function() {
    pm.environment.unset(config.accessTokenVar);
    pm.environment.unset(config.tokenExpiryVar);
    pm.environment.unset(config.tokenTypeVar);
    console.log('Cognito tokens cleared');
});

pm.globals.set('refreshCognitoToken', async function() {
    try {
        await getCognitoToken();
        console.log('Cognito token refreshed successfully');
    } catch (error) {
        console.error('Failed to refresh Cognito token:', error);
    }
});

// Debug function to display current token info
pm.globals.set('debugCognitoAuth', function() {
    const token = pm.environment.get(config.accessTokenVar);
    const expiry = pm.environment.get(config.tokenExpiryVar);
    const type = pm.environment.get(config.tokenTypeVar);
    const customerId = pm.environment.get('currentCustomerId');
    const customerName = pm.environment.get('currentCustomerName');
    
    if (token) {
        const expiryTime = parseInt(expiry || '0');
        const now = Math.floor(Date.now() / 1000);
        const remaining = expiryTime - now;
        
        console.log('=== Cognito Auth Debug Info ===');
        console.log(`Token Type: ${type}`);
        console.log(`Token Present: Yes (${token.substring(0, 20)}...)`);
        console.log(`Expires in: ${remaining > 0 ? remaining + ' seconds' : 'EXPIRED'}`);
        console.log(`Client ID: ${config.clientId}`);
        console.log(`Cognito Domain: ${config.cognitoDomain}`);
        console.log(`Scope: ${config.scope}`);
        
        if (customerId) {
            console.log('\n=== Customer Context ===');
            console.log(`Customer ID: ${customerId}`);
            console.log(`Customer Name: ${customerName || 'N/A'}`);
        }
        
        // Decode and display token claims
        try {
            const tokenParts = token.split('.');
            if (tokenParts.length === 3) {
                const payload = JSON.parse(atob(tokenParts[1]));
                console.log('\n=== Token Claims ===');
                console.log(JSON.stringify(payload, null, 2));
            }
        } catch (e) {
            console.log('Could not decode token');
        }
    } else {
        console.log('No Cognito token present');
    }
});

// Utility function to validate customer access
pm.globals.set('validateCustomerAccess', function(resourceCustomerId) {
    const tokenCustomerId = pm.environment.get('currentCustomerId');
    
    if (!tokenCustomerId) {
        console.warn('No customer context in token - cannot validate access');
        return false;
    }
    
    const hasAccess = tokenCustomerId === resourceCustomerId;
    
    if (!hasAccess) {
        console.error(`Access denied: Token customer ${tokenCustomerId} cannot access resource owned by ${resourceCustomerId}`);
    }
    
    return hasAccess;
});