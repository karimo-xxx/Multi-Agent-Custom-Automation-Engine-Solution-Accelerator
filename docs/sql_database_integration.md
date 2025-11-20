# Azure SQL Database Integration for MCP Server

This integration adds Azure SQL Database support to the MACAE MCP Server, enabling the HR and Technical Support agents to query structured data from a centralized database.

## 📋 Overview

The SQL Database integration provides:

### **HRHelperAgent Tools:**
- `query_employees` - Query employee records by department, position, or status
- `get_employee_benefits` - Retrieve benefits information for employees
- `get_leave_requests` - View leave/vacation requests and their status
- `get_training_records` - Access training and certification data
- `get_performance_reviews` - Query performance review history

### **TechnicalSupportAgent Tools:**
- `query_it_assets` - Search IT hardware inventory (laptops, monitors, phones)
- `get_software_licenses` - Check software license availability and usage
- `get_support_tickets` - View IT support tickets by status or priority
- `get_system_permissions` - Query user access permissions across systems

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │
│   (Web App)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│   Backend       │◄────►│  MCP Container   │
│   (FastAPI)     │      │  App (FastMCP)   │
└─────────────────┘      └────────┬─────────┘
                                  │
                                  │ Managed Identity
                                  │ Authentication
                                  ▼
                         ┌──────────────────┐
                         │  Azure SQL       │
                         │  Database        │
                         │  (macae-hr-db)   │
                         └──────────────────┘
```

## 🚀 Deployment Guide

### Prerequisites

1. **Azure CLI** installed and authenticated
2. **sqlcmd** utility installed for database operations
   - Windows: Install [SQL Server Command Line Utilities](https://learn.microsoft.com/sql/tools/sqlcmd-utility)
   - Or use: `winget install Microsoft.SqlCmd`
   - Alternative: Use Azure Cloud Shell (has sqlcmd pre-installed)

### Step 1: Deploy Infrastructure

The SQL Database is automatically deployed when you run:

```powershell
azd up
```

This will create:
- Azure SQL Server (`sql-{suffix}`)
- Azure SQL Database (`macae-hr-db` - Basic Tier)
- Managed Identity authentication configured
- Firewall rules for Azure services

### Step 2: Deploy Database Schema and Data

After infrastructure deployment, run the SQL deployment script:

```powershell
# Navigate to the scripts directory
cd infra/scripts

# Run the deployment script
./deploy-sql-database.ps1 `
  -ResourceGroupName "rg-karim" `
  -SqlServerName "sql-devpikfl" `
  -DatabaseName "macae-hr-db"
```

This script will:
1. ✅ Authenticate using Azure AD (Managed Identity)
2. ✅ Deploy the database schema (9 tables)
3. ✅ Insert demo data (17 employees, IT assets, tickets, etc.)
4. ✅ Verify deployment

### Step 3: Update MCP Container App

The MCP Container App needs to be restarted to load the SQL service:

```powershell
# Get the MCP Container App name
$mcpAppName = az containerapp list --resource-group rg-karim --query "[?contains(name, 'mcp')].name" -o tsv

# Restart the container app
az containerapp revision restart --name $mcpAppName --resource-group rg-karim
```

### Step 4: Upload Updated Team Configuration

Upload the updated HR team configuration with SQL-aware system messages:

```powershell
cd C:\Users\Karim-MichaelAitOuka\git\AI_for_Breakfast\Multi-Agent-Custom-Automation-Engine-Solution-Accelerator

.\.venv\Scripts\python.exe infra\scripts\upload_team_config.py https://app-devpikfl.azurewebsites.net data\agent_teams
```

## 🧪 Testing

### Test Queries via Frontend

1. Navigate to the frontend: `https://app-devpikfl.azurewebsites.net`
2. Select the **"Human Resources Team"**
3. Try these example prompts:

**HRHelperAgent Tests:**
```
- "Show me all employees in the IT department"
- "What are Jessica Smith's benefits?"
- "Show me pending leave requests"
- "What training has Daniel Lee completed?"
- "Show me the performance review for employee ID 12"
```

**TechnicalSupportAgent Tests:**
```
- "What laptops are available in inventory?"
- "Check software license usage for Microsoft 365"
- "Show me open support tickets"
- "What IT assets are assigned to jessica.smith@macae.com?"
- "List all system permissions for employee ID 8"
```

### Test Queries via Direct SQL

You can also test directly using sqlcmd:

```powershell
# Get access token
$token = az account get-access-token --resource=https://database.windows.net/ --query accessToken -o tsv

# Connect to database
sqlcmd -S sql-devpikfl.database.windows.net -d macae-hr-db -G -P $token

# Run test queries
SELECT COUNT(*) as EmployeeCount FROM Employees;
SELECT * FROM ITAssets WHERE Status = 'Available';
SELECT * FROM SupportTickets WHERE Status = 'Open';
```

## 📊 Database Schema

### HR Tables (HRHelperAgent)

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `Employees` | Employee master data | EmployeeID, Email, Department, Position |
| `Benefits` | Benefits enrollment | BenefitType, Provider, MonthlyContribution |
| `LeaveManagement` | Leave/vacation requests | LeaveType, Status, StartDate, EndDate |
| `TrainingRecords` | Training & certifications | TrainingName, Status, CertificationAwarded |
| `PerformanceReviews` | Performance evaluations | OverallRating, ReviewDate |

### IT Tables (TechnicalSupportAgent)

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `ITAssets` | Hardware inventory | AssetType, Status, AssignedTo |
| `SoftwareLicenses` | Software licensing | SoftwareName, TotalSeats, UsedSeats |
| `SupportTickets` | IT support tickets | TicketNumber, Priority, Status |
| `NetworkConfigurations` | Network settings | VPNAccess, NetworkDriveAccess |
| `SystemPermissions` | Access management | SystemName, AccessLevel |

## 🔐 Security

### Authentication

- **Managed Identity**: MCP Container App uses Azure Managed Identity for passwordless authentication
- **Azure AD Only**: SQL Server configured for Azure AD authentication only
- **No Credentials**: Connection strings don't contain passwords

### Connection String Format

```
Server=tcp:sql-{suffix}.database.windows.net,1433;
Initial Catalog=macae-hr-db;
Authentication=Active Directory Default;
Encrypt=True;
TrustServerCertificate=False;
Connection Timeout=30;
```

### Permissions

The Managed Identity is granted:
- SQL Database Contributor role on the database
- Permissions to query all tables
- No write access (read-only for safety)

## 🐛 Troubleshooting

### "Could not find package pyodbc"

**Solution**: The Docker image includes ODBC drivers. If running locally, install:
```powershell
pip install pyodbc
```

### "Login failed for user"

**Solution**: Ensure the Managed Identity has proper permissions:
```powershell
# Grant SQL DB Contributor role
az sql db update --name macae-hr-db --server sql-devpikfl --resource-group rg-karim --assign-identity
```

### "Cannot connect to SQL Server"

**Solution**: Verify firewall rules allow Azure services:
```powershell
az sql server firewall-rule show --name AllowAllWindowsAzureIps --server sql-devpikfl --resource-group rg-karim
```

### MCP Tools not appearing

**Solution**: 
1. Check MCP Container App logs
2. Verify `SQL_CONNECTION_STRING` environment variable is set
3. Restart the container app

## 📝 Demo Data

The database includes sample data for testing:

- **17 Employees** across IT, HR, Engineering, and Sales departments
- **9 IT Assets** (laptops, monitors, phones) with various statuses
- **7 Software Licenses** (Microsoft 365, Adobe, Slack, etc.)
- **5 Support Tickets** with different priorities and statuses
- **10 Benefits** enrollments
- **5 Leave Requests** (pending and approved)
- **6 Training Records** (completed and in-progress)
- **3 Performance Reviews**

## 🔄 Updating the Database

To modify schema or add data:

1. Edit SQL scripts in `infra/scripts/sql/`
2. Run the deployment script again:
   ```powershell
   ./deploy-sql-database.ps1 -ResourceGroupName rg-karim -SqlServerName sql-devpikfl
   ```

## 📚 References

- [Azure SQL Database Documentation](https://learn.microsoft.com/azure/azure-sql/)
- [Managed Identity for SQL](https://learn.microsoft.com/azure/azure-sql/database/authentication-aad-configure)
- [pyodbc Documentation](https://github.com/mkleehammer/pyodbc)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## 💡 Example Use Cases

### HR Onboarding Scenario
```
User: "I need to onboard Jessica Smith. Check her employee record and ensure she has all required benefits."

HRHelperAgent:
1. Queries employee record for Jessica Smith
2. Checks benefits enrollment
3. Verifies training schedule
4. Reviews system permissions

Result: Complete onboarding status report
```

### IT Asset Provisioning
```
User: "We need to provision a laptop for a new software engineer."

TechnicalSupportAgent:
1. Queries available laptops in inventory
2. Checks specifications
3. Recommends suitable device
4. Shows license availability for required software

Result: Laptop recommendation with asset tag and specs
```

---

**Built with ❤️ for the MACAE Solution Accelerator**
