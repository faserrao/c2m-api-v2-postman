#!/usr/bin/env bash
# ========================================================================
# SDK Generator for C2M API
# ========================================================================
# Generates client SDKs in multiple languages using OpenAPI Generator
# 
# Usage:
#   ./generate-sdk.sh [language] [output-dir]
#   
# Examples:
#   ./generate-sdk.sh                    # Interactive mode
#   ./generate-sdk.sh python             # Generate Python SDK
#   ./generate-sdk.sh python sdk/python  # Generate Python SDK in specific dir
#
# Supported languages: python, javascript, typescript, java, go, ruby, php
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
if [ ! -f "$OPENAPI_SPEC" ]; then
    print_error "OpenAPI specification not found: $OPENAPI_SPEC"
    print_info "Run 'make openapi-build' to generate the specification first"
    exit 1
fi

# Check if openapi-generator is installed
check_openapi_generator() {
    if ! command -v openapi-generator-cli &> /dev/null; then
        print_warning "OpenAPI Generator CLI not found. Installing..."
        
        # Check if npm is available
        if command -v npm &> /dev/null; then
            if [ "$OPENAPI_GENERATOR_VERSION" = "latest" ]; then
                npm install -g @openapitools/openapi-generator-cli
            else
                npm install -g @openapitools/openapi-generator-cli@${OPENAPI_GENERATOR_VERSION}
            fi
        else
            print_error "npm not found. Please install Node.js first or install OpenAPI Generator manually:"
            echo "  brew install openapi-generator"
            echo "  OR"
            echo "  npm install -g @openapitools/openapi-generator-cli"
            exit 1
        fi
    fi
}

# Function to get language configuration
get_language_config() {
    local lang=$1
    case $lang in
        "python")
            echo "python --package-name c2m_api"
            ;;
        "javascript")
            echo "javascript --project-name c2m-api-js"
            ;;
        "typescript")
            echo "typescript-axios --npm-name c2m-api-ts --npm-version 1.0.0"
            ;;
        "java")
            echo "java --artifact-id c2m-api --group-id com.c2m --api-package com.c2m.api --model-package com.c2m.model"
            ;;
        "go")
            echo "go --package-name c2mapi"
            ;;
        "ruby")
            echo "ruby --gem-name c2m_api"
            ;;
        "php")
            echo "php --package-name C2M\\Api"
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
    
    # Get language configuration
    local config=$(get_language_config "$language")
    if [ $? -ne 0 ]; then
        print_error "Unsupported language: $language"
        echo "Supported languages: python, javascript, typescript, java, go, ruby, php"
        exit 1
    fi
    
    print_info "Generating $language SDK..."
    
    # Create output directory
    mkdir -p "$output_dir"
    
    # Add common configurations
    local common_config="--git-user-id c2m --git-repo-id c2m-api-$language"
    
    # Build the command
    local cmd="openapi-generator-cli generate -i $OPENAPI_SPEC -g $config -o $output_dir $common_config"
    
    print_info "Running: openapi-generator-cli generate -g $config ..."
    
    if eval $cmd; then
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
                print_info "Installing npm dependencies..."
                cd "$output_dir" && npm install
                ;;
        esac
        
        # Create basic usage example
        create_usage_example "$language" "$output_dir"
        
    else
        print_error "Failed to generate SDK"
        exit 1
    fi
}

# Function to create usage examples
create_usage_example() {
    local language=$1
    local output_dir=$2
    local example_file=""
    
    case $language in
        "python")
            example_file="$output_dir/example.py"
            cat > "$example_file" << 'EOF'
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
EOF
            ;;
            
        "javascript")
            example_file="$output_dir/example.js"
            cat > "$example_file" << 'EOF'
/**
 * C2M API JavaScript SDK Example
 */

const C2mApi = require('c2m-api-js');

// Configure API client
const defaultClient = C2mApi.ApiClient.instance;
const bearerAuth = defaultClient.authentications['bearerAuth'];
bearerAuth.accessToken = 'YOUR_API_KEY';

// Set the base URL
defaultClient.basePath = 'https://api.c2m.com/v2';

// Create API instance
const jobsApi = new C2mApi.JobsApi();

// Create a job
const jobRequest = {
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

jobsApi.createSingleDocJobTemplate(jobRequest).then((response) => {
    console.log('Job created:', response.jobId);
}).catch((error) => {
    console.error('Error:', error);
});
EOF
            ;;
            
        "typescript")
            example_file="$output_dir/example.ts"
            cat > "$example_file" << 'EOF'
/**
 * C2M API TypeScript SDK Example
 */

import { Configuration, JobsApi } from 'c2m-api-ts';

// Configure API client
const configuration = new Configuration({
    basePath: 'https://api.c2m.com/v2',
    accessToken: 'YOUR_API_KEY'
});

// Create API instance
const jobsApi = new JobsApi(configuration);

// Create a job
async function createJob() {
    try {
        const jobRequest = {
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
        
        const response = await jobsApi.createSingleDocJobTemplate(jobRequest);
        console.log('Job created:', response.data.jobId);
    } catch (error) {
        console.error('Error:', error);
    }
}

createJob();
EOF
            ;;
    esac
    
    if [ -n "$example_file" ]; then
        print_success "Created example file: $example_file"
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
    
    local langs=("python" "javascript" "typescript" "java" "go" "ruby" "php")
    
    echo ""
    read -p "Select a language (1-7): " selection
    
    if [[ $selection -lt 1 || $selection -gt 7 ]]; then
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
    print_info "C2M API SDK Generator"
    echo ""
    
    # Check OpenAPI Generator
    check_openapi_generator
    
    # Parse arguments
    if [ $# -eq 0 ]; then
        # Interactive mode
        interactive_mode
    elif [ $# -eq 1 ]; then
        # Language specified, use default directory
        local language=$1
        local output_dir="$SDK_BASE_DIR/$language"
        generate_sdk "$language" "$output_dir"
    elif [ $# -eq 2 ]; then
        # Language and directory specified
        generate_sdk "$1" "$2"
    else
        print_error "Invalid arguments"
        echo "Usage: $0 [language] [output-dir]"
        echo "Supported languages: python, javascript, typescript, java, go, ruby, php"
        exit 1
    fi
    
    echo ""
    print_success "SDK generation complete!"
    echo ""
    echo "Next steps:"
    echo "1. Review the generated SDK in the output directory"
    echo "2. Check the example file for usage patterns"
    echo "3. Run tests if available"
    echo "4. Publish to package repository (PyPI, npm, etc.)"
}

# Run main function
main "$@"