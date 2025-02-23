# setup_directories.ps1

"""
Project directory structure initialization script.

This script systematically creates the required directory structure
for the Sentient Inbox project, ensuring proper organization and
component separation while maintaining Windows compatibility.

Directory Structure:
- src/: Core source code
- tests/: Test implementations
- config/: Configuration files
- data/: Data storage
- docs/: Documentation
- logs/: Log files
- scripts/: Utility scripts
"""

# Core source directories
$directories = @(
    # Source code structure
    "src",
    "src/email_processing",
    "src/email_processing/analyzers",
    "src/email_processing/classification",
    "src/email_processing/handlers",
    "src/storage",
    "src/integrations",
    "src/integrations/gmail",
    "src/integrations/groq",
    "src/utils",
    
    # Test structure
    "tests",
    "tests/unit",
    "tests/integration",
    
    # Configuration
    "config",
    
    # Data storage
    "data",
    "data/cache",
    "data/metrics",
    "data/secure",
    
    # Documentation
    "docs",
    "docs/architecture",
    "docs/api",
    
    # Logs and scripts
    "logs",
    "scripts"
)

# Create each directory
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
        Write-Host "Created directory: $dir"
    } else {
        Write-Host "Directory already exists: $dir"
    }
}

# Create required __init__.py files for Python packages
$python_packages = @(
    "src",
    "src/email_processing",
    "src/email_processing/analyzers",
    "src/email_processing/classification",
    "src/email_processing/handlers",
    "src/storage",
    "src/integrations",
    "src/integrations/gmail",
    "src/integrations/groq",
    "src/utils",
    "config"
)

foreach ($package in $python_packages) {
    $init_file = Join-Path $package "__init__.py"
    if (-not (Test-Path $init_file)) {
        New-Item -ItemType File -Path $init_file -Force
        Write-Host "Created __init__.py in: $package"
    }
}

Write-Host "`nDirectory structure created successfully!"
Write-Host "Next steps:"
Write-Host "1. Begin migrating existing files to new structure"
Write-Host "2. Update import statements in Python files"
Write-Host "3. Verify all __init__.py files are properly configured"
