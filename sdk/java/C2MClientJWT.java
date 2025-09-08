/**
 * C2M API Java SDK Example with JWT Authentication
 */

import com.c2m.api.*;
import com.c2m.api.auth.*;
import com.c2m.model.*;
import com.c2m.api.DefaultApi;
import com.fasterxml.jackson.databind.ObjectMapper;
import okhttp3.*;
import java.io.IOException;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

public class C2MClientJWT {
    private final String clientId;
    private final String clientSecret;
    private final String baseUrl;
    private String longToken;
    private String shortToken;
    private Instant tokenExpiry;
    private final OkHttpClient httpClient;
    private final ObjectMapper objectMapper;
    
    public C2MClientJWT(String clientId, String clientSecret) {
        this(clientId, clientSecret, "https://api.c2m.com/v2");
    }
    
    public C2MClientJWT(String clientId, String clientSecret, String baseUrl) {
        this.clientId = clientId;
        this.clientSecret = clientSecret;
        this.baseUrl = baseUrl;
        this.httpClient = new OkHttpClient();
        this.objectMapper = new ObjectMapper();
    }
    
    private String getLongToken() throws IOException {
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("grant_type", "client_credentials");
        requestBody.put("client_id", clientId);
        requestBody.put("client_secret", clientSecret);
        requestBody.put("scopes", Arrays.asList("jobs:submit", "jobs:read", "templates:read"));
        requestBody.put("ttl_seconds", 2592000);
        
        Request request = new Request.Builder()
            .url(baseUrl + "/auth/tokens/long")
            .post(RequestBody.create(
                MediaType.parse("application/json"),
                objectMapper.writeValueAsString(requestBody)
            ))
            .build();
            
        try (Response response = httpClient.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("Failed to get long token: " + response);
            }
            
            Map<String, Object> responseData = objectMapper.readValue(
                response.body().string(),
                Map.class
            );
            
            longToken = (String) responseData.get("access_token");
            System.out.println("Long-term token obtained: " + responseData.get("token_id"));
            return longToken;
        }
    }
    
    private String getShortToken() throws IOException {
        if (longToken == null) {
            getLongToken();
        }
        
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("scopes", Arrays.asList("jobs:submit"));
        
        Request request = new Request.Builder()
            .url(baseUrl + "/auth/tokens/short")
            .header("Authorization", "Bearer " + longToken)
            .post(RequestBody.create(
                MediaType.parse("application/json"),
                objectMapper.writeValueAsString(requestBody)
            ))
            .build();
            
        try (Response response = httpClient.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("Failed to get short token: " + response);
            }
            
            Map<String, Object> responseData = objectMapper.readValue(
                response.body().string(),
                Map.class
            );
            
            shortToken = (String) responseData.get("access_token");
            tokenExpiry = Instant.parse((String) responseData.get("expires_at"));
            System.out.println("Short-term token obtained: " + responseData.get("token_id"));
            return shortToken;
        }
    }
    
    private String ensureAuthenticated() throws IOException {
        if (shortToken == null || Instant.now().isAfter(tokenExpiry.minus(1, ChronoUnit.MINUTES))) {
            getShortToken();
        }
        return shortToken;
    }
    
    public ApiClient createApiClient() throws IOException {
        String token = ensureAuthenticated();
        
        ApiClient apiClient = Configuration.getDefaultApiClient();
        apiClient.setBasePath(baseUrl);
        
        HttpBearerAuth bearerAuth = (HttpBearerAuth) apiClient.getAuthentication("bearerAuth");
        bearerAuth.setBearerToken(token);
        
        return apiClient;
    }
    
    public static void main(String[] args) {
        try {
            C2MClientJWT client = new C2MClientJWT(
                "your-client-id",
                "your-client-secret"
            );
            
            ApiClient apiClient = client.createApiClient();
            DefaultApi api = new DefaultApi(apiClient);
            
            // Create job request
            Map<String, Object> jobRequest = new HashMap<>();
            jobRequest.put("templateId", "standard-letter");
            jobRequest.put("documentUrl", "https://example.com/document.pdf");
            
            Object result = api.submitSingleDocWithTemplateParams(jobRequest);
            System.out.println("Job submitted: " + result);
            
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}