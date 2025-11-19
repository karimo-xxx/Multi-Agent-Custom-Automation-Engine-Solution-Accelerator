#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Builds and pushes Docker images to Azure Container Registry.

.DESCRIPTION
    This script builds Backend, Frontend, and MCP Server Docker images and pushes them to your Azure Container Registry.
    It can automatically detect the ACR from azd environment or you can specify it manually.

.PARAMETER AcrName
    The name of the Azure Container Registry (without .azurecr.io)

.PARAMETER ImageTag
    The tag to use for the Docker images. Default: latest_v3

.PARAMETER SkipBuild
    Skip building images and only push existing local images

.PARAMETER Components
    Comma-separated list of components to build/push. Options: backend, frontend, mcp. Default: all

.EXAMPLE
    .\build-and-push-images.ps1
    # Automatically detects ACR from azd and builds all images

.EXAMPLE
    .\build-and-push-images.ps1 -AcrName "crmacaeabc12" -ImageTag "v2.0"
    # Uses specified ACR and tag

.EXAMPLE
    .\build-and-push-images.ps1 -Components "backend,frontend"
    # Only builds and pushes backend and frontend
#>

param(
    [string]$AcrName = "",
    [string]$ImageTag = "latest_v3",
    [switch]$SkipBuild = $false,
    [string]$Components = "backend,frontend,mcp"
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Info { Write-Host "ℹ️  $args" -ForegroundColor Cyan }
function Write-Success { Write-Host "✅ $args" -ForegroundColor Green }
function Write-Error { Write-Host "❌ $args" -ForegroundColor Red }
function Write-Warning { Write-Host "⚠️  $args" -ForegroundColor Yellow }

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Docker Image Build & Push Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Get repository root
$RepoRoot = Split-Path -Parent $PSScriptRoot
Write-Info "Repository root: $RepoRoot"

# Change to repository root
Set-Location $RepoRoot

# Detect ACR from azd if not specified
if ([string]::IsNullOrEmpty($AcrName)) {
    Write-Info "Detecting ACR from azd environment..."
    
    try {
        $azdEnvOutput = azd env get-values 2>&1
        $containerRegistryName = $azdEnvOutput | Select-String "CONTAINER_REGISTRY_NAME=" | ForEach-Object { $_.ToString().Split('=')[1].Trim('"') }
        
        if ([string]::IsNullOrEmpty($containerRegistryName)) {
            Write-Error "Could not detect ACR from azd environment."
            Write-Info "Please run 'azd up' first or specify -AcrName parameter."
            exit 1
        }
        
        $AcrName = $containerRegistryName
        Write-Success "Detected ACR: $AcrName"
    }
    catch {
        Write-Error "Failed to get ACR from azd: $_"
        Write-Info "Please specify -AcrName parameter."
        exit 1
    }
}

$AcrLoginServer = "$AcrName.azurecr.io"
Write-Info "ACR Login Server: $AcrLoginServer"
Write-Info "Image Tag: $ImageTag"
Write-Info "Components: $Components"
Write-Host ""

# Login to ACR
Write-Info "Logging in to Azure Container Registry..."
try {
    az acr login --name $AcrName
    Write-Success "Successfully logged in to ACR"
}
catch {
    Write-Error "Failed to login to ACR: $_"
    Write-Info "Make sure you are logged in to Azure CLI (az login)"
    exit 1
}
Write-Host ""

# Parse components
$componentList = $Components.Split(',') | ForEach-Object { $_.Trim().ToLower() }

# Build and push images
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

    Write-Host "================================" -ForegroundColor Yellow
    Write-Host "Processing: $($image.Name.ToUpper())" -ForegroundColor Yellow
    Write-Host "================================" -ForegroundColor Yellow
    
    $fullImageName = "$AcrLoginServer/$($image.ImageName):$ImageTag"
    Write-Info "Image: $fullImageName"
    
    # Check if Dockerfile exists
    if (-not (Test-Path $image.Dockerfile)) {
        Write-Error "Dockerfile not found: $($image.Dockerfile)"
        $failureCount++
        continue
    }
    
    # Build image
    if (-not $SkipBuild) {
        Write-Info "Building Docker image..."
        try {
            docker build --no-cache -f $image.Dockerfile -t $fullImageName .
            Write-Success "Successfully built $($image.Name) image"
        }
        catch {
            Write-Error "Failed to build $($image.Name) image: $_"
            $failureCount++
            continue
        }
    }
    else {
        Write-Warning "Skipping build (SkipBuild flag set)"
    }
    
    # Push image
    Write-Info "Pushing Docker image to ACR..."
    try {
        docker push $fullImageName
        Write-Success "Successfully pushed $($image.Name) image"
        $successCount++
    }
    catch {
        Write-Error "Failed to push $($image.Name) image: $_"
        $failureCount++
    }
    
    Write-Host ""
}

# Summary
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Success "Successfully processed: $successCount image(s)"
if ($failureCount -gt 0) {
    Write-Error "Failed: $failureCount image(s)"
}
Write-Host ""

if ($failureCount -eq 0) {
    Write-Success "All images successfully built and pushed! 🎉"
    Write-Host ""
    Write-Info "Next steps:"
    Write-Host "  1. Run 'azd deploy' to update the running services with new images"
    Write-Host "  2. Or manually restart Container Apps and App Service in Azure Portal"
    Write-Host ""
    exit 0
}
else {
    Write-Error "Some images failed to build/push. Please check the errors above."
    exit 1
}
