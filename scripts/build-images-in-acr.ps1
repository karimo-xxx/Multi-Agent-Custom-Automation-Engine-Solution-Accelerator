#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Builds Docker images directly in Azure Container Registry using ACR Build.

.DESCRIPTION
    This script builds Backend, Frontend, and MCP Server Docker images directly in Azure ACR
    without requiring Docker Desktop to be installed locally.

.PARAMETER AcrName
    The name of the Azure Container Registry (without .azurecr.io)

.PARAMETER ImageTag
    The tag to use for the Docker images. Default: latest_v3

.PARAMETER Components
    Comma-separated list of components to build. Options: backend, frontend, mcp. Default: all

.EXAMPLE
    .\build-images-in-acr.ps1 -AcrName "crdevpikfl"
    # Builds all images in Azure ACR

.EXAMPLE
    .\build-images-in-acr.ps1 -AcrName "crdevpikfl" -ImageTag "v2.0"
    # Uses specified tag

.EXAMPLE
    .\build-images-in-acr.ps1 -AcrName "crdevpikfl" -Components "backend,frontend"
    # Only builds backend and frontend
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$AcrName,
    [string]$ImageTag = "latest_v3",
    [string]$Components = "backend,frontend,mcp"
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Info { Write-Host "ℹ️  $args" -ForegroundColor Cyan }
function Write-Success { Write-Host "✅ $args" -ForegroundColor Green }
function Write-Error { Write-Host "❌ $args" -ForegroundColor Red }
function Write-Warning { Write-Host "⚠️  $args" -ForegroundColor Yellow }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Azure ACR Build Script (No Docker Needed)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get repository root
$RepoRoot = Split-Path -Parent $PSScriptRoot
Write-Info "Repository root: $RepoRoot"

# Change to repository root
Set-Location $RepoRoot

Write-Info "ACR Name: $AcrName"
Write-Info "Image Tag: $ImageTag"
Write-Info "Components: $Components"
Write-Host ""

# Check if logged in to Azure
Write-Info "Checking Azure login..."
try {
    $account = az account show 2>&1 | ConvertFrom-Json
    Write-Success "Logged in as: $($account.user.name)"
}
catch {
    Write-Error "Not logged in to Azure. Please run 'az login' first."
    exit 1
}
Write-Host ""

# Parse components
$componentList = $Components.Split(',') | ForEach-Object { $_.Trim().ToLower() }

# Build images
$images = @(
    @{
        Name = "backend"
        Dockerfile = "src/backend/Dockerfile"
        ImageName = "macaebackend"
        Enabled = $componentList -contains "backend"
    },
    @{
        Name = "frontend"
        Dockerfile = "src/frontend/Dockerfile"
        ImageName = "macaefrontend"
        Enabled = $componentList -contains "frontend"
    },
    @{
        Name = "mcp"
        Dockerfile = "src/mcp_server/Dockerfile"
        ImageName = "macaemcp"
        Enabled = $componentList -contains "mcp"
    }
)

$successCount = 0
$failureCount = 0

foreach ($image in $images) {
    if (-not $image.Enabled) {
        Write-Warning "Skipping $($image.Name) (not in component list)"
        continue
    }

    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "Building: $($image.Name.ToUpper())" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    
    $fullImageName = "$($image.ImageName):$ImageTag"
    Write-Info "Image: $fullImageName"
    Write-Info "Dockerfile: $($image.Dockerfile)"
    
    # Check if Dockerfile exists
    if (-not (Test-Path $image.Dockerfile)) {
        Write-Error "Dockerfile not found: $($image.Dockerfile)"
        $failureCount++
        continue
    }
    
    # Build image in ACR
    Write-Info "Building in Azure ACR (this may take several minutes)..."
    try {
        az acr build `
            --registry $AcrName `
            --image $fullImageName `
            --file $image.Dockerfile `
            .
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Successfully built $($image.Name) image in ACR"
            $successCount++
        } else {
            Write-Error "Failed to build $($image.Name) image"
            $failureCount++
        }
    }
    catch {
        Write-Error "Failed to build $($image.Name) image: $_"
        $failureCount++
    }
    
    Write-Host ""
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Success "Successfully built: $successCount image(s)"
if ($failureCount -gt 0) {
    Write-Error "Failed: $failureCount image(s)"
}
Write-Host ""

if ($failureCount -eq 0) {
    Write-Success "All images successfully built in Azure ACR! 🎉"
    Write-Host ""
    Write-Info "Next steps:"
    Write-Host "  1. Run 'azd deploy' to update the running services with new images"
    Write-Host "  2. Or manually restart Container Apps and App Service in Azure Portal"
    Write-Host ""
    exit 0
}
else {
    Write-Error "Some images failed to build. Please check the errors above."
    exit 1
}
