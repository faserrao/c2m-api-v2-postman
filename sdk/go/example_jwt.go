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
