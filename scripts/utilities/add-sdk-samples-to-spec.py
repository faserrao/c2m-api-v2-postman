#!/usr/bin/env python3
"""
Add SDK code samples to OpenAPI specification for Redoc documentation.
This script adds x-codeSamples to each endpoint with examples in multiple languages.
"""

import yaml
import json
import sys
from pathlib import Path

# SDK Language configurations
SDK_LANGUAGES = {
    'curl': {'label': 'cURL', 'lang': 'bash'},
    'python': {'label': 'Python', 'lang': 'python'},
    'javascript': {'label': 'JavaScript', 'lang': 'javascript'},
    'typescript': {'label': 'TypeScript', 'lang': 'typescript'},
    'java': {'label': 'Java', 'lang': 'java'},
    'csharp': {'label': 'C#', 'lang': 'csharp'},
    'go': {'label': 'Go', 'lang': 'go'},
    'ruby': {'label': 'Ruby', 'lang': 'ruby'},
    'php': {'label': 'PHP', 'lang': 'php'},
}

def generate_curl_sample(method, path, operation_id, parameters, request_body):
    """Generate cURL sample"""
    url = f"https://api.c2m.com/v2{path}"
    
    # Replace path parameters
    if parameters:
        for param in parameters:
            if param.get('in') == 'path':
                placeholder = f"{{{param['name']}}}"
                value = f"<{param['name']}>"
                url = url.replace(placeholder, value)
    
    curl_parts = [
        f"curl -X {method.upper()}",
        f'  "{url}"',
        '  -H "Authorization: Bearer <your-jwt-token>"',
        '  -H "Content-Type: application/json"'
    ]
    
    if request_body and method.upper() in ['POST', 'PUT', 'PATCH']:
        curl_parts.append("  -d '{}'")
    
    return ' \\\n'.join(curl_parts)

def generate_python_sample(method, path, operation_id, parameters, request_body):
    """Generate Python sample using requests"""
    path_with_params = path
    path_params = []
    
    if parameters:
        for param in parameters:
            if param.get('in') == 'path':
                path_params.append(param['name'])
                path_with_params = path_with_params.replace(f"{{{param['name']}}}", f"{{{param['name']}}}")
    
    sample = f'''import requests

url = f"https://api.c2m.com/v2{path_with_params}"
headers = {{
    "Authorization": "Bearer <your-jwt-token>",
    "Content-Type": "application/json"
}}'''
    
    if request_body and method.upper() in ['POST', 'PUT', 'PATCH']:
        sample += '\n\ndata = {\n    # Add your request body here\n}'
        sample += f'\n\nresponse = requests.{method.lower()}(url, headers=headers, json=data)'
    else:
        sample += f'\n\nresponse = requests.{method.lower()}(url, headers=headers)'
    
    sample += '\nprint(response.json())'
    
    return sample

def generate_javascript_sample(method, path, operation_id, parameters, request_body):
    """Generate JavaScript sample using fetch"""
    path_with_params = path
    
    if parameters:
        for param in parameters:
            if param.get('in') == 'path':
                path_with_params = path_with_params.replace(f"{{{param['name']}}}", f"${{{param['name']}}}")
    
    sample = f'''const url = `https://api.c2m.com/v2{path_with_params}`;
const headers = {{
    'Authorization': 'Bearer <your-jwt-token>',
    'Content-Type': 'application/json'
}};'''
    
    if request_body and method.upper() in ['POST', 'PUT', 'PATCH']:
        sample += '''

const data = {
    // Add your request body here
};

const response = await fetch(url, {
    method: '%s',
    headers: headers,
    body: JSON.stringify(data)
});''' % method.upper()
    else:
        sample += f'''

const response = await fetch(url, {{
    method: '{method.upper()}',
    headers: headers
}});'''
    
    sample += '\n\nconst result = await response.json();\nconsole.log(result);'
    
    return sample

def generate_java_sample(method, path, operation_id, parameters, request_body):
    """Generate Java sample"""
    sample = '''import com.c2m.ApiClient;
import com.c2m.ApiException;
import com.c2m.Configuration;
import com.c2m.auth.*;
import com.c2m.api.*;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        
        // Configure Bearer token
        HttpBearerAuth bearer = (HttpBearerAuth) defaultClient.getAuthentication("bearerAuth");
        bearer.setBearerToken("<your-jwt-token>");
        
        DefaultApi apiInstance = new DefaultApi(defaultClient);
        
        try {
            // Call the API
            var result = apiInstance.%s();
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling API");
            e.printStackTrace();
        }
    }
}''' % (operation_id or 'apiCall')
    
    return sample

def generate_csharp_sample(method, path, operation_id, parameters, request_body):
    """Generate C# sample"""
    sample = '''using System;
using C2M.Api;
using C2M.Client;
using C2M.Model;

namespace Example
{
    public class Program
    {
        public static void Main()
        {
            Configuration config = new Configuration();
            config.AccessToken = "<your-jwt-token>";
            
            var apiInstance = new DefaultApi(config);
            
            try
            {
                // Call the API
                var result = apiInstance.%s();
                Console.WriteLine(result);
            }
            catch (ApiException e)
            {
                Console.WriteLine("Exception: " + e.Message);
                Console.WriteLine("Status Code: " + e.ErrorCode);
            }
        }
    }
}''' % (operation_id or 'ApiCall')
    
    return sample

def generate_go_sample(method, path, operation_id, parameters, request_body):
    """Generate Go sample"""
    path_formatted = path
    if parameters:
        for param in parameters:
            if param.get('in') == 'path':
                path_formatted = path_formatted.replace(f"{{{param['name']}}}", f"%s")
    
    sample = '''package main

import (
    "context"
    "fmt"
    "github.com/c2m/go-sdk"
)

func main() {
    cfg := c2m.NewConfiguration()
    cfg.AddDefaultHeader("Authorization", "Bearer <your-jwt-token>")
    
    client := c2m.NewAPIClient(cfg)
    ctx := context.Background()
    
    resp, r, err := client.DefaultApi.%s(ctx).Execute()
    if err != nil {
        fmt.Printf("Error: %%v\\n", err)
        return
    }
    
    fmt.Printf("Response: %%v\\n", resp)
}''' % (operation_id or 'ApiCall')
    
    return sample

def add_code_samples_to_spec(input_file, output_file):
    """Add x-codeSamples to each endpoint in the OpenAPI spec"""
    
    # Read the OpenAPI spec
    with open(input_file, 'r') as f:
        spec = yaml.safe_load(f)
    
    # Process each path and method
    if 'paths' in spec:
        for path, path_item in spec['paths'].items():
            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'patch', 'delete']:
                    # Skip if already has code samples
                    if 'x-codeSamples' in operation:
                        continue
                    
                    # Get operation details
                    operation_id = operation.get('operationId', '')
                    parameters = operation.get('parameters', [])
                    request_body = operation.get('requestBody')
                    
                    # Generate code samples
                    code_samples = []
                    
                    # cURL
                    code_samples.append({
                        'lang': 'curl',
                        'label': 'cURL',
                        'source': generate_curl_sample(method, path, operation_id, parameters, request_body)
                    })
                    
                    # Python
                    code_samples.append({
                        'lang': 'python',
                        'label': 'Python',
                        'source': generate_python_sample(method, path, operation_id, parameters, request_body)
                    })
                    
                    # JavaScript
                    code_samples.append({
                        'lang': 'javascript',
                        'label': 'JavaScript',
                        'source': generate_javascript_sample(method, path, operation_id, parameters, request_body)
                    })
                    
                    # Java
                    code_samples.append({
                        'lang': 'java',
                        'label': 'Java',
                        'source': generate_java_sample(method, path, operation_id, parameters, request_body)
                    })
                    
                    # C#
                    code_samples.append({
                        'lang': 'csharp',
                        'label': 'C#',
                        'source': generate_csharp_sample(method, path, operation_id, parameters, request_body)
                    })
                    
                    # Go
                    code_samples.append({
                        'lang': 'go',
                        'label': 'Go',
                        'source': generate_go_sample(method, path, operation_id, parameters, request_body)
                    })
                    
                    # Add to operation
                    operation['x-codeSamples'] = code_samples
    
    # Write the updated spec
    with open(output_file, 'w') as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, width=120)
    
    print(f"✅ Added code samples to {output_file}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python add-sdk-samples-to-spec.py <input-spec> <output-spec>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    add_code_samples_to_spec(input_file, output_file)