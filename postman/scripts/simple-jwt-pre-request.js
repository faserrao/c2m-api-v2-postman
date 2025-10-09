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

    // Check if we're using a mock server - FIX: Check ACTUAL request URL
    const requestUrl = pm.request.url.toString();
    const baseUrlVar = pm.environment.get("baseUrl") || "";
    const isMockServer = requestUrl.includes("mock.pstmn.io") ||
                        requestUrl.includes("localhost:4010");

    // Enhanced logging for debugging
    console.log("=== JWT AUTH DEBUG ===");
    console.log("Request URL:", requestUrl);
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