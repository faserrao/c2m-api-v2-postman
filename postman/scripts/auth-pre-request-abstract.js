// Abstract pre-request script that delegates to a configured auth provider
// This allows swapping between different auth implementations (JWT, Cognito, etc.)

// Get the auth provider script from collection variables
const authProviderScript = pm.collectionVariables.get('authProviderScript');

if (!authProviderScript) {
    console.warn('No auth provider configured. Please run: make postman-auth-setup');
    return;
}

// Execute the auth provider script
try {
    eval(authProviderScript);
} catch (error) {
    console.error('Auth provider script failed:', error);
    pm.environment.set('authError', error.toString());
}