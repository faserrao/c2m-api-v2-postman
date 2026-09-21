#!/usr/bin/env python3
"""
Add SDK code samples to OpenAPI specification for Redoc documentation.
This script adds x-codeSamples to each endpoint with examples in multiple languages.
"""

import argparse
import yaml
import json
import sys
from pathlib import Path

# Redoc x-codeSamples lang identifier differs from slug for some entries.
_SLUG_TO_REDOC_LANG: dict = {
    'curl': 'bash',  # cURL displayed with bash syntax highlighting in Redoc
}

# SDK Language configurations — fallback when --sdk-langs is not provided.
# Primary source of truth: config/sdk-languages.yaml (also drives generate-sdk-v2.sh
# and generate_artifacts_index.py).  Update that file to add new SDK languages;
# pass --sdk-langs to this script so the change propagates to Redoc x-codeSamples.
SDK_LANGUAGES = {
    'curl':       {'label': 'cURL',       'lang': 'bash'},
    'python':     {'label': 'Python',     'lang': 'python'},
    'javascript': {'label': 'JavaScript', 'lang': 'javascript'},
    'typescript': {'label': 'TypeScript', 'lang': 'typescript'},
    'java':       {'label': 'Java',       'lang': 'java'},
    'csharp':     {'label': 'C#',         'lang': 'csharp'},
    'go':         {'label': 'Go',         'lang': 'go'},
    'ruby':       {'label': 'Ruby',       'lang': 'ruby'},
    'php':        {'label': 'PHP',        'lang': 'php'},
    'swift':      {'label': 'Swift',      'lang': 'swift'},
    'kotlin':     {'label': 'Kotlin',     'lang': 'kotlin'},
    'rust':       {'label': 'Rust',       'lang': 'rust'},
}

def generate_curl_sample(method, path, operation_id, parameters, request_body, server_url):
    """Generate cURL sample"""
    url = f"{server_url}{path}"
    
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

def generate_python_sample(method, path, operation_id, parameters, request_body, server_url):
    """Generate Python sample using requests"""
    path_with_params = path
    path_params = []

    if parameters:
        for param in parameters:
            if param.get('in') == 'path':
                path_params.append(param['name'])
                path_with_params = path_with_params.replace(f"{{{param['name']}}}", f"{{{param['name']}}}")

    sample = f'''import requests

url = f"{server_url}{path_with_params}"
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

def generate_javascript_sample(method, path, operation_id, parameters, request_body, server_url):
    """Generate JavaScript sample using fetch"""
    path_with_params = path

    if parameters:
        for param in parameters:
            if param.get('in') == 'path':
                path_with_params = path_with_params.replace(f"{{{param['name']}}}", f"${{{param['name']}}}")

    sample = f'''const url = `{server_url}{path_with_params}`;
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

def generate_java_sample(method, path, operation_id, parameters, request_body, server_url):
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

def generate_csharp_sample(method, path, operation_id, parameters, request_body, server_url):
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

def generate_go_sample(method, path, operation_id, parameters, request_body, server_url):
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

def generate_swift_sample(method, path, operation_id, parameters, request_body, server_url):
    """Generate Swift sample using URLSession"""
    url = f"{server_url}{path}"
    if parameters:
        for param in parameters:
            if param.get('in') == 'path':
                url = url.replace(f"{{{param['name']}}}", f"\\(<{param['name']}>)")

    sample = f'''import Foundation

let url = URL(string: "{url}")!
var request = URLRequest(url: url)
request.httpMethod = "{method.upper()}"
request.setValue("Bearer <your-jwt-token>", forHTTPHeaderField: "Authorization")
request.setValue("application/json", forHTTPHeaderField: "Content-Type")'''

    if request_body and method.upper() in ['POST', 'PUT', 'PATCH']:
        sample += '''

let body: [String: Any] = [
    // Add your request body here
]
request.httpBody = try? JSONSerialization.data(withJSONObject: body)'''

    sample += '''

let task = URLSession.shared.dataTask(with: request) { data, response, error in
    if let data = data,
       let json = try? JSONSerialization.jsonObject(with: data) {
        print(json)
    }
}
task.resume()'''
    return sample


def generate_kotlin_sample(method, path, operation_id, parameters, request_body, server_url):
    """Generate Kotlin sample using OkHttp"""
    url = f"{server_url}{path}"
    if parameters:
        for param in parameters:
            if param.get('in') == 'path':
                url = url.replace(f"{{{param['name']}}}", f"${{{param['name']}}}")

    sample = f'''import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody

val client = OkHttpClient()
val url = "{url}"'''

    if request_body and method.upper() in ['POST', 'PUT', 'PATCH']:
        sample += '''

val body = """
    {{
        // Add your request body here
    }}
""".trimIndent().toRequestBody("application/json".toMediaType())

val request = Request.Builder()
    .url(url)
    .addHeader("Authorization", "Bearer <your-jwt-token>")
    .addHeader("Content-Type", "application/json")
    .%s(body)
    .build()''' % method.lower()
    else:
        sample += '''

val request = Request.Builder()
    .url(url)
    .addHeader("Authorization", "Bearer <your-jwt-token>")
    .get()
    .build()'''

    sample += '''

val response = client.newCall(request).execute()
println(response.body?.string())'''
    return sample


def generate_rust_sample(method, path, operation_id, parameters, request_body, server_url):
    """Generate Rust sample using reqwest"""
    url = f"{server_url}{path}"
    if parameters:
        for param in parameters:
            if param.get('in') == 'path':
                url = url.replace(f"{{{param['name']}}}", f"{{{param['name']}}}")

    sample = f'''use reqwest::header;
use serde_json::json;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {{
    let client = reqwest::Client::new();
    let url = "{url}";'''

    if request_body and method.upper() in ['POST', 'PUT', 'PATCH']:
        sample += '''

    let body = json!({{
        // Add your request body here
    }});

    let response = client
        .{method}(url)
        .header(header::AUTHORIZATION, "Bearer <your-jwt-token>")
        .header(header::CONTENT_TYPE, "application/json")
        .json(&body)
        .send()
        .await?;'''.format(method=method.lower())
    else:
        sample += f'''

    let response = client
        .{method.lower()}(url)
        .header(header::AUTHORIZATION, "Bearer <your-jwt-token>")
        .send()
        .await?;'''

    sample += '''

    let result: serde_json::Value = response.json().await?;
    println!("{:#?}", result);
    Ok(())
}'''
    return sample


def _load_sdk_langs(sdk_langs_path: str | None) -> dict:
    """Load SDK language config from sdk-languages.yaml. Falls back to SDK_LANGUAGES.

    curl is always prepended as the first entry (it is a code sample format, not a
    generated SDK, so it is not listed in sdk-languages.yaml).
    """
    if sdk_langs_path:
        try:
            with open(sdk_langs_path) as f:
                data = yaml.safe_load(f)
            langs: dict = {'curl': {'label': 'cURL', 'lang': 'bash'}}
            for entry in data.get('languages', []):
                slug = entry['slug']
                langs[slug] = {
                    'label': entry['label'],
                    'lang': _SLUG_TO_REDOC_LANG.get(slug, slug),
                }
            print(f"Loaded {len(langs)} SDK language(s) from {sdk_langs_path}")
            return langs
        except Exception as exc:
            print(f"⚠️  Could not load sdk-languages.yaml '{sdk_langs_path}': {exc} — using built-in list", file=sys.stderr)
    return SDK_LANGUAGES


_GENERATOR_MAP = {
    'curl':       generate_curl_sample,
    'python':     generate_python_sample,
    'javascript': generate_javascript_sample,
    'java':       generate_java_sample,
    'csharp':     generate_csharp_sample,
    'go':         generate_go_sample,
    'swift':      generate_swift_sample,
    'kotlin':     generate_kotlin_sample,
    'rust':       generate_rust_sample,
}


def add_code_samples_to_spec(input_file, output_file, sdk_langs: dict | None = None):
    """Add x-codeSamples to each endpoint in the OpenAPI spec"""
    langs = sdk_langs if sdk_langs is not None else SDK_LANGUAGES

    with open(input_file, 'r') as f:
        spec = yaml.safe_load(f)

    # Read server URL from spec so samples stay correct if the hostname ever changes.
    server_url = spec.get('servers', [{}])[0].get('url', 'https://api.click2mail.com/v2').rstrip('/')

    if 'paths' in spec:
        for path, path_item in spec['paths'].items():
            for method, operation in path_item.items():
                if method not in ['get', 'post', 'put', 'patch', 'delete']:
                    continue
                if 'x-codeSamples' in operation:
                    continue

                operation_id = operation.get('operationId', '')
                parameters = operation.get('parameters', [])
                request_body = operation.get('requestBody')

                code_samples = []
                for lang_key, lang_meta in langs.items():
                    generator = _GENERATOR_MAP.get(lang_key)
                    if generator:
                        code_samples.append({
                            'lang': lang_meta['lang'],
                            'label': lang_meta['label'],
                            'source': generator(method, path, operation_id, parameters, request_body, server_url),
                        })

                operation['x-codeSamples'] = code_samples

    with open(output_file, 'w') as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, width=120)

    print(f"✅ Added code samples to {output_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_spec', help='Path to input OpenAPI YAML spec')
    parser.add_argument('output_spec', help='Path to write output OpenAPI YAML spec')
    parser.add_argument(
        '--sdk-langs',
        metavar='PATH',
        default=None,
        help='Path to config/sdk-languages.yaml (single source of truth for SDK language list). '
             'If omitted, falls back to the built-in SDK_LANGUAGES dict.',
    )
    args = parser.parse_args()

    sdk_langs = _load_sdk_langs(args.sdk_langs)
    add_code_samples_to_spec(args.input_spec, args.output_spec, sdk_langs=sdk_langs)