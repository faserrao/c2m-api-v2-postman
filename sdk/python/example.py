#!/usr/bin/env python3
"""
C2M API Python SDK Example
"""

import c2m_api
from c2m_api.rest import ApiException

# Configure API client
configuration = c2m_api.Configuration(
    host="https://api.c2m.com/v2",
    api_key={'Authorization': 'Bearer YOUR_API_KEY'}
)

# Create API client
with c2m_api.ApiClient(configuration) as api_client:
    # Create job instance
    jobs_api = c2m_api.JobsApi(api_client)
    
    try:
        # Create a single document job
        job_request = {
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
        
        # Submit job
        response = jobs_api.create_single_doc_job_template(job_request)
        print(f"Job created: {response.job_id}")
        
    except ApiException as e:
        print(f"Exception when calling JobsApi: {e}")
