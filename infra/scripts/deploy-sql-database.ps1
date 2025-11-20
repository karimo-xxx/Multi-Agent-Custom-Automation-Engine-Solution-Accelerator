# ========================================
# Deploy SQL Database Schema and Data
# ========================================
# This script deploys the SQL schema and seed data to Azure SQL Database
# Uses Azure CLI and sqlcmd for database operations

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$SqlServerName,
    
    [Parameter(Mandatory=$true)]
    [string]$DatabaseName = "macae-hr-db"
)

Write-Host "🚀 Starting SQL Database Schema Deployment" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor Yellow
Write-Host "SQL Server: $SqlServerName" -ForegroundColor Yellow
Write-Host "Database: $DatabaseName" -ForegroundColor Yellow
Write-Host ""

# Get the directory where this script is located
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$sqlScriptsPath = Join-Path $scriptPath "sql"

# Check if SQL scripts exist
$schemaScript = Join-Path $sqlScriptsPath "schema.sql"
$seedDataScript = Join-Path $sqlScriptsPath "seed_data.sql"

if (-not (Test-Path $schemaScript)) {
    Write-Host "❌ Schema script not found: $schemaScript" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $seedDataScript)) {
    Write-Host "❌ Seed data script not found: $seedDataScript" -ForegroundColor Red
    exit 1
}

Write-Host "✅ SQL scripts found" -ForegroundColor Green
Write-Host ""

# Get Azure AD access token for SQL Database
Write-Host "🔐 Getting Azure AD access token..." -ForegroundColor Cyan
$token = az account get-access-token --resource=https://database.windows.net/ --query accessToken -o tsv

if (-not $token) {
    Write-Host "❌ Failed to get Azure AD access token. Please ensure you are logged in with 'az login'" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Access token obtained" -ForegroundColor Green
Write-Host ""

# Get SQL Server FQDN
Write-Host "🔍 Getting SQL Server FQDN..." -ForegroundColor Cyan
$sqlServerFqdn = az sql server show --name $SqlServerName --resource-group $ResourceGroupName --query "fullyQualifiedDomainName" -o tsv

if (-not $sqlServerFqdn) {
    Write-Host "❌ Failed to get SQL Server FQDN" -ForegroundColor Red
    exit 1
}

Write-Host "✅ SQL Server FQDN: $sqlServerFqdn" -ForegroundColor Green
Write-Host ""

# Check if sqlcmd is installed
Write-Host "🔍 Checking for sqlcmd..." -ForegroundColor Cyan
$sqlcmdPath = Get-Command sqlcmd -ErrorAction SilentlyContinue

if (-not $sqlcmdPath) {
    Write-Host "⚠️  sqlcmd not found. Attempting to install..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please install sqlcmd using one of these methods:" -ForegroundColor Yellow
    Write-Host "  1. Windows: Install SQL Server Command Line Utilities" -ForegroundColor Yellow
    Write-Host "     Download from: https://learn.microsoft.com/sql/tools/sqlcmd-utility" -ForegroundColor Yellow
    Write-Host "  2. winget: winget install Microsoft.SqlCmd" -ForegroundColor Yellow
    Write-Host "  3. Or use Azure Cloud Shell which has sqlcmd pre-installed" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installation, run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ sqlcmd found: $($sqlcmdPath.Source)" -ForegroundColor Green
Write-Host ""

# Function to execute SQL script with access token
function Invoke-SqlScript {
    param(
        [string]$ScriptPath,
        [string]$Description
    )
    
    Write-Host "📝 Executing $Description..." -ForegroundColor Cyan
    
    # Read script content
    $sqlContent = Get-Content $ScriptPath -Raw
    
    # Execute with sqlcmd using access token
    $result = $sqlContent | sqlcmd -S $sqlServerFqdn -d $DatabaseName -G -P $token -b
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to execute $Description" -ForegroundColor Red
        Write-Host $result -ForegroundColor Red
        return $false
    }
    
    Write-Host "✅ $Description executed successfully" -ForegroundColor Green
    return $true
}

# Deploy schema
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 1: Deploying Database Schema" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$schemaSuccess = Invoke-SqlScript -ScriptPath $schemaScript -Description "Database Schema"

if (-not $schemaSuccess) {
    Write-Host "❌ Schema deployment failed. Stopping." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Deploy seed data
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 2: Deploying Seed Data" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$seedDataSuccess = Invoke-SqlScript -ScriptPath $seedDataScript -Description "Seed Data"

if (-not $seedDataSuccess) {
    Write-Host "❌ Seed data deployment failed. Stopping." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Verify deployment
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 3: Verifying Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$verificationQuery = @"
SELECT 
    (SELECT COUNT(*) FROM Employees) as EmployeeCount,
    (SELECT COUNT(*) FROM ITAssets) as AssetCount,
    (SELECT COUNT(*) FROM SoftwareLicenses) as LicenseCount,
    (SELECT COUNT(*) FROM SupportTickets) as TicketCount;
"@

Write-Host "🔍 Verifying table counts..." -ForegroundColor Cyan
$verificationResult = $verificationQuery | sqlcmd -S $sqlServerFqdn -d $DatabaseName -G -P $token -b

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database verification successful" -ForegroundColor Green
    Write-Host $verificationResult
} else {
    Write-Host "⚠️  Database verification had issues" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ SQL Database Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Database: $DatabaseName on $sqlServerFqdn" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Verify the MCP Container App has the SQL_CONNECTION_STRING environment variable set" -ForegroundColor White
Write-Host "  2. Restart the MCP Container App to load the new SQL service" -ForegroundColor White
Write-Host "  3. Upload the updated HR team configuration: data/agent_teams/hr.json" -ForegroundColor White
Write-Host "  4. Test SQL queries through the HR and Technical Support agents" -ForegroundColor White
Write-Host ""
