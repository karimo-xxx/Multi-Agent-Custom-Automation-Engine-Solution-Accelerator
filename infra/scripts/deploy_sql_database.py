#!/usr/bin/env python3
"""
Deploy SQL Database Schema and Data using Python and pyodbc
Alternative to PowerShell script when sqlcmd is not available
"""

import sys
import argparse
from pathlib import Path
import pyodbc
from azure.identity import DefaultAzureCredential

def main():
    parser = argparse.ArgumentParser(description='Deploy SQL Database Schema and Data')
    parser.add_argument('--resource-group', required=True, help='Resource Group name')
    parser.add_argument('--sql-server', required=True, help='SQL Server name (without .database.windows.net)')
    parser.add_argument('--database', default='macae-hr-db', help='Database name')
    
    args = parser.parse_args()
    
    print("🚀 Starting SQL Database Schema Deployment")
    print("=" * 60)
    print(f"Resource Group: {args.resource_group}")
    print(f"SQL Server: {args.sql_server}")
    print(f"Database: {args.database}")
    print()
    
    # Get script directory
    script_dir = Path(__file__).parent
    sql_dir = script_dir / "sql"
    
    schema_file = sql_dir / "schema.sql"
    seed_file = sql_dir / "seed_data.sql"
    
    # Check if SQL scripts exist
    if not schema_file.exists():
        print(f"❌ Schema script not found: {schema_file}")
        return 1
    
    if not seed_file.exists():
        print(f"❌ Seed data script not found: {seed_file}")
        return 1
    
    print("✅ SQL scripts found")
    print()
    
    # Get Azure AD access token
    print("🔐 Getting Azure AD access token...")
    try:
        credential = DefaultAzureCredential()
        token = credential.get_token("https://database.windows.net/.default")
        token_bytes = token.token.encode("UTF-16-LE")
        token_struct = b'\x01\x00' + token_bytes + b'\x00\x00'
        print("✅ Access token obtained")
        print()
    except Exception as e:
        print(f"❌ Failed to get Azure AD access token: {e}")
        print("Please ensure you are logged in with 'az login'")
        return 1
    
    # Build connection string
    server_fqdn = f"{args.sql_server}.database.windows.net"
    
    print(f"🔍 Connecting to: {server_fqdn}")
    print()
    
    # Try connection with Azure AD authentication
    try:
        # Method 1: Try with ActiveDirectoryInteractive (will prompt for authentication)
        conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={server_fqdn};Database={args.database};Authentication=ActiveDirectoryInteractive;Encrypt=yes;TrustServerCertificate=no;"
        
        print("Attempting connection with Azure AD Interactive authentication...")
        print("(This may open a browser window for authentication)")
        connection = pyodbc.connect(conn_str)
        print("✅ Connected to SQL Database")
        print()
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        print()
        print("Please ensure:")
        print("  1. You are logged in with 'az login'")
        print("  2. Your account has permissions on the SQL Database")
        print("  3. The SQL Server firewall allows your IP address")
        print()
        print("Alternative: You can also run this in Azure Cloud Shell where authentication is automatic")
        return 1
    
    cursor = connection.cursor()
    
    # Deploy schema
    print("=" * 60)
    print("Step 1: Deploying Database Schema")
    print("=" * 60)
    print()
    print("📝 Executing Database Schema...")
    
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Split by GO statements and execute individually
        statements = [stmt.strip() for stmt in schema_sql.split('GO') if stmt.strip()]
        
        for i, stmt in enumerate(statements, 1):
            if stmt:
                try:
                    cursor.execute(stmt)
                    connection.commit()
                except Exception as e:
                    # Ignore table already exists errors
                    if "already an object" not in str(e) and "already exists" not in str(e):
                        print(f"⚠️  Warning on statement {i}: {e}")
        
        print("✅ Database Schema executed successfully")
        print()
    except Exception as e:
        print(f"❌ Failed to execute schema: {e}")
        connection.close()
        return 1
    
    # Deploy seed data
    print("=" * 60)
    print("Step 2: Deploying Seed Data")
    print("=" * 60)
    print()
    print("📝 Executing Seed Data...")
    
    try:
        with open(seed_file, 'r', encoding='utf-8') as f:
            seed_sql = f.read()
        
        # Split by GO statements and execute individually
        statements = [stmt.strip() for stmt in seed_sql.split('GO') if stmt.strip()]
        
        for i, stmt in enumerate(statements, 1):
            if stmt:
                try:
                    cursor.execute(stmt)
                    connection.commit()
                except Exception as e:
                    # Ignore duplicate key errors
                    if "duplicate key" not in str(e).lower() and "violation" not in str(e).lower():
                        print(f"⚠️  Warning on statement {i}: {e}")
        
        print("✅ Seed Data executed successfully")
        print()
    except Exception as e:
        print(f"❌ Failed to execute seed data: {e}")
        connection.close()
        return 1
    
    # Verify deployment
    print("=" * 60)
    print("Step 3: Verifying Deployment")
    print("=" * 60)
    print()
    print("🔍 Verifying table counts...")
    
    try:
        verification_query = """
        SELECT 
            (SELECT COUNT(*) FROM Employees) as EmployeeCount,
            (SELECT COUNT(*) FROM ITAssets) as AssetCount,
            (SELECT COUNT(*) FROM SoftwareLicenses) as LicenseCount,
            (SELECT COUNT(*) FROM SupportTickets) as TicketCount
        """
        cursor.execute(verification_query)
        row = cursor.fetchone()
        
        print("✅ Database verification successful")
        print()
        print(f"  Employees:        {row.EmployeeCount}")
        print(f"  IT Assets:        {row.AssetCount}")
        print(f"  Software Licenses: {row.LicenseCount}")
        print(f"  Support Tickets:  {row.TicketCount}")
        print()
    except Exception as e:
        print(f"⚠️  Database verification had issues: {e}")
    
    connection.close()
    
    print("=" * 60)
    print("✅ SQL Database Deployment Complete!")
    print("=" * 60)
    print()
    print(f"Database: {args.database} on {server_fqdn}")
    print()
    print("Next Steps:")
    print("  1. Verify the MCP Container App has the SQL_CONNECTION_STRING environment variable set ✅")
    print("  2. Restart the MCP Container App to load the new SQL service")
    print("  3. Upload the updated HR team configuration: data/agent_teams/hr.json")
    print("  4. Test SQL queries through the HR and Technical Support agents")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
