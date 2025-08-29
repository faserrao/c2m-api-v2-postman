/**
 * JWT Authentication Test Suite
 * 
 * This file contains comprehensive tests for the JWT authentication endpoints.
 * Can be run with Node.js or integrated into your testing framework.
 */

const axios = require('axios');
const assert = require('assert');

// Test configuration
const config = {
    baseUrl: process.env.API_BASE_URL || 'http://localhost:4010',
    clientId: process.env.TEST_CLIENT_ID || 'c2m_test_client',
    clientSecret: process.env.TEST_CLIENT_SECRET || 'test_secret',
    testTimeout: 30000
};

// Test data storage
let testData = {
    longTermToken: null,
    longTokenId: null,
    shortTermToken: null,
    shortTokenId: null
};

// Helper function to make API requests
async function apiRequest(method, endpoint, data = null, headers = {}) {
    try {
        const response = await axios({
            method,
            url: `${config.baseUrl}${endpoint}`,
            data,
            headers: {
                'Content-Type': 'application/json',
                ...headers
            },
            validateStatus: () => true // Don't throw on any status
        });
        return response;
    } catch (error) {
        console.error(`Request failed: ${method} ${endpoint}`, error.message);
        throw error;
    }
}

// Test Suite
const jwtAuthTests = {
    // Test 1: Get long-term token with valid credentials
    async testGetLongTermTokenSuccess() {
        console.log('Test 1: Get long-term token with valid credentials');
        
        const response = await apiRequest('POST', '/auth/tokens/long', {
            grant_type: 'client_credentials',
            client_id: config.clientId,
            client_secret: config.clientSecret,
            scopes: ['jobs:submit', 'templates:read', 'tokens:revoke'],
            ttl_seconds: 3600 // 1 hour for testing
        }, {
            'X-Client-Id': config.clientId
        });

        assert.strictEqual(response.status, 201, 'Should return 201 Created');
        assert.strictEqual(response.data.token_type, 'Bearer', 'Token type should be Bearer');
        assert(response.data.access_token, 'Should have access_token');
        assert(response.data.expires_in, 'Should have expires_in');
        assert(response.data.expires_at, 'Should have expires_at');
        assert(response.data.token_id, 'Should have token_id');
        assert(Array.isArray(response.data.scopes), 'Scopes should be an array');
        
        // Store for later tests
        testData.longTermToken = response.data.access_token;
        testData.longTokenId = response.data.token_id;
        
        console.log('✅ Test passed');
    },

    // Test 2: Get long-term token with invalid credentials
    async testGetLongTermTokenInvalidCredentials() {
        console.log('Test 2: Get long-term token with invalid credentials');
        
        const response = await apiRequest('POST', '/auth/tokens/long', {
            grant_type: 'client_credentials',
            client_id: config.clientId,
            client_secret: 'wrong_secret',
            scopes: ['jobs:submit']
        }, {
            'X-Client-Id': config.clientId
        });

        assert.strictEqual(response.status, 401, 'Should return 401 Unauthorized');
        assert(response.data.code, 'Should have error code');
        assert(response.data.message, 'Should have error message');
        
        console.log('✅ Test passed');
    },

    // Test 3: Get long-term token with missing grant_type
    async testGetLongTermTokenMissingGrantType() {
        console.log('Test 3: Get long-term token with missing grant_type');
        
        const response = await apiRequest('POST', '/auth/tokens/long', {
            client_id: config.clientId,
            client_secret: config.clientSecret
        }, {
            'X-Client-Id': config.clientId
        });

        assert.strictEqual(response.status, 400, 'Should return 400 Bad Request');
        assert.strictEqual(response.data.code, 'invalid_grant', 'Should have invalid_grant error');
        
        console.log('✅ Test passed');
    },

    // Test 4: Exchange for short-term token
    async testGetShortTermTokenSuccess() {
        console.log('Test 4: Exchange for short-term token');
        
        assert(testData.longTermToken, 'Need long-term token from previous test');
        
        const response = await apiRequest('POST', '/auth/tokens/short', {
            scopes: ['jobs:submit']
        }, {
            'Authorization': `Bearer ${testData.longTermToken}`
        });

        assert.strictEqual(response.status, 201, 'Should return 201 Created');
        assert.strictEqual(response.data.token_type, 'Bearer', 'Token type should be Bearer');
        assert(response.data.access_token, 'Should have access_token');
        assert(response.data.expires_in >= 890 && response.data.expires_in <= 910, 
            'Short token should expire in ~15 minutes');
        assert(response.data.token_id, 'Should have token_id');
        
        // Verify JWT format (basic check)
        const tokenParts = response.data.access_token.split('.');
        assert.strictEqual(tokenParts.length, 3, 'JWT should have 3 parts');
        
        // Store for later tests
        testData.shortTermToken = response.data.access_token;
        testData.shortTokenId = response.data.token_id;
        
        console.log('✅ Test passed');
    },

    // Test 5: Get short-term token without auth
    async testGetShortTermTokenNoAuth() {
        console.log('Test 5: Get short-term token without auth');
        
        const response = await apiRequest('POST', '/auth/tokens/short', {
            scopes: ['jobs:submit']
        });

        assert.strictEqual(response.status, 401, 'Should return 401 Unauthorized');
        assert(response.data.code, 'Should have error code');
        
        console.log('✅ Test passed');
    },

    // Test 6: Use short-term token for API request
    async testUseShortTermToken() {
        console.log('Test 6: Use short-term token for API request');
        
        assert(testData.shortTermToken, 'Need short-term token from previous test');
        
        // Test with a simple job submission
        const response = await apiRequest('POST', '/jobs/single-doc-job-template', {
            jobTemplate: 'test-template',
            paymentDetails: {
                creditCardDetails: {
                    cardType: 'visa',
                    cardNumber: '4111111111111111',
                    expirationDate: { month: 12, year: 2025 },
                    cvv: 123
                }
            }
        }, {
            'Authorization': `Bearer ${testData.shortTermToken}`
        });

        // Should either succeed (200) or fail with validation (400), but not auth (401)
        assert([200, 400].includes(response.status), 
            `Expected 200 or 400, got ${response.status}`);
        
        console.log('✅ Test passed');
    },

    // Test 7: Revoke short-term token
    async testRevokeShortTermToken() {
        console.log('Test 7: Revoke short-term token');
        
        assert(testData.shortTokenId, 'Need token ID from previous test');
        assert(testData.longTermToken, 'Need long-term token for auth');
        
        const response = await apiRequest('POST', `/auth/tokens/${testData.shortTokenId}/revoke`, null, {
            'Authorization': `Bearer ${testData.longTermToken}`
        });

        assert.strictEqual(response.status, 204, 'Should return 204 No Content');
        
        console.log('✅ Test passed');
    },

    // Test 8: Verify revoked token is rejected
    async testUseRevokedToken() {
        console.log('Test 8: Verify revoked token is rejected');
        
        assert(testData.shortTermToken, 'Need revoked token from previous test');
        
        const response = await apiRequest('POST', '/jobs/single-doc-job-template', {
            jobTemplate: 'test-template'
        }, {
            'Authorization': `Bearer ${testData.shortTermToken}`
        });

        assert.strictEqual(response.status, 401, 'Should return 401 Unauthorized');
        assert.strictEqual(response.data.code, 'invalid_token', 'Should indicate invalid token');
        
        console.log('✅ Test passed');
    },

    // Test 9: Revoke is idempotent
    async testRevokeIdempotent() {
        console.log('Test 9: Revoke is idempotent');
        
        assert(testData.shortTokenId, 'Need token ID from previous test');
        assert(testData.longTermToken, 'Need long-term token for auth');
        
        // Second revocation of same token
        const response = await apiRequest('POST', `/auth/tokens/${testData.shortTokenId}/revoke`, null, {
            'Authorization': `Bearer ${testData.longTermToken}`
        });

        assert([204, 404].includes(response.status), 
            'Should return 204 (idempotent) or 404 (already revoked)');
        
        console.log('✅ Test passed');
    },

    // Test 10: Get long-term token with OTP (mock)
    async testGetLongTermTokenWithOTP() {
        console.log('Test 10: Get long-term token with OTP');
        
        const response = await apiRequest('POST', '/auth/tokens/long', {
            grant_type: 'client_credentials',
            client_id: config.clientId,
            otp_code: '123456', // Mock OTP
            scopes: ['jobs:*'],
            ttl_seconds: 7200
        }, {
            'X-Client-Id': config.clientId
        });

        // Should either succeed (if OTP is implemented) or fail with specific error
        if (response.status === 201) {
            assert(response.data.access_token, 'Should have access_token');
            console.log('✅ OTP authentication succeeded');
        } else {
            assert.strictEqual(response.status, 401, 'Should return 401 if OTP invalid');
            assert(response.data.code, 'Should have error code');
            console.log('✅ OTP authentication properly rejected');
        }
    },

    // Test 11: Token scope narrowing
    async testTokenScopeNarrowing() {
        console.log('Test 11: Token scope narrowing');
        
        // Get new long-term token with broad scope
        const longResponse = await apiRequest('POST', '/auth/tokens/long', {
            grant_type: 'client_credentials',
            client_id: config.clientId,
            client_secret: config.clientSecret,
            scopes: ['jobs:*', 'templates:*', 'tokens:*'],
            ttl_seconds: 3600
        }, {
            'X-Client-Id': config.clientId
        });

        assert.strictEqual(longResponse.status, 201, 'Should get long-term token');
        const broadToken = longResponse.data.access_token;
        const broadScopes = longResponse.data.scopes;
        
        // Exchange for short-term token with narrowed scope
        const shortResponse = await apiRequest('POST', '/auth/tokens/short', {
            scopes: ['jobs:submit'] // Narrow scope
        }, {
            'Authorization': `Bearer ${broadToken}`
        });

        assert.strictEqual(shortResponse.status, 201, 'Should get short-term token');
        const narrowScopes = shortResponse.data.scopes;
        
        assert(narrowScopes.length < broadScopes.length || 
               narrowScopes.every(s => !s.includes('*')), 
               'Short token should have narrower scope');
        
        console.log('✅ Test passed');
    },

    // Test 12: Rate limiting
    async testRateLimiting() {
        console.log('Test 12: Rate limiting');
        
        // Make multiple rapid requests
        const requests = [];
        for (let i = 0; i < 10; i++) {
            requests.push(
                apiRequest('POST', '/auth/tokens/short', {}, {
                    'Authorization': `Bearer ${testData.longTermToken}`
                })
            );
        }
        
        const responses = await Promise.all(requests);
        const rateLimited = responses.some(r => r.status === 429);
        
        if (rateLimited) {
            const limitedResponse = responses.find(r => r.status === 429);
            assert.strictEqual(limitedResponse.data.code, 'rate_limited', 
                'Should have rate_limited error code');
            assert(limitedResponse.data.message.includes('retry'), 
                'Should indicate retry time');
            console.log('✅ Rate limiting is active');
        } else {
            console.log('⚠️  Rate limiting not triggered (may need more requests)');
        }
    }
};

// Run all tests
async function runAllTests() {
    console.log('🚀 Starting JWT Authentication Tests\n');
    console.log(`API Base URL: ${config.baseUrl}`);
    console.log(`Client ID: ${config.clientId}\n`);
    
    const tests = Object.entries(jwtAuthTests);
    let passed = 0;
    let failed = 0;
    
    for (const [name, test] of tests) {
        try {
            await test();
            passed++;
        } catch (error) {
            failed++;
            console.error(`❌ Test failed: ${name}`);
            console.error(`   Error: ${error.message}`);
            if (error.response) {
                console.error(`   Response: ${JSON.stringify(error.response.data)}`);
            }
        }
        console.log(''); // Empty line between tests
    }
    
    console.log('📊 Test Summary:');
    console.log(`   ✅ Passed: ${passed}`);
    console.log(`   ❌ Failed: ${failed}`);
    console.log(`   📝 Total: ${tests.length}`);
    
    return failed === 0;
}

// Export for use in other test frameworks
module.exports = {
    config,
    jwtAuthTests,
    runAllTests
};

// Run tests if executed directly
if (require.main === module) {
    runAllTests()
        .then(success => process.exit(success ? 0 : 1))
        .catch(error => {
            console.error('Test suite error:', error);
            process.exit(1);
        });
}