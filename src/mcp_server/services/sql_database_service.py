"""
SQL Database Service for MACAE MCP Server.
Provides MCP tools for querying HR and IT support data from Azure SQL Database.
"""

import logging
import os
from typing import Any

import pyodbc
from azure.identity import DefaultAzureCredential

from core.factory import Domain, MCPToolBase

logger = logging.getLogger(__name__)


class SQLDatabaseService(MCPToolBase):
    """Service for interacting with Azure SQL Database via MCP tools."""

    def __init__(self):
        """Initialize SQL Database Service."""
        super().__init__(Domain.DATA)
        self.connection_string = os.getenv("SQL_CONNECTION_STRING", "")
        self.use_managed_identity = os.getenv("SQL_USE_MANAGED_IDENTITY", "true").lower() == "true"
        self._connection = None
        logger.info("🗄️  SQL Database Service initialized")

    @property
    def tool_count(self) -> int:
        """Return the number of tools provided by this service."""
        return 9  # Total SQL query tools

    def register_tools(self, mcp) -> None:
        """Register SQL database tools with the MCP server."""

        @mcp.tool(tags={self.domain.value})
        async def query_employees(
            department: str | None = None,
            position: str | None = None,
            employment_status: str = "Active",
        ) -> list[dict[str, Any]]:
            """
            Query employee records from the HR database.

            Args:
                department: Filter by department (e.g., 'IT', 'HR', 'Engineering')
                position: Filter by position (e.g., 'Software Engineer')
                employment_status: Filter by status (default: 'Active')

            Returns:
                List of employee records with details
            """
            return self._query_employees(department, position, employment_status)

        @mcp.tool(tags={self.domain.value})
        async def get_employee_benefits(
            employee_id: int | None = None, 
            email: str | None = None
        ) -> list[dict[str, Any]]:
            """
            Get benefits information for an employee.

            Args:
                employee_id: Employee ID to query
                email: Employee email to query (alternative to ID)

            Returns:
                List of benefits records for the employee
            """
            return self._get_employee_benefits(employee_id, email)

        @mcp.tool(tags={self.domain.value})
        async def get_leave_requests(
            employee_id: int | None = None,
            status: str | None = None,
            limit: int = 10,
        ) -> list[dict[str, Any]]:
            """
            Get leave/vacation requests.

            Args:
                employee_id: Filter by employee ID (optional)
                status: Filter by status (Pending, Approved, Rejected)
                limit: Maximum number of records to return

            Returns:
                List of leave requests
            """
            return self._get_leave_requests(employee_id, status, limit)

        @mcp.tool(tags={self.domain.value})
        async def get_training_records(
            employee_id: int | None = None,
            status: str | None = None,
            limit: int = 10,
        ) -> list[dict[str, Any]]:
            """
            Get training and development records.

            Args:
                employee_id: Filter by employee ID (optional)
                status: Filter by status (Scheduled, In Progress, Completed)
                limit: Maximum number of records to return

            Returns:
                List of training records
            """
            return self._get_training_records(employee_id, status, limit)

        @mcp.tool(tags={self.domain.value})
        async def get_performance_reviews(
            employee_id: int | None = None, 
            limit: int = 5
        ) -> list[dict[str, Any]]:
            """
            Get performance review records.

            Args:
                employee_id: Filter by employee ID (optional)
                limit: Maximum number of records to return

            Returns:
                List of performance reviews
            """
            return self._get_performance_reviews(employee_id, limit)

        @mcp.tool(tags={self.domain.value})
        async def query_it_assets(
            asset_type: str | None = None,
            status: str = "Available",
            limit: int = 20,
        ) -> list[dict[str, Any]]:
            """
            Query IT hardware assets from inventory.

            Args:
                asset_type: Filter by type (Laptop, Desktop, Monitor, Phone, etc.)
                status: Filter by status (Available, Assigned, In Repair, Retired)
                limit: Maximum number of records to return

            Returns:
                List of IT assets
            """
            return self._query_it_assets(asset_type, status, limit)

        @mcp.tool(tags={self.domain.value})
        async def get_software_licenses(
            software_name: str | None = None, 
            status: str = "Active"
        ) -> list[dict[str, Any]]:
            """
            Get software license information.

            Args:
                software_name: Filter by software name (optional)
                status: Filter by status (default: Active)

            Returns:
                List of software licenses with usage information
            """
            return self._get_software_licenses(software_name, status)

        @mcp.tool(tags={self.domain.value})
        async def get_support_tickets(
            status: str | None = None,
            priority: str | None = None,
            limit: int = 10,
        ) -> list[dict[str, Any]]:
            """
            Get IT support tickets.

            Args:
                status: Filter by status (Open, In Progress, Resolved, Closed)
                priority: Filter by priority (Low, Medium, High, Critical)
                limit: Maximum number of records to return

            Returns:
                List of support tickets
            """
            return self._get_support_tickets(status, priority, limit)

        @mcp.tool(tags={self.domain.value})
        async def get_system_permissions(
            employee_id: int | None = None, 
            email: str | None = None
        ) -> list[dict[str, Any]]:
            """
            Get system access permissions for an employee.

            Args:
                employee_id: Employee ID to query
                email: Employee email to query (alternative to ID)

            Returns:
                List of system permissions for the employee
            """
            return self._get_system_permissions(employee_id, email)

    def _get_connection(self) -> pyodbc.Connection:
        """Get or create database connection with managed identity support."""
        if self._connection and not self._connection.closed:
            return self._connection

        if not self.connection_string:
            raise ValueError("SQL_CONNECTION_STRING environment variable not set")

        try:
            if self.use_managed_identity:
                # Use Azure Managed Identity for authentication
                credential = DefaultAzureCredential()
                token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
                token_struct = b'\x01\x00' + token_bytes + b'\x00\x00'
                
                # Parse connection string to extract server and database
                conn_parts = {}
                for part in self.connection_string.split(";"):
                    if "=" in part:
                        key, value = part.split("=", 1)
                        conn_parts[key.strip().lower()] = value.strip()
                
                server = conn_parts.get("server", "").replace("tcp:", "").split(",")[0]
                database = conn_parts.get("initial catalog", conn_parts.get("database", ""))
                
                # Build connection string for managed identity
                conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={server};Database={database};Encrypt=yes;TrustServerCertificate=no;"
                
                # Connect with access token
                self._connection = pyodbc.connect(conn_str, attrs_before={1256: token_struct})
                logger.info("✅ Connected to SQL Database using Managed Identity")
            else:
                # Use SQL Authentication (fallback)
                self._connection = pyodbc.connect(self.connection_string)
                logger.info("✅ Connected to SQL Database using SQL Authentication")
            
            return self._connection
        except Exception as e:
            logger.error(f"❌ Failed to connect to SQL Database: {e}")
            raise

    def _execute_query(self, query: str) -> list[dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Get column names
            columns = [column[0] for column in cursor.description]
            
            # Fetch all rows and convert to dictionaries
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            cursor.close()
            logger.info(f"✅ Query executed successfully, returned {len(results)} rows")
            return results
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            raise

    # ========================================
    # HR Helper Agent Tools
    # ========================================

    def _query_employees(
        self,
        department: str | None = None,
        position: str | None = None,
        employment_status: str = "Active",
    ) -> list[dict[str, Any]]:
        """
        Query employee records from the HR database.

        Args:
            department: Filter by department (e.g., 'IT', 'HR', 'Engineering')
            position: Filter by position (e.g., 'Software Engineer')
            employment_status: Filter by status (default: 'Active')

        Returns:
            List of employee records with details
        """
        query = "SELECT EmployeeID, FirstName, LastName, Email, Department, Position, HireDate, Salary, EmploymentStatus FROM Employees WHERE EmploymentStatus = ?"
        params = [employment_status]

        if department:
            query += " AND Department = ?"
            params.append(department)

        if position:
            query += " AND Position = ?"
            params.append(position)

        query += " ORDER BY LastName, FirstName"

        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"❌ Failed to query employees: {e}")
            raise

    def _get_employee_benefits(self, employee_id: int | None = None, email: str | None = None) -> list[dict[str, Any]]:
        """
        Get benefits information for an employee.

        Args:
            employee_id: Employee ID to query
            email: Employee email to query (alternative to ID)

        Returns:
            List of benefits records for the employee
        """
        if not employee_id and not email:
            raise ValueError("Either employee_id or email must be provided")

        if email:
            # First get employee ID from email
            emp_query = "SELECT EmployeeID FROM Employees WHERE Email = ?"
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(emp_query, [email])
            result = cursor.fetchone()
            if not result:
                return []
            employee_id = result[0]

        query = """
        SELECT b.BenefitID, b.BenefitType, b.Provider, b.PlanName, 
               b.MonthlyContribution, b.EnrollmentDate, b.Status
        FROM Benefits b
        WHERE b.EmployeeID = ? AND b.Status = 'Active'
        ORDER BY b.BenefitType
        """
        return self._execute_query(query.replace("?", str(employee_id)))

    def _get_leave_requests(
        self, employee_id: int | None = None, status: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Get leave/vacation requests.

        Args:
            employee_id: Filter by employee ID (optional)
            status: Filter by status (Pending, Approved, Rejected)
            limit: Maximum number of records to return

        Returns:
            List of leave requests
        """
        query = """
        SELECT l.LeaveID, e.FirstName + ' ' + e.LastName as EmployeeName, 
               l.LeaveType, l.StartDate, l.EndDate, l.TotalDays, 
               l.Status, l.RequestDate, l.Reason
        FROM LeaveManagement l
        JOIN Employees e ON l.EmployeeID = e.EmployeeID
        WHERE 1=1
        """
        params = []

        if employee_id:
            query += " AND l.EmployeeID = ?"
            params.append(employee_id)

        if status:
            query += " AND l.Status = ?"
            params.append(status)

        query += f" ORDER BY l.RequestDate DESC OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"

        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"❌ Failed to query leave requests: {e}")
            raise

    def _get_training_records(
        self, employee_id: int | None = None, status: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Get training and development records.

        Args:
            employee_id: Filter by employee ID (optional)
            status: Filter by status (Scheduled, In Progress, Completed)
            limit: Maximum number of records to return

        Returns:
            List of training records
        """
        query = """
        SELECT t.TrainingID, e.FirstName + ' ' + e.LastName as EmployeeName,
               t.TrainingName, t.TrainingCategory, t.Provider, 
               t.StartDate, t.EndDate, t.Status, t.CompletionPercentage,
               t.CertificationAwarded
        FROM TrainingRecords t
        JOIN Employees e ON t.EmployeeID = e.EmployeeID
        WHERE 1=1
        """
        params = []

        if employee_id:
            query += " AND t.EmployeeID = ?"
            params.append(employee_id)

        if status:
            query += " AND t.Status = ?"
            params.append(status)

        query += f" ORDER BY t.StartDate DESC OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"

        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"❌ Failed to query training records: {e}")
            raise

    def _get_performance_reviews(self, employee_id: int | None = None, limit: int = 5) -> list[dict[str, Any]]:
        """
        Get performance review records.

        Args:
            employee_id: Filter by employee ID (optional)
            limit: Maximum number of records to return

        Returns:
            List of performance reviews
        """
        query = """
        SELECT p.ReviewID, e.FirstName + ' ' + e.LastName as EmployeeName,
               p.ReviewPeriodStart, p.ReviewPeriodEnd, p.OverallRating,
               p.TechnicalSkills, p.Communication, p.Teamwork, p.Leadership,
               p.Goals, p.Achievements, p.AreasForImprovement, p.ReviewDate
        FROM PerformanceReviews p
        JOIN Employees e ON p.EmployeeID = e.EmployeeID
        WHERE 1=1
        """
        params = []

        if employee_id:
            query += " AND p.EmployeeID = ?"
            params.append(employee_id)

        query += f" ORDER BY p.ReviewDate DESC OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"

        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"❌ Failed to query performance reviews: {e}")
            raise

    # ========================================
    # Technical Support Agent Tools
    # ========================================

    def _query_it_assets(
        self, asset_type: str | None = None, status: str = "Available", limit: int = 20
    ) -> list[dict[str, Any]]:
        """
        Query IT hardware assets from inventory.

        Args:
            asset_type: Filter by type (Laptop, Desktop, Monitor, Phone, etc.)
            status: Filter by status (Available, Assigned, In Repair, Retired)
            limit: Maximum number of records to return

        Returns:
            List of IT assets
        """
        query = """
        SELECT a.AssetID, a.AssetTag, a.AssetType, a.Manufacturer, a.Model,
               a.SerialNumber, a.Status, a.Location, a.Specifications,
               e.FirstName + ' ' + e.LastName as AssignedTo
        FROM ITAssets a
        LEFT JOIN Employees e ON a.AssignedToEmployeeID = e.EmployeeID
        WHERE a.Status = ?
        """
        params = [status]

        if asset_type:
            query += " AND a.AssetType = ?"
            params.append(asset_type)

        query += f" ORDER BY a.AssetType, a.Manufacturer OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"

        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"❌ Failed to query IT assets: {e}")
            raise

    def _get_software_licenses(self, software_name: str | None = None, status: str = "Active") -> list[dict[str, Any]]:
        """
        Get software license information.

        Args:
            software_name: Filter by software name (optional)
            status: Filter by status (default: Active)

        Returns:
            List of software licenses with usage information
        """
        query = """
        SELECT LicenseID, SoftwareName, LicenseType, Vendor, 
               TotalSeats, UsedSeats, (TotalSeats - UsedSeats) as AvailableSeats,
               ExpiryDate, RenewalDate, Cost, Status
        FROM SoftwareLicenses
        WHERE Status = ?
        """
        params = [status]

        if software_name:
            query += " AND SoftwareName LIKE ?"
            params.append(f"%{software_name}%")

        query += " ORDER BY SoftwareName"

        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"❌ Failed to query software licenses: {e}")
            raise

    def _get_support_tickets(
        self, status: str | None = None, priority: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Get IT support tickets.

        Args:
            status: Filter by status (Open, In Progress, Resolved, Closed)
            priority: Filter by priority (Low, Medium, High, Critical)
            limit: Maximum number of records to return

        Returns:
            List of support tickets
        """
        query = """
        SELECT t.TicketID, t.TicketNumber, t.Category, t.Priority, t.Status,
               t.Subject, t.Description, t.CreatedAt,
               e.FirstName + ' ' + e.LastName as RequestedBy,
               tech.FirstName + ' ' + tech.LastName as AssignedTo
        FROM SupportTickets t
        JOIN Employees e ON t.EmployeeID = e.EmployeeID
        LEFT JOIN Employees tech ON t.AssignedToTechnicianID = tech.EmployeeID
        WHERE 1=1
        """
        params = []

        if status:
            query += " AND t.Status = ?"
            params.append(status)

        if priority:
            query += " AND t.Priority = ?"
            params.append(priority)

        query += f" ORDER BY t.CreatedAt DESC OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"

        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"❌ Failed to query support tickets: {e}")
            raise

    def _get_system_permissions(self, employee_id: int | None = None, email: str | None = None) -> list[dict[str, Any]]:
        """
        Get system access permissions for an employee.

        Args:
            employee_id: Employee ID to query
            email: Employee email to query (alternative to ID)

        Returns:
            List of system permissions for the employee
        """
        if not employee_id and not email:
            raise ValueError("Either employee_id or email must be provided")

        if email:
            # First get employee ID from email
            emp_query = "SELECT EmployeeID FROM Employees WHERE Email = ?"
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(emp_query, [email])
            result = cursor.fetchone()
            if not result:
                return []
            employee_id = result[0]

        query = """
        SELECT p.PermissionID, p.SystemName, p.AccessLevel, 
               p.GrantedDate, p.ExpiryDate, p.Status
        FROM SystemPermissions p
        WHERE p.EmployeeID = ? AND p.Status = 'Active'
        ORDER BY p.SystemName
        """
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, [employee_id])
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"❌ Failed to query system permissions: {e}")
            raise

    def __del__(self):
        """Close database connection on cleanup."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            logger.info("🔒 SQL Database connection closed")
