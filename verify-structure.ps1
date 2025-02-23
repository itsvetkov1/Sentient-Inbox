# verify_structure.ps1

$expectedStructure = @{
    # Core source directories
    "src/email_processing" = $true
    "src/email_processing/analyzers" = $true
    "src/email_processing/classification" = $true
    "src/email_processing/handlers" = $true
    "src/storage" = $true
    "src/integrations/gmail" = $true
    "src/integrations/groq" = $true
    "src/utils" = $true

    # Test directories
    "tests/unit" = $true
    "tests/integration" = $true

    # Core files that should NOT be in root
    "email_analyzers_base.py" = $false
    "email_date_service.py" = $false
    "email_writer.py" = $false
    "mail_sorter.py" = $false
    "meeting_analyzer.py" = $false

    # Expected locations of key files
    "src/email_processing/processor.py" = $true
    "src/email_processing/analyzers/deepseek.py" = $true
    "src/email_processing/analyzers/llama.py" = $true
    "src/email_processing/classification/classifier.py" = $true
    "src/integrations/gmail/client.py" = $true
    "src/integrations/groq/client.py" = $true
    "src/storage/secure.py" = $true
}

# Check for old directories that should be removed
$oldDirectories = @(
    "utils",
    "processors",
    "analyzers",
    "groq_integration"
)

Write-Host "`nVerifying project structure...`n" -ForegroundColor Cyan

$issues = @()

# Check expected structure
foreach ($path in $expectedStructure.Keys) {
    $shouldExist = $expectedStructure[$path]
    $exists = Test-Path $path
    
    if ($shouldExist -and -not $exists) {
        $issues += "Missing: $path (should exist)"
    }
    elseif (-not $shouldExist -and $exists) {
        $issues += "Found: $path (should not exist)"
    }
}

# Check for old directories
foreach ($dir in $oldDirectories) {
    if (Test-Path $dir) {
        $issues += "Old directory still exists: $dir (should be removed)"
    }
}

# Verify __init__.py files
$pythonPackages = Get-ChildItem -Recurse -Directory | Where-Object {
    $_.FullName -like "*\src\*" -or 
    $_.FullName -like "*\tests\*"
}

foreach ($package in $pythonPackages) {
    $initPath = Join-Path $package.FullName "__init__.py"
    if (-not (Test-Path $initPath)) {
        $issues += "Missing __init__.py in: $($package.FullName)"
    }
}

# Report results
if ($issues.Count -eq 0) {
    Write-Host "✅ Project structure verification passed!" -ForegroundColor Green
    Write-Host "`nAll directories and files are in their correct locations."
} else {
    Write-Host "❌ Project structure verification found issues:" -ForegroundColor Red
    Write-Host "`nIssues found:"
    foreach ($issue in $issues) {
        Write-Host "- $issue" -ForegroundColor Yellow
    }
    Write-Host "`nPlease address these issues to maintain proper project structure."
}

# Display current structure
Write-Host "`nCurrent Project Structure:" -ForegroundColor Cyan
Get-ChildItem -Recurse -Directory | 
    Where-Object { -not $_.FullName.Contains('.git') } |
    ForEach-Object {
        $indent = "  " * ($_.FullName.Split('\').Count - 2)
        Write-Host "$indent$($_.Name)/"
        Get-ChildItem -Path $_.FullName -File |
            ForEach-Object {
                Write-Host "$indent  $($_.Name)"
            }
    }
