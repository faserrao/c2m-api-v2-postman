#!/usr/bin/env bash
# ========================================================================
# Documentation Deployment Script for C2M API
# ========================================================================
# Deploys API documentation to various hosting services
# 
# Usage:
#   ./deploy-docs.sh [target] [options]
#   
# Targets:
#   github-pages  - Deploy to GitHub Pages
#   s3           - Deploy to AWS S3
#   netlify      - Deploy to Netlify
#   local        - Start local preview server
#
# Examples:
#   ./deploy-docs.sh                    # Interactive mode
#   ./deploy-docs.sh github-pages       # Deploy to GitHub Pages
#   ./deploy-docs.sh s3 --bucket my-bucket
# ========================================================================

set -euo pipefail

# Configuration
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOCS_DIR="${PROJECT_ROOT}/docs"
DOCS_SITE_DIR="${DOCS_DIR}/site"
OPENAPI_SPEC="${PROJECT_ROOT}/openapi/c2mapiv2-openapi-spec-final.yaml"
BUILD_DIR="${PROJECT_ROOT}/_site"

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

# Check if documentation exists
check_docs() {
    if [ ! -f "${DOCS_DIR}/index.html" ]; then
        print_warning "Documentation not built. Building now..."
        cd "$PROJECT_ROOT"
        make docs
    fi
}

# Prepare documentation for deployment
prepare_docs() {
    print_info "Preparing documentation for deployment..."
    
    # Create build directory
    rm -rf "$BUILD_DIR"
    mkdir -p "$BUILD_DIR"
    
    # Copy documentation files
    cp -r "$DOCS_DIR"/* "$BUILD_DIR/"
    
    # Copy OpenAPI spec
    mkdir -p "$BUILD_DIR/openapi"
    cp "$OPENAPI_SPEC" "$BUILD_DIR/openapi/"
    cp "${PROJECT_ROOT}/openapi/bundled.yaml" "$BUILD_DIR/openapi/" 2>/dev/null || true
    
    # Create index page if not exists
    if [ ! -f "$BUILD_DIR/index.html" ]; then
        cat > "$BUILD_DIR/index.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>C2M API Documentation</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            line-height: 1.6;
        }
        .header { 
            text-align: center;
            padding: 2rem 0;
            border-bottom: 2px solid #e0e0e0;
            margin-bottom: 3rem;
        }
        .links {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }
        .link-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1.5rem;
            text-decoration: none;
            color: inherit;
            transition: all 0.2s;
        }
        .link-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .link-card h3 {
            margin-top: 0;
            color: #0066cc;
        }
        .version {
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>C2M API Documentation</h1>
        <p class="version">Version 2.0</p>
    </div>
    
    <h2>Available Documentation</h2>
    <div class="links">
        <a href="redoc.html" class="link-card">
            <h3>ReDoc Documentation</h3>
            <p>Interactive API reference documentation with a clean, responsive design</p>
        </a>
        
        <a href="swagger/index.html" class="link-card">
            <h3>Swagger UI</h3>
            <p>Interactive API explorer with built-in testing capabilities</p>
        </a>
        
        <a href="openapi/c2mapiv2-openapi-spec-final.yaml" class="link-card">
            <h3>OpenAPI Specification</h3>
            <p>Raw OpenAPI 3.0 specification file in YAML format</p>
        </a>
    </div>
    
    <h2>Quick Start</h2>
    <ol>
        <li>Get your API key from the C2M dashboard</li>
        <li>Review the authentication section in the documentation</li>
        <li>Try the template endpoints for quick integration</li>
        <li>Use the interactive Swagger UI to test endpoints</li>
    </ol>
    
    <h2>SDKs</h2>
    <p>Client SDKs are available for:</p>
    <ul>
        <li>Python</li>
        <li>JavaScript/TypeScript</li>
        <li>Java</li>
        <li>Go</li>
        <li>Ruby</li>
        <li>PHP</li>
    </ul>
    <p>Generate SDKs using <code>make generate-sdk</code></p>
</body>
</html>
EOF
    fi
    
    # Create .nojekyll for GitHub Pages
    touch "$BUILD_DIR/.nojekyll"
    
    print_success "Documentation prepared in: $BUILD_DIR"
}

# Deploy to GitHub Pages
deploy_github_pages() {
    print_info "Deploying to GitHub Pages..."
    
    # Check if gh-pages branch exists
    if ! git show-ref --quiet refs/heads/gh-pages; then
        print_info "Creating gh-pages branch..."
        git checkout --orphan gh-pages
        git reset --hard
        git commit --allow-empty -m "Initialize gh-pages branch"
        git checkout main
    fi
    
    # Use git worktree for deployment
    local PAGES_DIR="${PROJECT_ROOT}/_gh-pages"
    
    # Remove existing worktree if exists
    if [ -d "$PAGES_DIR" ]; then
        git worktree remove --force "$PAGES_DIR"
    fi
    
    # Add worktree for gh-pages
    git worktree add "$PAGES_DIR" gh-pages
    
    # Copy files to gh-pages
    rm -rf "$PAGES_DIR"/*
    cp -r "$BUILD_DIR"/* "$PAGES_DIR/"
    
    # Commit and push
    cd "$PAGES_DIR"
    git add -A
    
    if git diff --cached --quiet; then
        print_warning "No changes to deploy"
    else
        git commit -m "Deploy documentation $(date +'%Y-%m-%d %H:%M:%S')"
        git push origin gh-pages
        print_success "Documentation deployed to GitHub Pages!"
        print_info "URL: https://$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/').github.io/$(basename $(git rev-parse --show-toplevel))/"
    fi
    
    # Cleanup
    cd "$PROJECT_ROOT"
    git worktree remove "$PAGES_DIR"
}

# Deploy to AWS S3
deploy_s3() {
    local bucket="${1:-}"
    
    if [ -z "$bucket" ]; then
        read -p "S3 bucket name: " bucket
    fi
    
    print_info "Deploying to S3 bucket: $bucket..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found. Please install it first:"
        echo "  brew install awscli"
        echo "  OR"
        echo "  pip install awscli"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
    
    # Sync to S3
    aws s3 sync "$BUILD_DIR" "s3://$bucket" \
        --delete \
        --exclude ".git/*" \
        --exclude ".DS_Store" \
        --acl public-read
    
    # Set proper content types
    aws s3 cp "s3://$bucket" "s3://$bucket" \
        --recursive \
        --exclude "*" \
        --include "*.html" \
        --acl public-read \
        --content-type "text/html" \
        --metadata-directive REPLACE
    
    aws s3 cp "s3://$bucket" "s3://$bucket" \
        --recursive \
        --exclude "*" \
        --include "*.yaml" \
        --include "*.yml" \
        --acl public-read \
        --content-type "text/yaml" \
        --metadata-directive REPLACE
    
    print_success "Documentation deployed to S3!"
    print_info "URL: http://$bucket.s3-website-$(aws configure get region).amazonaws.com/"
}

# Deploy to Netlify
deploy_netlify() {
    print_info "Deploying to Netlify..."
    
    # Check if netlify CLI is installed
    if ! command -v netlify &> /dev/null; then
        print_warning "Netlify CLI not found. Installing..."
        npm install -g netlify-cli
    fi
    
    # Deploy
    netlify deploy --dir="$BUILD_DIR" --prod
    
    print_success "Documentation deployed to Netlify!"
}

# Start local preview server
start_local_server() {
    local port="${1:-8000}"
    
    print_info "Starting local documentation server on port $port..."
    print_info "URL: http://localhost:$port"
    
    cd "$BUILD_DIR"
    
    # Try Python 3 first
    if command -v python3 &> /dev/null; then
        python3 -m http.server "$port"
    # Try Python 2
    elif command -v python &> /dev/null; then
        python -m SimpleHTTPServer "$port"
    # Try Node.js http-server
    elif command -v npx &> /dev/null; then
        npx http-server -p "$port"
    else
        print_error "No suitable web server found. Install Python or Node.js."
        exit 1
    fi
}

# Interactive mode
interactive_mode() {
    print_info "C2M API Documentation Deployment - Interactive Mode"
    echo ""
    echo "Deployment targets:"
    echo "  1. GitHub Pages"
    echo "  2. AWS S3"
    echo "  3. Netlify"
    echo "  4. Local Preview"
    echo ""
    read -p "Select target (1-4): " selection
    
    case $selection in
        1) deploy_github_pages ;;
        2) deploy_s3 ;;
        3) deploy_netlify ;;
        4) start_local_server ;;
        *) print_error "Invalid selection"; exit 1 ;;
    esac
}

# Main execution
main() {
    print_info "C2M API Documentation Deployment"
    echo ""
    
    # Check and prepare documentation
    check_docs
    prepare_docs
    
    # Parse arguments
    case "${1:-}" in
        "github-pages")
            deploy_github_pages
            ;;
        "s3")
            deploy_s3 "${2:-}"
            ;;
        "netlify")
            deploy_netlify
            ;;
        "local")
            start_local_server "${2:-8000}"
            ;;
        "")
            interactive_mode
            ;;
        *)
            print_error "Unknown target: $1"
            echo "Usage: $0 [github-pages|s3|netlify|local]"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"