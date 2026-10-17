// Abstract Authentication Pre-request Script for C2M API
// This script delegates to a specific auth provider implementation

// Check if auth provider script is available
if (!pm.collectionVariables.get('authProviderScript')) {
    console.warn('No auth provider configured. Please run: make postman-auth-setup');
    return;
}

// Load and execute the provider-specific auth script
try {
    // The actual provider script is injected by the build process
    const authProvider = pm.collectionVariables.get('authProviderScript');
    eval(authProvider);
} catch (error) {
    console.error('Failed to execute auth provider script:', error);
    pm.environment.set('authError', error.toString());
}