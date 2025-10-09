console.log("Starting JWT auth for:", pm.request.url.getPath());
const authUrl = pm.environment.get("authUrl");
const clientId = pm.environment.get("clientId");
const clientSecret = pm.environment.get("clientSecret");

if (!clientId || !clientSecret) {
    console.error("Missing credentials");
    return;
}

const authRequest = {
    url: authUrl + "/auth/tokens/long",
    method: "POST",
    header: {
        "Content-Type": "application/json",
        "X-Client-Id": clientId
    },
    body: {
        mode: "raw",
        raw: JSON.stringify({
            grant_type: "client_credentials",
            client_id: clientId,
            client_secret: clientSecret
        })
    }
};

pm.sendRequest(authRequest, (err, response) => {
    if (err || (response.code !== 200 && response.code !== 201)) {
        console.error("Auth failed:", err || response.code);
        return;
    }
    const token = response.json().access_token;
    // Always save the token for later use
    pm.environment.set("authToken", token);

    // FIX: Check URL host (resolved) OR baseUrl variable (for templates)
    const requestUrl = pm.request.url.toString();
    const urlHost = Array.isArray(pm.request.url.host) ? pm.request.url.host.join(".") : (pm.request.url.host || "");
    const baseUrlVar = pm.environment.get("baseUrl") || pm.collectionVariables.get("baseUrl") || "";

    // Check both the resolved host AND the baseUrl variable
    const isMockServer = urlHost.includes("mock.pstmn.io") ||
                        urlHost.includes("localhost") ||
                        baseUrlVar.includes("mock.pstmn.io") ||
                        baseUrlVar.includes("localhost:4010");

    // Enhanced logging for debugging
    console.log("=== JWT AUTH DEBUG ===");
    console.log("Request URL:", requestUrl);
    console.log("URL Host (resolved):", urlHost);
    console.log("BaseUrl variable:", baseUrlVar);
    console.log("Is mock server:", isMockServer);
    console.log("Long-term token (last 20 chars):", token ? "..." + token.slice(-20) : "NONE");

    if (!isMockServer) {
        pm.request.headers.add({
            key: "Authorization",
            value: "Bearer " + token
        });
        console.log("✅ JWT token obtained and Authorization header ADDED (real API detected)");
    } else {
        console.log("⏭️  JWT token obtained and saved, but Authorization header SKIPPED (mock server detected)");
    }
    console.log("=== END DEBUG ===");
});