/**
 * C2M API Rust SDK Example with JWT Authentication
 */

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{Duration, SystemTime};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use reqwest::{Client, StatusCode};
use tokio;

#[derive(Debug, Serialize)]
struct LongTokenRequest {
    grant_type: String,
    client_id: String,
    client_secret: String,
    scopes: Vec<String>,
    ttl_seconds: u32,
}

#[derive(Debug, Serialize)]
struct ShortTokenRequest {
    scopes: Vec<String>,
}

#[derive(Debug, Deserialize)]
struct TokenResponse {
    access_token: String,
    token_id: String,
    expires_at: String,
}

pub struct C2MClient {
    client_id: String,
    client_secret: String,
    base_url: String,
    http_client: Client,
    long_token: Arc<Mutex<Option<String>>>,
    short_token: Arc<Mutex<Option<String>>>,
    token_expiry: Arc<Mutex<Option<DateTime<Utc>>>>,
}

impl C2MClient {
    pub fn new(client_id: String, client_secret: String) -> Self {
        Self::with_base_url(client_id, client_secret, "https://api.c2m.com/v2".to_string())
    }
    
    pub fn with_base_url(client_id: String, client_secret: String, base_url: String) -> Self {
        C2MClient {
            client_id,
            client_secret,
            base_url,
            http_client: Client::builder()
                .timeout(Duration::from_secs(30))
                .build()
                .expect("Failed to create HTTP client"),
            long_token: Arc::new(Mutex::new(None)),
            short_token: Arc::new(Mutex::new(None)),
            token_expiry: Arc::new(Mutex::new(None)),
        }
    }
    
    async fn get_long_token(&self) -> Result<String, Box<dyn std::error::Error>> {
        let request_body = LongTokenRequest {
            grant_type: "client_credentials".to_string(),
            client_id: self.client_id.clone(),
            client_secret: self.client_secret.clone(),
            scopes: vec![
                "jobs:submit".to_string(),
                "jobs:read".to_string(),
                "templates:read".to_string(),
            ],
            ttl_seconds: 2592000, // 30 days
        };
        
        let response = self.http_client
            .post(&format!("{}/auth/tokens/long", self.base_url))
            .json(&request_body)
            .send()
            .await?;
        
        if !response.status().is_success() {
            return Err(format!("Failed to get long token: {}", response.status()).into());
        }
        
        let token_response: TokenResponse = response.json().await?;
        
        let token = token_response.access_token.clone();
        *self.long_token.lock().unwrap() = Some(token.clone());
        
        println!("Long-term token obtained: {}", token_response.token_id);
        Ok(token)
    }
    
    async fn get_short_token(&self) -> Result<String, Box<dyn std::error::Error>> {
        let long_token = {
            let token_guard = self.long_token.lock().unwrap();
            match &*token_guard {
                Some(token) => token.clone(),
                None => {
                    drop(token_guard);
                    self.get_long_token().await?
                }
            }
        };
        
        let request_body = ShortTokenRequest {
            scopes: vec!["jobs:submit".to_string()],
        };
        
        let response = self.http_client
            .post(&format!("{}/auth/tokens/short", self.base_url))
            .header("Authorization", format!("Bearer {}", long_token))
            .json(&request_body)
            .send()
            .await?;
        
        if !response.status().is_success() {
            return Err(format!("Failed to get short token: {}", response.status()).into());
        }
        
        let token_response: TokenResponse = response.json().await?;
        
        let token = token_response.access_token.clone();
        let expiry = DateTime::parse_from_rfc3339(&token_response.expires_at)?
            .with_timezone(&Utc);
        
        *self.short_token.lock().unwrap() = Some(token.clone());
        *self.token_expiry.lock().unwrap() = Some(expiry);
        
        println!("Short-term token obtained: {}", token_response.token_id);
        Ok(token)
    }
    
    async fn ensure_authenticated(&self) -> Result<String, Box<dyn std::error::Error>> {
        let now = Utc::now();
        let buffer = chrono::Duration::minutes(1);
        
        let needs_refresh = {
            let token_guard = self.short_token.lock().unwrap();
            let expiry_guard = self.token_expiry.lock().unwrap();
            
            token_guard.is_none() || 
            expiry_guard.is_none() || 
            now + buffer >= expiry_guard.unwrap()
        };
        
        if needs_refresh {
            self.get_short_token().await
        } else {
            Ok(self.short_token.lock().unwrap().as_ref().unwrap().clone())
        }
    }
    
    pub async fn submit_job(
        &self, 
        job_params: HashMap<String, serde_json::Value>
    ) -> Result<serde_json::Value, Box<dyn std::error::Error>> {
        let token = self.ensure_authenticated().await?;
        
        let response = self.http_client
            .post(&format!("{}/jobs/submit-single-doc-with-template", self.base_url))
            .header("Authorization", format!("Bearer {}", token))
            .json(&job_params)
            .send()
            .await?;
        
        match response.status() {
            StatusCode::UNAUTHORIZED | StatusCode::FORBIDDEN => {
                // Token expired, refresh and retry
                *self.short_token.lock().unwrap() = None;
                let new_token = self.ensure_authenticated().await?;
                
                let retry_response = self.http_client
                    .post(&format!("{}/jobs/submit-single-doc-with-template", self.base_url))
                    .header("Authorization", format!("Bearer {}", new_token))
                    .json(&job_params)
                    .send()
                    .await?;
                
                if !retry_response.status().is_success() {
                    return Err(format!("Request failed: {}", retry_response.status()).into());
                }
                
                Ok(retry_response.json().await?)
            }
            _ if response.status().is_success() => {
                Ok(response.json().await?)
            }
            _ => {
                Err(format!("Request failed: {}", response.status()).into())
            }
        }
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = C2MClient::new(
        "your-client-id".to_string(),
        "your-client-secret".to_string()
    );
    
    let mut job_params = HashMap::new();
    job_params.insert("templateId".to_string(), serde_json::json!("standard-letter"));
    job_params.insert("documentUrl".to_string(), serde_json::json!("https://example.com/document.pdf"));
    job_params.insert("recipients".to_string(), serde_json::json!([{
        "name": "John Doe",
        "address": {
            "line1": "123 Main St",
            "city": "New York",
            "state": "NY",
            "zip": "10001"
        }
    }]));
    
    match client.submit_job(job_params).await {
        Ok(result) => println!("Job submitted: {:?}", result),
        Err(e) => eprintln!("Error: {}", e),
    }
    
    Ok(())
}

// Add to Cargo.toml dependencies:
// [dependencies]
// tokio = { version = "1", features = ["full"] }
// reqwest = { version = "0.11", features = ["json"] }
// serde = { version = "1.0", features = ["derive"] }
// serde_json = "1.0"
// chrono = { version = "0.4", features = ["serde"] }