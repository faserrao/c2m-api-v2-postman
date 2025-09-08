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
