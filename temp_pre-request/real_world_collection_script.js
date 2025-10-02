// JWT Authentication Pre-request Script
// This script automatically handles JWT token acquisition and refresh

// Skip auth for token endpoints themselves
if (pm.request.url.path.includes('auth/tokens')) {
    console.log('Skipping auth for token endpoint');
    return;
}

// Check if we have client credentials
const clientId = pm.environment.get('clientId') || pm.collectionVariables.get('clientId');
const clientSecret = pm.environment.get('clientSecret') || pm.collectionVariables.get('clientSecret');

if (!clientId || !clientSecret) {
    console.warn('Client credentials not configured. Set clientId and clientSecret in environment.');
    return;
}

// Function to get a new token
async function getNewToken() {
    const authUrl = pm.environment.get('authUrl') || pm.collectionVariables.get('authUrl');
    if (!authUrl) {
        console.error('authUrl not configured');
        return null;
    }

    const tokenRequest = {
        url: authUrl + '/auth/tokens/long',
        method: 'POST',
        header: {
            'Content-Type': 'application/json'
        },
        body: {
            mode: 'raw',
            raw: JSON.stringify({
                grant_type: 'client_credentials',
                client_id: clientId,
                client_secret: clientSecret
            })
        }
    };

    try {
        const response = await pm.sendRequest(tokenRequest);
        if (response.code === 200 || response.code === 201) {
            const tokenData = response.json();
            return tokenData.access_token;
        } else {
            console.error('Failed to get token:', response.code, response.status);
            return null;
        }
    } catch (error) {
        console.error('Error getting token:', error);
        return null;
    }
}

// Main authentication logic
(async function() {
    let token = pm.environment.get('authToken') || pm.collectionVariables.get('authToken');
    
    // If no token, get a new one
    if (!token) {
        console.log('No token found, acquiring new token...');
        token = await getNewToken();
        if (token) {
            pm.environment.set('authToken', token);
            pm.collectionVariables.set('authToken', token);
        }
    }
    
    // Add token to request if we have one
    if (token) {
        // Check if we're using a mock server - if so, skip adding the Authorization header
        const baseUrl = pm.environment.get('baseUrl') || pm.collectionVariables.get('baseUrl') || '';
        const isMockServer = baseUrl.includes('mock.pstmn.io') || 
                           baseUrl.includes('localhost:4010') ||
                           pm.environment.get('isMockServer') === 'true';
        
        if (!isMockServer) {
            pm.request.headers.add({
                key: 'Authorization',
                value: 'Bearer ' + token
            });
            console.log('Authorization header added');
        } else {
            console.log('Mock server detected - skipping Authorization header');
        }
    } else {
        console.warn('No token available - request may fail with 401');
    }
})();
