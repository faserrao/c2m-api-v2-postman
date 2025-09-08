# C2M API v1 to v2 Migration Strategy

## Overview

This document outlines the strategy for migrating existing v1 customers to v2 with AWS Cognito authentication, while maintaining backward compatibility and ensuring zero downtime.

## Current State (v1) vs Future State (v2)

### v1 Authentication (Current)
- Custom authentication system
- API keys or basic auth
- Customer data isolation via API key mapping
- Existing customer base actively using the API

### v2 Authentication (New)
- AWS Cognito with OAuth 2.0
- Client credentials flow
- JWT tokens with customer context
- Enhanced security and scalability

## Migration Approach: Dual Support Strategy

### Phase 1: Parallel Operation (Months 1-6)
Run both authentication systems simultaneously:

```
                    ┌─────────────────┐
                    │ Load Balancer   │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
        ┌───────▼────────┐       ┌───────▼────────┐
        │ v1 Auth        │       │ v2 Auth        │
        │ (Legacy)       │       │ (Cognito)      │
        └───────┬────────┘       └───────┬────────┘
                │                         │
                └────────────┬────────────┘
                             │
                    ┌────────▼────────┐
                    │ API Business    │
                    │ Logic           │
                    └─────────────────┘
```

## Implementation Steps

### 1. Update API Gateway to Support Both Auth Methods

```javascript
// Lambda Authorizer - Supports both v1 and v2
exports.handler = async (event) => {
    const authHeader = event.authorizationToken;
    
    try {
        // Check if it's a v2 JWT token
        if (authHeader.startsWith('Bearer ') && authHeader.includes('.')) {
            return await handleV2Authentication(authHeader);
        } 
        // Fall back to v1 authentication
        else {
            return await handleV1Authentication(authHeader);
        }
    } catch (error) {
        console.error('Authentication failed:', error);
        throw new Error('Unauthorized');
    }
};

async function handleV1Authentication(authHeader) {
    // Extract v1 API key
    const apiKey = authHeader.replace('Bearer ', '').replace('ApiKey ', '');
    
    // Validate against v1 system
    const customer = await validateV1ApiKey(apiKey);
    
    if (!customer) {
        throw new Error('Invalid v1 API key');
    }
    
    // Return policy with customer context
    return {
        principalId: `v1-${customer.customerId}`,
        policyDocument: generatePolicy('Allow'),
        context: {
            customerId: customer.customerId,
            authVersion: 'v1',
            migrationStatus: customer.migrationStatus || 'pending'
        }
    };
}

async function handleV2Authentication(authHeader) {
    // Existing Cognito validation logic
    const token = await validateCognitoToken(authHeader);
    
    return {
        principalId: token.client_id,
        policyDocument: generatePolicy('Allow'),
        context: {
            customerId: token['custom:customerId'],
            authVersion: 'v2',
            migrationStatus: 'completed'
        }
    };
}
```

### 2. Customer Migration Tracking Database

```sql
-- Migration tracking table
CREATE TABLE customer_migration (
    customer_id VARCHAR(50) PRIMARY KEY,
    v1_api_key VARCHAR(100),
    v2_client_id VARCHAR(100),
    migration_status VARCHAR(20) DEFAULT 'pending',
    migration_date TIMESTAMP,
    last_v1_usage TIMESTAMP,
    last_v2_usage TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Migration status values:
-- 'pending' - Not yet migrated
-- 'ready' - Cognito credentials created but not used
-- 'testing' - Customer using both v1 and v2
-- 'migrated' - Only using v2
-- 'completed' - v1 access revoked
```

### 3. Automated Migration Process

```javascript
/**
 * Batch migration script for existing customers
 */
async function migrateExistingCustomers() {
    const v1Customers = await getV1Customers();
    
    for (const customer of v1Customers) {
        try {
            // 1. Create Cognito app client
            const appClient = await createCognitoAppClient({
                customerId: customer.id,
                customerName: customer.name,
                plan: customer.plan || 'basic'
            });
            
            // 2. Store migration mapping
            await saveMigrationMapping({
                customerId: customer.id,
                v1ApiKey: customer.apiKey,
                v2ClientId: appClient.ClientId,
                migrationStatus: 'ready'
            });
            
            // 3. Store credentials securely
            await storeV2Credentials(customer.id, {
                clientId: appClient.ClientId,
                clientSecret: appClient.ClientSecret
            });
            
            // 4. Queue notification for customer
            await queueMigrationNotification(customer);
            
            console.log(`Migrated customer: ${customer.id}`);
        } catch (error) {
            console.error(`Failed to migrate ${customer.id}:`, error);
            await logMigrationError(customer.id, error);
        }
    }
}
```

### 4. Customer Communication Templates

```javascript
// Email templates for different migration stages

const templates = {
    initialNotification: {
        subject: 'Important: C2M API v2 Upgrade Available',
        body: `
Dear {{customerName}},

We're excited to announce C2M API v2 with enhanced security and features.
Your v1 API access remains active, and we've prepared your v2 credentials.

What's New:
- OAuth 2.0 authentication with JWT tokens
- Enhanced security with AWS Cognito
- Improved rate limits for ${plan} customers
- New bulk submission endpoints

Your v1 API key will continue to work until {{v1EndDate}}.

Get Started:
1. Download your v2 credentials: {{credentialsLink}}
2. Review migration guide: {{migrationGuideLink}}
3. Test in our sandbox environment
4. Update your integration

Need help? Contact our migration support team.
        `
    },
    
    testingReminder: {
        subject: 'Reminder: Test C2M API v2',
        body: `
We noticed you haven't tested your v2 credentials yet.
v1 API will be deprecated on {{v1EndDate}}.

Quick Start:
- Your v2 credentials are ready: {{credentialsLink}}
- Test endpoint: POST {{apiUrl}}/v2/test
- Migration guide: {{migrationGuideLink}}
        `
    },
    
    deprecationWarning: {
        subject: 'Action Required: C2M API v1 Deprecation',
        body: `
The C2M API v1 will be discontinued on {{v1EndDate}}.
You're still using v1 - please migrate to v2 immediately.

We're here to help with your migration.
        `
    }
};
```

### 5. Gradual Migration Monitoring

```javascript
/**
 * Monitor migration progress and customer adoption
 */
class MigrationMonitor {
    async trackUsage(customerId, version) {
        const timestamp = new Date().toISOString();
        
        if (version === 'v1') {
            await updateLastV1Usage(customerId, timestamp);
        } else {
            await updateLastV2Usage(customerId, timestamp);
            await checkMigrationProgress(customerId);
        }
    }
    
    async checkMigrationProgress(customerId) {
        const usage = await getCustomerUsage(customerId);
        
        // Auto-update migration status based on usage patterns
        if (!usage.lastV1Usage || 
            daysSince(usage.lastV1Usage) > 30) {
            await updateMigrationStatus(customerId, 'migrated');
        } else if (usage.lastV2Usage) {
            await updateMigrationStatus(customerId, 'testing');
        }
    }
    
    async generateMigrationReport() {
        const stats = await db.query(`
            SELECT 
                migration_status,
                COUNT(*) as count,
                AVG(EXTRACT(day FROM NOW() - last_v1_usage)) as avg_days_since_v1
            FROM customer_migration
            GROUP BY migration_status
        `);
        
        return {
            summary: stats,
            readyForV1Shutdown: stats.pending === 0,
            customersStillOnV1: await getActiveV1Customers()
        };
    }
}
```

### 6. Rollback Strategy

```javascript
/**
 * Emergency rollback procedures
 */
const rollbackProcedures = {
    // Re-enable v1 for specific customer
    async enableV1ForCustomer(customerId) {
        await db.update({
            table: 'customer_migration',
            set: { 
                migration_status: 'rollback',
                rollback_reason: 'customer_request'
            },
            where: { customer_id: customerId }
        });
    },
    
    // Global v1 re-enablement
    async globalV1Restore() {
        // Update load balancer to route 100% to v1
        await updateLoadBalancerWeights({
            v1: 100,
            v2: 0
        });
    }
};
```

## Migration Timeline

### Month 1-2: Preparation
- [ ] Deploy dual-auth API Gateway
- [ ] Create migration tracking database
- [ ] Generate v2 credentials for all customers
- [ ] Prepare documentation and support materials

### Month 2-3: Soft Launch
- [ ] Enable v2 for beta customers
- [ ] Monitor and fix issues
- [ ] Refine migration tools

### Month 3-6: Active Migration
- [ ] Send notifications to all customers
- [ ] Provide migration support
- [ ] Track adoption metrics
- [ ] Follow up with laggards

### Month 6: Deprecation
- [ ] Final warnings to v1-only users
- [ ] Disable v1 for migrated customers
- [ ] Plan v1 shutdown date

## Support During Migration

### 1. Dedicated Migration Endpoint
```javascript
// GET /api/migration/status
{
    "customerId": "CUST-123",
    "v1Status": "active",
    "v2Status": "ready",
    "migrationStatus": "pending",
    "v1LastUsed": "2024-01-15T10:30:00Z",
    "v2LastUsed": null,
    "recommendedActions": [
        "Download v2 credentials",
        "Test v2 endpoints",
        "Update production code"
    ]
}
```

### 2. Parallel Testing Support
```javascript
// Allow customers to test v2 while using v1
app.use((req, res, next) => {
    // Add migration headers to help customers test
    res.set({
        'X-API-Version': req.auth.authVersion,
        'X-Migration-Status': req.auth.migrationStatus,
        'X-V1-Deprecation-Date': '2024-07-01'
    });
    next();
});
```

### 3. SDK Updates
```javascript
// Updated SDK with automatic version detection
class C2MClient {
    constructor(config) {
        this.v1Key = config.apiKey;
        this.v2Credentials = config.cognitoCredentials;
        this.preferredVersion = config.version || 'auto';
    }
    
    async authenticate() {
        if (this.preferredVersion === 'v2' || 
            (this.preferredVersion === 'auto' && this.v2Credentials)) {
            return this.authenticateV2();
        }
        return this.authenticateV1();
    }
}
```

## Success Metrics

1. **Migration Adoption Rate**
   - Target: 80% using v2 by month 4
   - 95% by month 6

2. **Zero Downtime**
   - No service interruptions during migration
   - Seamless fallback to v1 if needed

3. **Customer Satisfaction**
   - Support ticket volume < 5% of customer base
   - Positive feedback on new features

## Post-Migration Cleanup

```javascript
// After all customers migrated
async function cleanupV1System() {
    // 1. Archive v1 data
    await archiveV1ApiKeys();
    
    // 2. Remove v1 code paths
    await deployV2OnlyCode();
    
    // 3. Update documentation
    await removeV1Documentation();
    
    // 4. Celebrate! 🎉
}
```