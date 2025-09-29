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
    
    // Check if we're using a mock server
    const baseUrl = pm.environment.get("baseUrl") || "";
    if (baseUrl.includes("mock.pstmn.io")) {
        console.log("✅ JWT token obtained and saved, but NOT attached (mock server detected)");
    } else {
        pm.request.headers.add({
            key: "Authorization",
            value: "Bearer " + token
        });
        console.log("✅ JWT token obtained and Authorization header added (real API)");
    }
});