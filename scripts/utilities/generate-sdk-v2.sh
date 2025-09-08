#!/usr/bin/env bash
# ========================================================================
# SDK Generator for C2M API v2
# ========================================================================
# Generates client SDKs in multiple languages using OpenAPI Generator
# with improved error handling and JWT authentication examples
# ========================================================================

set -eo pipefail

# Configuration
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OPENAPI_SPEC="${PROJECT_ROOT}/openapi/c2mapiv2-openapi-spec-final.yaml"
SDK_BASE_DIR="${PROJECT_ROOT}/sdk"
OPENAPI_GENERATOR_VERSION="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if OpenAPI spec exists
check_openapi_spec() {
    if [ ! -f "$OPENAPI_SPEC" ]; then
        print_error "OpenAPI spec not found: $OPENAPI_SPEC"
        print_info "Run 'make openapi-build' to generate the spec first"
        exit 1
    fi
}

# Check if OpenAPI Generator is installed
check_openapi_generator() {
    if ! command -v openapi-generator-cli &> /dev/null && ! command -v openapi-generator &> /dev/null; then
        print_warning "OpenAPI Generator CLI not found"
        print_info "Installing OpenAPI Generator CLI..."
        
        if command -v npm &> /dev/null; then
            npm install -g @openapitools/openapi-generator-cli
        else
            print_error "npm not found. Please install Node.js and npm first"
            exit 1
        fi
    fi
}

# Get OpenAPI generator command
get_generator_cmd() {
    if command -v openapi-generator-cli &> /dev/null; then
        echo "openapi-generator-cli"
    elif command -v openapi-generator &> /dev/null; then
        echo "openapi-generator"
    else
        echo ""
    fi
}

# Function to get language-specific parameters
get_generator_params() {
    local lang=$1
    case $lang in
        "python")
            echo "python --package-name c2m_api"
            ;;
        "javascript")
            echo "javascript --invoker-package c2m_api"
            ;;
        "typescript")
            echo "typescript-axios --package-name c2m-api-ts"
            ;;
        "java")
            echo "java --artifact-id c2m-api --group-id com.c2m --api-package com.c2m.api --model-package com.c2m.model"
            ;;
        "go")
            echo "go --package-name c2mapi"
            ;;
        "ruby")
            echo "ruby"
            ;;
        "php")
            echo "php --invoker-package C2M\\Api"
            ;;
        "csharp")
            echo "csharp --package-name C2M.Api"
            ;;
        "swift")
            echo "swift5"
            ;;
        "kotlin")
            echo "kotlin --package-name com.c2m.api"
            ;;
        "rust")
            echo "rust --package-name c2m_api"
            ;;
        *)
            return 1
            ;;
    esac
}

# Function to generate SDK
generate_sdk() {
    local language=$1
    local output_dir=$2
    
    # Get generator command
    local generator_cmd=$(get_generator_cmd)
    if [ -z "$generator_cmd" ]; then
        print_error "OpenAPI Generator not found"
        return 1
    fi
    
    # Get language-specific parameters
    local params=$(get_generator_params "$language")
    if [ -z "$params" ]; then
        print_error "Unknown language: $language"
        return 1
    fi
    
    print_info "Generating $language SDK..."
    
    # Create output directory
    mkdir -p "$output_dir"
    
    # Clean up any existing broken symlinks
    find "$output_dir" -type l -exec test ! -e {} \; -delete 2>/dev/null || true
    
    # Run OpenAPI Generator
    local cmd="$generator_cmd generate -g $params -i $OPENAPI_SPEC -o $output_dir"
    print_info "Running: $cmd"
    
    if $cmd; then
        print_success "SDK generated successfully in: $output_dir"
        
        # Post-generation steps
        case $language in
            "python")
                print_info "Creating Python requirements file..."
                echo "requests>=2.25.0" > "$output_dir/requirements.txt"
                echo "python-dateutil>=2.8.0" >> "$output_dir/requirements.txt"
                echo "urllib3>=1.25.3" >> "$output_dir/requirements.txt"
                ;;
            "javascript"|"typescript")
                if [ -f "$output_dir/package.json" ]; then
                    print_info "Installing npm dependencies..."
                    (cd "$output_dir" && npm install --no-audit --no-fund) || print_warning "npm install failed"
                fi
                ;;
        esac
        
        # Create JWT authentication example
        create_jwt_example "$language" "$output_dir"
        
        return 0
    else
        print_error "Failed to generate SDK"
        return 1
    fi
}

# Function to create JWT authentication examples
create_jwt_example() {
    local language=$1
    local output_dir=$2
    
    # Skip if output directory doesn't exist
    if [ ! -d "$output_dir" ]; then
        return
    fi
    
    local example_file=""
    
    case $language in
        "python")
            example_file="$output_dir/example_jwt.py"
            cat > "$example_file" << 'EOF'
#!/usr/bin/env python3
"""
C2M API Python SDK Example with JWT Authentication
"""

import c2m_api
from c2m_api.rest import ApiException
import requests
import time
from datetime import datetime, timedelta

class C2MClient:
    def __init__(self, client_id, client_secret, base_url="https://api.c2m.com/v2"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.auth_url = base_url
        self.long_token = None
        self.short_token = None
        self.token_expiry = None
        
    def get_long_token(self):
        """Get long-term token from auth service"""
        response = requests.post(
            f"{self.auth_url}/auth/tokens/long",
            json={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scopes": ["jobs:submit", "jobs:read", "templates:read"],
                "ttl_seconds": 2592000  # 30 days
            }
        )
        response.raise_for_status()
        data = response.json()
        self.long_token = data["access_token"]
        print(f"Long-term token obtained: {data['token_id']}")
        return self.long_token
        
    def get_short_token(self):
        """Exchange long token for short-term token"""
        if not self.long_token:
            self.get_long_token()
            
        response = requests.post(
            f"{self.auth_url}/auth/tokens/short",
            headers={"Authorization": f"Bearer {self.long_token}"},
            json={"scopes": ["jobs:submit"]}
        )
        response.raise_for_status()
        data = response.json()
        self.short_token = data["access_token"]
        self.token_expiry = datetime.fromisoformat(data["expires_at"].replace('Z', '+00:00'))
        print(f"Short-term token obtained: {data['token_id']}")
        return self.short_token
        
    def ensure_authenticated(self):
        """Ensure we have a valid token"""
        if not self.short_token or datetime.now() >= self.token_expiry - timedelta(minutes=1):
            self.get_short_token()
        return self.short_token
        
    def create_api_client(self):
        """Create configured API client"""
        token = self.ensure_authenticated()
        
        configuration = c2m_api.Configuration()
        configuration.host = self.base_url
        configuration.api_key['bearerAuth'] = token
        configuration.api_key_prefix['bearerAuth'] = 'Bearer'
        
        return c2m_api.ApiClient(configuration)
    
    def submit_job(self, job_params):
        """Submit a job using the SDK"""
        with self.create_api_client() as api_client:
            jobs_api = c2m_api.DefaultApi(api_client)
            
            try:
                response = jobs_api.submit_single_doc_with_template_params(job_params)
                return response
            except ApiException as e:
                if e.status in [401, 403]:
                    # Token expired, refresh and retry
                    self.short_token = None
                    with self.create_api_client() as api_client:
                        jobs_api = c2m_api.DefaultApi(api_client)
                        response = jobs_api.submit_single_doc_with_template_params(job_params)
                        return response
                raise

# Usage example
if __name__ == "__main__":
    # Initialize client
    client = C2MClient(
        client_id="your-client-id",
        client_secret="your-client-secret"
    )
    
    # Submit a job
    job_params = {
        "templateId": "standard-letter",
        "documentUrl": "https://example.com/document.pdf",
        "recipients": [{
            "name": "John Doe",
            "address": {
                "line1": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001"
            }
        }]
    }
    
    try:
        result = client.submit_job(job_params)
        print(f"Job submitted: {result}")
    except Exception as e:
        print(f"Error: {e}")
EOF
            ;;
            
        "javascript")
            example_file="$output_dir/example_jwt.js"
            cat > "$example_file" << 'EOF'
/**
 * C2M API JavaScript SDK Example with JWT Authentication
 */

const C2mApi = require('c2m_api');
const axios = require('axios');

class C2MClient {
    constructor(clientId, clientSecret, baseUrl = 'https://api.c2m.com/v2') {
        this.clientId = clientId;
        this.clientSecret = clientSecret;
        this.baseUrl = baseUrl;
        this.authUrl = baseUrl;
        this.longToken = null;
        this.shortToken = null;
        this.tokenExpiry = null;
    }
    
    async getLongToken() {
        const response = await axios.post(`${this.authUrl}/auth/tokens/long`, {
            grant_type: 'client_credentials',
            client_id: this.clientId,
            client_secret: this.clientSecret,
            scopes: ['jobs:submit', 'jobs:read', 'templates:read'],
            ttl_seconds: 2592000 // 30 days
        });
        
        this.longToken = response.data.access_token;
        console.log(`Long-term token obtained: ${response.data.token_id}`);
        return this.longToken;
    }
    
    async getShortToken() {
        if (!this.longToken) {
            await this.getLongToken();
        }
        
        const response = await axios.post(
            `${this.authUrl}/auth/tokens/short`,
            { scopes: ['jobs:submit'] },
            { headers: { Authorization: `Bearer ${this.longToken}` } }
        );
        
        this.shortToken = response.data.access_token;
        this.tokenExpiry = new Date(response.data.expires_at);
        console.log(`Short-term token obtained: ${response.data.token_id}`);
        return this.shortToken;
    }
    
    async ensureAuthenticated() {
        const now = new Date();
        const buffer = new Date(now.getTime() + 60000); // 1 minute buffer
        
        if (!this.shortToken || buffer >= this.tokenExpiry) {
            await this.getShortToken();
        }
        
        return this.shortToken;
    }
    
    async configureClient() {
        const token = await this.ensureAuthenticated();
        
        const defaultClient = C2mApi.ApiClient.instance;
        const bearerAuth = defaultClient.authentications['bearerAuth'];
        bearerAuth.accessToken = token;
        defaultClient.basePath = this.baseUrl;
        
        return defaultClient;
    }
    
    async submitJob(jobParams) {
        await this.configureClient();
        const jobsApi = new C2mApi.DefaultApi();
        
        try {
            return await jobsApi.submitSingleDocWithTemplateParams(jobParams);
        } catch (error) {
            if (error.status === 401 || error.status === 403) {
                // Token expired, refresh and retry
                this.shortToken = null;
                await this.configureClient();
                return await jobsApi.submitSingleDocWithTemplateParams(jobParams);
            }
            throw error;
        }
    }
}

// Usage example
async function main() {
    const client = new C2MClient(
        'your-client-id',
        'your-client-secret'
    );
    
    const jobParams = {
        templateId: 'standard-letter',
        documentUrl: 'https://example.com/document.pdf',
        recipients: [{
            name: 'John Doe',
            address: {
                line1: '123 Main St',
                city: 'New York',
                state: 'NY',
                zip: '10001'
            }
        }]
    };
    
    try {
        const result = await client.submitJob(jobParams);
        console.log('Job submitted:', result);
    } catch (error) {
        console.error('Error:', error);
    }
}

// Run if called directly
if (require.main === module) {
    main();
}

module.exports = C2MClient;
EOF
            ;;
            
        "typescript")
            example_file="$output_dir/example_jwt.ts"
            cat > "$example_file" << 'EOF'
/**
 * C2M API TypeScript SDK Example with JWT Authentication
 */

import { Configuration, DefaultApi } from 'c2m-api-ts';
import axios from 'axios';

interface TokenResponse {
    access_token: string;
    token_id: string;
    expires_at: string;
}

class C2MClient {
    private clientId: string;
    private clientSecret: string;
    private baseUrl: string;
    private authUrl: string;
    private longToken: string | null = null;
    private shortToken: string | null = null;
    private tokenExpiry: Date | null = null;
    
    constructor(clientId: string, clientSecret: string, baseUrl = 'https://api.c2m.com/v2') {
        this.clientId = clientId;
        this.clientSecret = clientSecret;
        this.baseUrl = baseUrl;
        this.authUrl = baseUrl;
    }
    
    private async getLongToken(): Promise<string> {
        const response = await axios.post<TokenResponse>(`${this.authUrl}/auth/tokens/long`, {
            grant_type: 'client_credentials',
            client_id: this.clientId,
            client_secret: this.clientSecret,
            scopes: ['jobs:submit', 'jobs:read', 'templates:read'],
            ttl_seconds: 2592000 // 30 days
        });
        
        this.longToken = response.data.access_token;
        console.log(`Long-term token obtained: ${response.data.token_id}`);
        return this.longToken;
    }
    
    private async getShortToken(): Promise<string> {
        if (!this.longToken) {
            await this.getLongToken();
        }
        
        const response = await axios.post<TokenResponse>(
            `${this.authUrl}/auth/tokens/short`,
            { scopes: ['jobs:submit'] },
            { headers: { Authorization: `Bearer ${this.longToken}` } }
        );
        
        this.shortToken = response.data.access_token;
        this.tokenExpiry = new Date(response.data.expires_at);
        console.log(`Short-term token obtained: ${response.data.token_id}`);
        return this.shortToken;
    }
    
    private async ensureAuthenticated(): Promise<string> {
        const now = new Date();
        const buffer = new Date(now.getTime() + 60000); // 1 minute buffer
        
        if (!this.shortToken || !this.tokenExpiry || buffer >= this.tokenExpiry) {
            await this.getShortToken();
        }
        
        return this.shortToken!;
    }
    
    private async getConfiguration(): Promise<Configuration> {
        const token = await this.ensureAuthenticated();
        
        return new Configuration({
            basePath: this.baseUrl,
            accessToken: token
        });
    }
    
    public async submitJob(jobParams: any): Promise<any> {
        const config = await this.getConfiguration();
        const api = new DefaultApi(config);
        
        try {
            return await api.submitSingleDocWithTemplateParams(jobParams);
        } catch (error: any) {
            if (error.response?.status === 401 || error.response?.status === 403) {
                // Token expired, refresh and retry
                this.shortToken = null;
                const newConfig = await this.getConfiguration();
                const newApi = new DefaultApi(newConfig);
                return await newApi.submitSingleDocWithTemplateParams(jobParams);
            }
            throw error;
        }
    }
}

// Usage example
async function main() {
    const client = new C2MClient(
        'your-client-id',
        'your-client-secret'
    );
    
    const jobParams = {
        templateId: 'standard-letter',
        documentUrl: 'https://example.com/document.pdf',
        recipients: [{
            name: 'John Doe',
            address: {
                line1: '123 Main St',
                city: 'New York',
                state: 'NY',
                zip: '10001'
            }
        }]
    };
    
    try {
        const result = await client.submitJob(jobParams);
        console.log('Job submitted:', result);
    } catch (error) {
        console.error('Error:', error);
    }
}

// Run if called directly
if (require.main === module) {
    main().catch(console.error);
}

export default C2MClient;
EOF
            ;;
            
        "java")
            example_file="$output_dir/C2MClientJWT.java"
            cat > "$example_file" << 'EOF'
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
EOF
            ;;
            
        "go")
            example_file="$output_dir/example_jwt.go"
            cat > "$example_file" << 'EOF'
package main

import (
    "bytes"
    "context"
    "encoding/json"
    "fmt"
    "io/ioutil"
    "log"
    "net/http"
    "time"
    
    c2mapi "github.com/c2m/c2m-go-sdk"
)

type C2MClient struct {
    clientID     string
    clientSecret string
    baseURL      string
    authURL      string
    longToken    string
    shortToken   string
    tokenExpiry  time.Time
    httpClient   *http.Client
}

type TokenResponse struct {
    AccessToken string    `json:"access_token"`
    TokenID     string    `json:"token_id"`
    ExpiresAt   time.Time `json:"expires_at"`
}

func NewC2MClient(clientID, clientSecret string) *C2MClient {
    return &C2MClient{
        clientID:     clientID,
        clientSecret: clientSecret,
        baseURL:      "https://api.c2m.com/v2",
        authURL:      "https://api.c2m.com/v2",
        httpClient:   &http.Client{Timeout: 30 * time.Second},
    }
}

func (c *C2MClient) getLongToken() error {
    reqBody, _ := json.Marshal(map[string]interface{}{
        "grant_type":    "client_credentials",
        "client_id":     c.clientID,
        "client_secret": c.clientSecret,
        "scopes":        []string{"jobs:submit", "jobs:read", "templates:read"},
        "ttl_seconds":   2592000,
    })
    
    req, err := http.NewRequest("POST", c.authURL+"/auth/tokens/long", bytes.NewBuffer(reqBody))
    if err != nil {
        return err
    }
    req.Header.Set("Content-Type", "application/json")
    
    resp, err := c.httpClient.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    
    var tokenResp TokenResponse
    if err := json.NewDecoder(resp.Body).Decode(&tokenResp); err != nil {
        return err
    }
    
    c.longToken = tokenResp.AccessToken
    fmt.Printf("Long-term token obtained: %s\n", tokenResp.TokenID)
    return nil
}

func (c *C2MClient) getShortToken() error {
    if c.longToken == "" {
        if err := c.getLongToken(); err != nil {
            return err
        }
    }
    
    reqBody, _ := json.Marshal(map[string]interface{}{
        "scopes": []string{"jobs:submit"},
    })
    
    req, err := http.NewRequest("POST", c.authURL+"/auth/tokens/short", bytes.NewBuffer(reqBody))
    if err != nil {
        return err
    }
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("Authorization", "Bearer "+c.longToken)
    
    resp, err := c.httpClient.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    
    var tokenResp TokenResponse
    if err := json.NewDecoder(resp.Body).Decode(&tokenResp); err != nil {
        return err
    }
    
    c.shortToken = tokenResp.AccessToken
    c.tokenExpiry = tokenResp.ExpiresAt
    fmt.Printf("Short-term token obtained: %s\n", tokenResp.TokenID)
    return nil
}

func (c *C2MClient) ensureAuthenticated() error {
    if c.shortToken == "" || time.Now().After(c.tokenExpiry.Add(-1*time.Minute)) {
        return c.getShortToken()
    }
    return nil
}

func (c *C2MClient) CreateAPIClient() (*c2mapi.APIClient, context.Context, error) {
    if err := c.ensureAuthenticated(); err != nil {
        return nil, nil, err
    }
    
    configuration := c2mapi.NewConfiguration()
    configuration.Host = "api.c2m.com"
    configuration.Scheme = "https"
    
    apiClient := c2mapi.NewAPIClient(configuration)
    auth := context.WithValue(context.Background(), c2mapi.ContextAccessToken, c.shortToken)
    
    return apiClient, auth, nil
}

func main() {
    client := NewC2MClient("your-client-id", "your-client-secret")
    
    apiClient, ctx, err := client.CreateAPIClient()
    if err != nil {
        log.Fatalf("Failed to create API client: %v", err)
    }
    
    // Submit job
    jobRequest := map[string]interface{}{
        "templateId":  "standard-letter",
        "documentUrl": "https://example.com/document.pdf",
    }
    
    resp, _, err := apiClient.DefaultApi.SubmitSingleDocWithTemplateParams(ctx).Body(jobRequest).Execute()
    if err != nil {
        log.Fatalf("Error submitting job: %v", err)
    }
    
    fmt.Printf("Job submitted: %v\n", resp)
}
EOF
            ;;
    esac
    
    if [ -n "$example_file" ] && [ -f "$example_file" ]; then
        print_success "Created JWT example: $example_file"
    fi
}

# Generate SDKs for all supported languages
generate_all_sdks() {
    local languages=("python" "javascript" "typescript" "java" "go" "ruby" "php" "csharp" "swift" "kotlin" "rust")
    local success_count=0
    local failed_languages=()
    
    print_info "Generating SDKs for all supported languages..."
    echo ""
    
    for lang in "${languages[@]}"; do
        local output_dir="$SDK_BASE_DIR/$lang"
        
        if generate_sdk "$lang" "$output_dir"; then
            ((success_count++))
        else
            failed_languages+=("$lang")
        fi
        
        echo "" # Add spacing between languages
    done
    
    # Summary
    echo "========================================"
    print_success "Successfully generated $success_count out of ${#languages[@]} SDKs"
    
    if [ ${#failed_languages[@]} -gt 0 ]; then
        print_warning "Failed languages: ${failed_languages[*]}"
    fi
}

# Interactive mode
interactive_mode() {
    print_info "C2M API SDK Generator - Interactive Mode"
    echo ""
    echo "Available languages:"
    echo "  1. python"
    echo "  2. javascript"
    echo "  3. typescript"
    echo "  4. java"
    echo "  5. go"
    echo "  6. ruby"
    echo "  7. php"
    echo "  8. csharp"
    echo "  9. swift"
    echo " 10. kotlin"
    echo " 11. rust"
    echo " 12. ALL (generate for all languages)"
    
    local langs=("python" "javascript" "typescript" "java" "go" "ruby" "php" "csharp" "swift" "kotlin" "rust")
    
    echo ""
    read -p "Select a language (1-12): " selection
    
    if [[ $selection -eq 12 ]]; then
        generate_all_sdks
        return
    fi
    
    if [[ $selection -lt 1 || $selection -gt 11 ]]; then
        print_error "Invalid selection"
        exit 1
    fi
    
    local selected_lang="${langs[$((selection-1))]}"
    local default_dir="$SDK_BASE_DIR/$selected_lang"
    
    echo ""
    read -p "Output directory [$default_dir]: " output_dir
    output_dir="${output_dir:-$default_dir}"
    
    generate_sdk "$selected_lang" "$output_dir"
}

# Main execution
main() {
    print_info "C2M API SDK Generator v2"
    echo ""
    
    # Check prerequisites
    check_openapi_spec
    check_openapi_generator
    
    # Parse command line arguments
    if [ $# -eq 0 ]; then
        interactive_mode
    elif [ "$1" = "all" ]; then
        generate_all_sdks
    elif [ $# -eq 1 ]; then
        generate_sdk "$1" "$SDK_BASE_DIR/$1"
    elif [ $# -eq 2 ]; then
        generate_sdk "$1" "$2"
    else
        echo "Usage: $0 [language] [output-dir]"
        echo "       $0 all"
        echo "       $0  # Interactive mode"
        exit 1
    fi
}

# Run main function
main "$@"