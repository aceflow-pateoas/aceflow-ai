#!/bin/bash
# AceFlow MCP Unified Server Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VERSION="2.0.0"
DOCKER_IMAGE="aceflow/mcp-server:${VERSION}"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check pip
    if ! command -v pip &> /dev/null; then
        log_error "pip is required but not installed"
        exit 1
    fi
    
    log_success "Dependencies check passed"
}

build_package() {
    log_info "Building Python package..."
    
    cd "$PROJECT_DIR"
    
    # Clean previous builds
    rm -rf build/ dist/ *.egg-info/
    
    # Install build dependencies
    pip install --upgrade build twine
    
    # Build package
    python -m build
    
    log_success "Package built successfully"
}

test_package() {
    log_info "Testing package installation..."
    
    cd "$PROJECT_DIR"
    
    # Create virtual environment for testing
    python -m venv test_env
    source test_env/bin/activate
    
    # Install package
    pip install dist/*.whl
    
    # Test basic functionality
    aceflow-unified --version
    aceflow-unified test health
    
    # Cleanup
    deactivate
    rm -rf test_env
    
    log_success "Package testing completed"
}

build_docker() {
    log_info "Building Docker image..."
    
    cd "$PROJECT_DIR"
    
    # Build Docker image
    docker build -t "$DOCKER_IMAGE" .
    docker tag "$DOCKER_IMAGE" "aceflow/mcp-server:latest"
    
    log_success "Docker image built: $DOCKER_IMAGE"
}

test_docker() {
    log_info "Testing Docker image..."
    
    # Run container for testing
    CONTAINER_ID=$(docker run -d -p 8080:8080 "$DOCKER_IMAGE")
    
    # Wait for container to start
    sleep 10
    
    # Test health endpoint
    if docker exec "$CONTAINER_ID" aceflow-unified test health; then
        log_success "Docker image test passed"
    else
        log_error "Docker image test failed"
        docker logs "$CONTAINER_ID"
        docker stop "$CONTAINER_ID"
        docker rm "$CONTAINER_ID"
        exit 1
    fi
    
    # Cleanup
    docker stop "$CONTAINER_ID"
    docker rm "$CONTAINER_ID"
}

deploy_local() {
    log_info "Deploying locally..."
    
    cd "$PROJECT_DIR"
    
    # Install package in development mode
    pip install -e ".[dev]"
    
    # Create configuration directory
    mkdir -p ~/.aceflow
    
    # Copy example configuration
    if [ ! -f ~/.aceflow/config.json ]; then
        cp config/examples/default-config.json ~/.aceflow/config.json
        log_info "Created default configuration at ~/.aceflow/config.json"
    fi
    
    log_success "Local deployment completed"
    log_info "Start server with: aceflow-unified --mode enhanced"
}

deploy_docker() {
    log_info "Deploying with Docker Compose..."
    
    cd "$PROJECT_DIR"
    
    # Create necessary directories
    mkdir -p config data logs
    
    # Copy example configuration if not exists
    if [ ! -f config/aceflow-config.json ]; then
        cp .env.example config/.env
        log_info "Created example environment file"
    fi
    
    # Start services
    docker-compose up -d
    
    # Wait for services to start
    sleep 15
    
    # Check health
    if docker-compose exec aceflow-unified aceflow-unified test health; then
        log_success "Docker deployment successful"
        log_info "Server is running at http://localhost:8080"
        log_info "View logs with: docker-compose logs -f"
    else
        log_error "Docker deployment failed"
        docker-compose logs
        exit 1
    fi
}

deploy_production() {
    log_info "Preparing production deployment..."
    
    # Build and test package
    build_package
    test_package
    
    # Build and test Docker image
    build_docker
    test_docker
    
    log_success "Production artifacts ready"
    log_info "Package: dist/*.whl"
    log_info "Docker image: $DOCKER_IMAGE"
    
    log_warning "Manual steps for production deployment:"
    echo "1. Upload package to PyPI: twine upload dist/*"
    echo "2. Push Docker image: docker push $DOCKER_IMAGE"
    echo "3. Update deployment manifests with new version"
    echo "4. Deploy to production environment"
}

show_help() {
    echo "AceFlow MCP Server Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  local       Deploy locally for development"
    echo "  docker      Deploy using Docker Compose"
    echo "  build       Build package and Docker image"
    echo "  test        Test package and Docker image"
    echo "  production  Prepare production deployment"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 local                # Install locally"
    echo "  $0 docker               # Deploy with Docker"
    echo "  $0 production           # Prepare for production"
}

# Main execution
main() {
    case "${1:-help}" in
        "local")
            check_dependencies
            deploy_local
            ;;
        "docker")
            check_dependencies
            build_docker
            deploy_docker
            ;;
        "build")
            check_dependencies
            build_package
            build_docker
            ;;
        "test")
            check_dependencies
            test_package
            test_docker
            ;;
        "production")
            check_dependencies
            deploy_production
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function
main "$@"