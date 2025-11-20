-- ========================================
-- MACAE HR Database Schema
-- For HRHelperAgent and TechnicalSupportAgent
-- ========================================

-- ========================================
-- HR Helper Agent Tables
-- ========================================

-- Employee Records Table
CREATE TABLE Employees (
    EmployeeID INT PRIMARY KEY IDENTITY(1,1),
    FirstName NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    Email NVARCHAR(100) NOT NULL UNIQUE,
    Department NVARCHAR(50) NOT NULL,
    Position NVARCHAR(100) NOT NULL,
    HireDate DATE NOT NULL,
    ManagerID INT NULL,
    Salary DECIMAL(10,2) NOT NULL,
    EmploymentStatus NVARCHAR(20) NOT NULL DEFAULT 'Active',
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    UpdatedAt DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Manager FOREIGN KEY (ManagerID) REFERENCES Employees(EmployeeID)
);

-- Benefits and Salary Table
CREATE TABLE Benefits (
    BenefitID INT PRIMARY KEY IDENTITY(1,1),
    EmployeeID INT NOT NULL,
    BenefitType NVARCHAR(50) NOT NULL, -- Health, Dental, Vision, 401k, etc.
    Provider NVARCHAR(100) NOT NULL,
    PlanName NVARCHAR(100) NOT NULL,
    MonthlyContribution DECIMAL(10,2) NOT NULL,
    EnrollmentDate DATE NOT NULL,
    Status NVARCHAR(20) NOT NULL DEFAULT 'Active',
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Benefits_Employee FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);

-- Leave/Vacation Management Table
CREATE TABLE LeaveManagement (
    LeaveID INT PRIMARY KEY IDENTITY(1,1),
    EmployeeID INT NOT NULL,
    LeaveType NVARCHAR(30) NOT NULL, -- Vacation, Sick, Personal, Maternity, etc.
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    TotalDays INT NOT NULL,
    Status NVARCHAR(20) NOT NULL DEFAULT 'Pending', -- Pending, Approved, Rejected, Cancelled
    RequestDate DATETIME2 DEFAULT GETDATE(),
    ApprovedBy INT NULL,
    ApprovalDate DATETIME2 NULL,
    Reason NVARCHAR(500) NULL,
    CONSTRAINT FK_Leave_Employee FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID),
    CONSTRAINT FK_Leave_Approver FOREIGN KEY (ApprovedBy) REFERENCES Employees(EmployeeID)
);

-- Training and Development Table
CREATE TABLE TrainingRecords (
    TrainingID INT PRIMARY KEY IDENTITY(1,1),
    EmployeeID INT NOT NULL,
    TrainingName NVARCHAR(200) NOT NULL,
    TrainingCategory NVARCHAR(50) NOT NULL, -- Technical, Compliance, Leadership, etc.
    Provider NVARCHAR(100) NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    Status NVARCHAR(20) NOT NULL DEFAULT 'Scheduled', -- Scheduled, In Progress, Completed, Cancelled
    CompletionPercentage INT DEFAULT 0,
    CertificationAwarded BIT DEFAULT 0,
    CertificationExpiryDate DATE NULL,
    Cost DECIMAL(10,2) DEFAULT 0,
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Training_Employee FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);

-- Performance Reviews Table
CREATE TABLE PerformanceReviews (
    ReviewID INT PRIMARY KEY IDENTITY(1,1),
    EmployeeID INT NOT NULL,
    ReviewPeriodStart DATE NOT NULL,
    ReviewPeriodEnd DATE NOT NULL,
    ReviewerID INT NOT NULL,
    OverallRating DECIMAL(3,2) NOT NULL, -- Scale of 1.00 to 5.00
    TechnicalSkills DECIMAL(3,2) NOT NULL,
    Communication DECIMAL(3,2) NOT NULL,
    Teamwork DECIMAL(3,2) NOT NULL,
    Leadership DECIMAL(3,2) NOT NULL,
    Goals NVARCHAR(MAX) NULL,
    Achievements NVARCHAR(MAX) NULL,
    AreasForImprovement NVARCHAR(MAX) NULL,
    Comments NVARCHAR(MAX) NULL,
    ReviewDate DATE NOT NULL,
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Performance_Employee FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID),
    CONSTRAINT FK_Performance_Reviewer FOREIGN KEY (ReviewerID) REFERENCES Employees(EmployeeID)
);

-- ========================================
-- Technical Support Agent Tables
-- ========================================

-- IT Assets / Hardware Inventory Table
CREATE TABLE ITAssets (
    AssetID INT PRIMARY KEY IDENTITY(1,1),
    AssetTag NVARCHAR(50) NOT NULL UNIQUE,
    AssetType NVARCHAR(50) NOT NULL, -- Laptop, Desktop, Monitor, Phone, Tablet, etc.
    Manufacturer NVARCHAR(100) NOT NULL,
    Model NVARCHAR(100) NOT NULL,
    SerialNumber NVARCHAR(100) NOT NULL UNIQUE,
    PurchaseDate DATE NOT NULL,
    PurchaseCost DECIMAL(10,2) NOT NULL,
    WarrantyExpiryDate DATE NULL,
    Status NVARCHAR(20) NOT NULL DEFAULT 'Available', -- Available, Assigned, In Repair, Retired
    AssignedToEmployeeID INT NULL,
    AssignmentDate DATE NULL,
    Location NVARCHAR(100) NOT NULL,
    Specifications NVARCHAR(MAX) NULL, -- JSON or text with specs
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    UpdatedAt DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Asset_Employee FOREIGN KEY (AssignedToEmployeeID) REFERENCES Employees(EmployeeID)
);

-- Software Licenses Table
CREATE TABLE SoftwareLicenses (
    LicenseID INT PRIMARY KEY IDENTITY(1,1),
    SoftwareName NVARCHAR(100) NOT NULL,
    LicenseType NVARCHAR(50) NOT NULL, -- User, Device, Site, Subscription
    LicenseKey NVARCHAR(500) NULL,
    Vendor NVARCHAR(100) NOT NULL,
    PurchaseDate DATE NOT NULL,
    ExpiryDate DATE NULL,
    TotalSeats INT NOT NULL,
    UsedSeats INT DEFAULT 0,
    Cost DECIMAL(10,2) NOT NULL,
    RenewalDate DATE NULL,
    Status NVARCHAR(20) NOT NULL DEFAULT 'Active', -- Active, Expired, Cancelled
    AssignedToEmployeeID INT NULL,
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    UpdatedAt DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_License_Employee FOREIGN KEY (AssignedToEmployeeID) REFERENCES Employees(EmployeeID)
);

-- IT Support Tickets Table
CREATE TABLE SupportTickets (
    TicketID INT PRIMARY KEY IDENTITY(1,1),
    TicketNumber NVARCHAR(20) NOT NULL UNIQUE,
    EmployeeID INT NOT NULL,
    Category NVARCHAR(50) NOT NULL, -- Hardware, Software, Network, Access, Other
    Priority NVARCHAR(20) NOT NULL DEFAULT 'Medium', -- Low, Medium, High, Critical
    Status NVARCHAR(20) NOT NULL DEFAULT 'Open', -- Open, In Progress, Resolved, Closed
    Subject NVARCHAR(200) NOT NULL,
    Description NVARCHAR(MAX) NOT NULL,
    AssignedToTechnicianID INT NULL,
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    UpdatedAt DATETIME2 DEFAULT GETDATE(),
    ResolvedAt DATETIME2 NULL,
    ResolutionNotes NVARCHAR(MAX) NULL,
    CONSTRAINT FK_Ticket_Employee FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID),
    CONSTRAINT FK_Ticket_Technician FOREIGN KEY (AssignedToTechnicianID) REFERENCES Employees(EmployeeID)
);

-- Network Configurations Table (Simplified)
CREATE TABLE NetworkConfigurations (
    ConfigID INT PRIMARY KEY IDENTITY(1,1),
    EmployeeID INT NOT NULL,
    IPAddress NVARCHAR(50) NULL,
    MACAddress NVARCHAR(50) NULL,
    VPNAccess BIT DEFAULT 0,
    NetworkDriveAccess NVARCHAR(MAX) NULL, -- JSON list of accessible drives
    WiFiProfile NVARCHAR(100) NULL,
    LastConnected DATETIME2 NULL,
    Status NVARCHAR(20) NOT NULL DEFAULT 'Active',
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    UpdatedAt DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Network_Employee FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);

-- System Permissions / Access Management Table
CREATE TABLE SystemPermissions (
    PermissionID INT PRIMARY KEY IDENTITY(1,1),
    EmployeeID INT NOT NULL,
    SystemName NVARCHAR(100) NOT NULL, -- Azure Portal, CRM, ERP, Email, etc.
    AccessLevel NVARCHAR(50) NOT NULL, -- Read, Write, Admin, Full
    GrantedDate DATE NOT NULL,
    ExpiryDate DATE NULL,
    GrantedBy INT NULL,
    Status NVARCHAR(20) NOT NULL DEFAULT 'Active',
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    UpdatedAt DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Permission_Employee FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID),
    CONSTRAINT FK_Permission_Granter FOREIGN KEY (GrantedBy) REFERENCES Employees(EmployeeID)
);

-- ========================================
-- Indexes for Performance
-- ========================================

CREATE INDEX IX_Employees_Email ON Employees(Email);
CREATE INDEX IX_Employees_Department ON Employees(Department);
CREATE INDEX IX_Benefits_EmployeeID ON Benefits(EmployeeID);
CREATE INDEX IX_Leave_EmployeeID ON LeaveManagement(EmployeeID);
CREATE INDEX IX_Leave_Status ON LeaveManagement(Status);
CREATE INDEX IX_Training_EmployeeID ON TrainingRecords(EmployeeID);
CREATE INDEX IX_Performance_EmployeeID ON PerformanceReviews(EmployeeID);
CREATE INDEX IX_Assets_Status ON ITAssets(Status);
CREATE INDEX IX_Assets_EmployeeID ON ITAssets(AssignedToEmployeeID);
CREATE INDEX IX_Licenses_Status ON SoftwareLicenses(Status);
CREATE INDEX IX_Tickets_EmployeeID ON SupportTickets(EmployeeID);
CREATE INDEX IX_Tickets_Status ON SupportTickets(Status);
CREATE INDEX IX_Network_EmployeeID ON NetworkConfigurations(EmployeeID);
CREATE INDEX IX_Permissions_EmployeeID ON SystemPermissions(EmployeeID);
