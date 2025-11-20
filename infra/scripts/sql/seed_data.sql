-- ========================================
-- MACAE HR Database - Sample Data
-- Demo data for HR and Technical Support scenarios
-- ========================================

-- ========================================
-- Insert Sample Employees
-- ========================================

INSERT INTO Employees (FirstName, LastName, Email, Department, Position, HireDate, ManagerID, Salary, EmploymentStatus) VALUES
-- Management
('Sarah', 'Johnson', 'sarah.johnson@macae.com', 'Management', 'CEO', '2020-01-15', NULL, 250000.00, 'Active'),
('Michael', 'Chen', 'michael.chen@macae.com', 'Management', 'CTO', '2020-03-01', 1, 180000.00, 'Active'),
('Emily', 'Rodriguez', 'emily.rodriguez@macae.com', 'Management', 'VP Human Resources', '2020-05-10', 1, 150000.00, 'Active'),

-- HR Team
('David', 'Williams', 'david.williams@macae.com', 'Human Resources', 'HR Manager', '2021-01-15', 3, 95000.00, 'Active'),
('Jessica', 'Smith', 'jessica.smith@macae.com', 'Human Resources', 'HR Specialist', '2024-11-01', 4, 65000.00, 'Active'),
('Amanda', 'Brown', 'amanda.brown@macae.com', 'Human Resources', 'Benefits Coordinator', '2022-06-01', 4, 70000.00, 'Active'),

-- IT Team
('Robert', 'Martinez', 'robert.martinez@macae.com', 'IT', 'IT Manager', '2020-08-15', 2, 120000.00, 'Active'),
('Kevin', 'Anderson', 'kevin.anderson@macae.com', 'IT', 'Senior Systems Engineer', '2021-03-01', 7, 95000.00, 'Active'),
('Lisa', 'Taylor', 'lisa.taylor@macae.com', 'IT', 'Network Administrator', '2022-01-10', 7, 85000.00, 'Active'),
('James', 'Thomas', 'james.thomas@macae.com', 'IT', 'Help Desk Technician', '2023-04-15', 7, 55000.00, 'Active'),

-- Engineering Team
('Jennifer', 'Garcia', 'jennifer.garcia@macae.com', 'Engineering', 'Engineering Manager', '2020-11-01', 2, 140000.00, 'Active'),
('Daniel', 'Lee', 'daniel.lee@macae.com', 'Engineering', 'Senior Software Engineer', '2021-05-15', 11, 110000.00, 'Active'),
('Maria', 'Lopez', 'maria.lopez@macae.com', 'Engineering', 'Software Engineer', '2022-09-01', 11, 95000.00, 'Active'),
('Christopher', 'White', 'christopher.white@macae.com', 'Engineering', 'Junior Developer', '2023-06-01', 11, 75000.00, 'Active'),

-- Sales Team
('Patricia', 'Harris', 'patricia.harris@macae.com', 'Sales', 'Sales Director', '2021-02-01', 1, 130000.00, 'Active'),
('Thomas', 'Clark', 'thomas.clark@macae.com', 'Sales', 'Sales Manager', '2021-08-15', 15, 100000.00, 'Active'),
('Nancy', 'Lewis', 'nancy.lewis@macae.com', 'Sales', 'Account Executive', '2022-11-01', 16, 80000.00, 'Active');

-- ========================================
-- Insert Benefits Data
-- ========================================

INSERT INTO Benefits (EmployeeID, BenefitType, Provider, PlanName, MonthlyContribution, EnrollmentDate, Status) VALUES
(1, 'Health Insurance', 'BlueCross BlueShield', 'Premium PPO', 450.00, '2020-01-15', 'Active'),
(1, '401k', 'Fidelity', 'Executive Plan', 1500.00, '2020-01-15', 'Active'),
(2, 'Health Insurance', 'BlueCross BlueShield', 'Premium PPO', 450.00, '2020-03-01', 'Active'),
(2, '401k', 'Fidelity', 'Executive Plan', 1200.00, '2020-03-01', 'Active'),
(5, 'Health Insurance', 'BlueCross BlueShield', 'Standard HMO', 250.00, '2024-11-01', 'Active'),
(5, 'Dental Insurance', 'Delta Dental', 'Basic Plan', 50.00, '2024-11-01', 'Active'),
(8, 'Health Insurance', 'BlueCross BlueShield', 'Premium PPO', 350.00, '2021-03-01', 'Active'),
(8, '401k', 'Fidelity', 'Standard Plan', 800.00, '2021-03-01', 'Active'),
(12, 'Health Insurance', 'BlueCross BlueShield', 'Standard HMO', 275.00, '2021-05-15', 'Active'),
(12, '401k', 'Fidelity', 'Standard Plan', 900.00, '2021-05-15', 'Active');

-- ========================================
-- Insert Leave Management Data
-- ========================================

INSERT INTO LeaveManagement (EmployeeID, LeaveType, StartDate, EndDate, TotalDays, Status, RequestDate, ApprovedBy, ApprovalDate, Reason) VALUES
(5, 'Vacation', '2024-12-20', '2024-12-31', 10, 'Approved', '2024-11-01', 4, '2024-11-05', 'Winter holidays'),
(12, 'Vacation', '2025-01-15', '2025-01-19', 5, 'Pending', '2024-11-15', NULL, NULL, 'Personal trip'),
(14, 'Sick Leave', '2024-11-10', '2024-11-12', 3, 'Approved', '2024-11-09', 11, '2024-11-09', 'Medical appointment'),
(17, 'Vacation', '2025-02-10', '2025-02-21', 10, 'Pending', '2024-11-18', NULL, NULL, 'Family vacation'),
(8, 'Personal', '2024-12-15', '2024-12-15', 1, 'Approved', '2024-11-10', 7, '2024-11-11', 'Personal matter');

-- ========================================
-- Insert Training Records
-- ========================================

INSERT INTO TrainingRecords (EmployeeID, TrainingName, TrainingCategory, Provider, StartDate, EndDate, Status, CompletionPercentage, CertificationAwarded, Cost) VALUES
(5, 'HR Compliance Training 2024', 'Compliance', 'SHRM', '2024-11-05', '2024-11-10', 'Completed', 100, 1, 500.00),
(8, 'Azure Administrator Certification', 'Technical', 'Microsoft Learn', '2024-10-01', '2024-11-30', 'In Progress', 75, 0, 1200.00),
(10, 'IT Service Management Fundamentals', 'Technical', 'ITIL', '2024-11-01', '2024-11-15', 'Completed', 100, 1, 800.00),
(12, 'Advanced Python Programming', 'Technical', 'Udemy', '2024-09-01', '2024-10-15', 'Completed', 100, 1, 350.00),
(14, 'Introduction to AI Development', 'Technical', 'Coursera', '2024-11-01', '2024-12-15', 'In Progress', 40, 0, 450.00),
(17, 'Sales Leadership Masterclass', 'Leadership', 'LinkedIn Learning', '2024-10-15', '2024-11-30', 'In Progress', 60, 0, 600.00);

-- ========================================
-- Insert Performance Reviews
-- ========================================

INSERT INTO PerformanceReviews (EmployeeID, ReviewPeriodStart, ReviewPeriodEnd, ReviewerID, OverallRating, TechnicalSkills, Communication, Teamwork, Leadership, Goals, Achievements, AreasForImprovement, ReviewDate) VALUES
(12, '2024-01-01', '2024-06-30', 11, 4.50, 4.75, 4.25, 4.50, 4.00, 
'Complete Azure migration project, mentor junior developers', 
'Successfully led team migration to microservices architecture, improved system performance by 40%', 
'Continue developing leadership skills, focus on project planning', '2024-07-15'),

(14, '2024-01-01', '2024-06-30', 11, 3.75, 3.50, 4.00, 4.25, 3.00, 
'Complete at least 3 major features, improve code quality', 
'Delivered two critical features ahead of schedule, improved test coverage', 
'Need to improve debugging skills and ask questions earlier', '2024-07-18'),

(8, '2024-01-01', '2024-06-30', 7, 4.75, 5.00, 4.50, 4.75, 4.50, 
'Implement zero-trust security model, reduce ticket resolution time', 
'Implemented comprehensive security framework, reduced average ticket time by 35%', 
'Excellent performance, continue knowledge sharing with team', '2024-07-20');

-- ========================================
-- Insert IT Assets
-- ========================================

INSERT INTO ITAssets (AssetTag, AssetType, Manufacturer, Model, SerialNumber, PurchaseDate, PurchaseCost, WarrantyExpiryDate, Status, AssignedToEmployeeID, AssignmentDate, Location, Specifications) VALUES
('MACAE-LT-001', 'Laptop', 'Dell', 'Latitude 7440', 'DL7440-2024-001', '2024-01-15', 1899.99, '2027-01-15', 'Assigned', 5, '2024-11-01', 'Seattle Office', '{"cpu": "Intel i7-1365U", "ram": "32GB", "storage": "1TB SSD"}'),
('MACAE-LT-002', 'Laptop', 'Lenovo', 'ThinkPad X1 Carbon', 'TP-X1C-2024-002', '2024-02-20', 2299.99, '2027-02-20', 'Assigned', 8, '2024-02-25', 'Seattle Office', '{"cpu": "Intel i7-1355U", "ram": "32GB", "storage": "512GB SSD"}'),
('MACAE-LT-003', 'Laptop', 'Apple', 'MacBook Pro 14', 'MBP14-2024-003', '2024-03-10', 2499.99, '2027-03-10', 'Assigned', 12, '2024-03-15', 'Seattle Office', '{"cpu": "M3 Pro", "ram": "32GB", "storage": "1TB SSD"}'),
('MACAE-LT-004', 'Laptop', 'Dell', 'Latitude 5540', 'DL5540-2024-004', '2024-10-15', 1299.99, '2027-10-15', 'Available', NULL, NULL, 'IT Storage', '{"cpu": "Intel i5-1335U", "ram": "16GB", "storage": "512GB SSD"}'),
('MACAE-LT-005', 'Laptop', 'HP', 'EliteBook 840', 'HP-EB840-2024-005', '2024-11-01', 1599.99, '2027-11-01', 'Available', NULL, NULL, 'IT Storage', '{"cpu": "Intel i7-1355U", "ram": "16GB", "storage": "512GB SSD"}'),
('MACAE-MON-001', 'Monitor', 'Dell', 'UltraSharp U2723DE', 'DL-U27-2024-001', '2024-01-20', 549.99, '2027-01-20', 'Assigned', 5, '2024-11-01', 'Seattle Office', '{"size": "27 inch", "resolution": "2560x1440"}'),
('MACAE-MON-002', 'Monitor', 'LG', '27UP850-W', 'LG-27UP-2024-002', '2024-02-15', 499.99, '2027-02-15', 'Assigned', 12, '2024-03-15', 'Seattle Office', '{"size": "27 inch", "resolution": "3840x2160"}'),
('MACAE-PHN-001', 'Phone', 'Apple', 'iPhone 15 Pro', 'IP15P-2024-001', '2024-06-01', 1199.99, '2025-06-01', 'Assigned', 1, '2024-06-05', 'Seattle Office', '{"storage": "256GB", "color": "Natural Titanium"}'),
('MACAE-TAB-001', 'Tablet', 'Apple', 'iPad Pro 12.9', 'IPADP-2024-001', '2024-07-10', 1299.99, '2025-07-10', 'Assigned', 15, '2024-07-15', 'Seattle Office', '{"storage": "512GB", "connectivity": "WiFi + Cellular"}');

-- ========================================
-- Insert Software Licenses
-- ========================================

INSERT INTO SoftwareLicenses (SoftwareName, LicenseType, LicenseKey, Vendor, PurchaseDate, ExpiryDate, TotalSeats, UsedSeats, Cost, RenewalDate, Status, AssignedToEmployeeID) VALUES
('Microsoft 365 E5', 'User', NULL, 'Microsoft', '2024-01-01', '2025-01-01', 50, 17, 25000.00, '2025-01-01', 'Active', NULL),
('Adobe Creative Cloud', 'User', 'ADOBE-CC-2024-XXXX', 'Adobe', '2024-01-15', '2025-01-15', 10, 5, 6000.00, '2025-01-15', 'Active', NULL),
('JetBrains IntelliJ IDEA', 'User', 'JETBRAINS-2024-YYYY', 'JetBrains', '2024-02-01', '2025-02-01', 15, 8, 3750.00, '2025-02-01', 'Active', NULL),
('Slack Enterprise', 'Site', NULL, 'Slack', '2024-01-01', '2025-01-01', 100, 52, 15000.00, '2025-01-01', 'Active', NULL),
('GitHub Enterprise', 'Site', NULL, 'GitHub', '2024-01-01', '2025-01-01', 50, 25, 10500.00, '2025-01-01', 'Active', NULL),
('Zoom Business Plus', 'User', NULL, 'Zoom', '2024-01-01', '2025-01-01', 25, 17, 4500.00, '2025-01-01', 'Active', NULL),
('Visual Studio Enterprise', 'User', 'VS-ENT-2024-ZZZZ', 'Microsoft', '2024-03-01', '2025-03-01', 20, 12, 14000.00, '2025-03-01', 'Active', 12);

-- ========================================
-- Insert Support Tickets
-- ========================================

INSERT INTO SupportTickets (TicketNumber, EmployeeID, Category, Priority, Status, Subject, Description, AssignedToTechnicianID, CreatedAt, UpdatedAt, ResolvedAt, ResolutionNotes) VALUES
('TICK-2024-001', 5, 'Hardware', 'High', 'Resolved', 'Laptop keyboard not working', 
'My laptop keyboard suddenly stopped working. External keyboard works fine. Need urgent replacement.', 
10, '2024-11-15 09:30:00', '2024-11-15 14:20:00', '2024-11-15 14:20:00', 
'Diagnosed hardware failure. Replaced keyboard. Laptop tested and working properly.'),

('TICK-2024-002', 14, 'Software', 'Medium', 'In Progress', 'VS Code extension not loading', 
'Cannot install Python extension in VS Code. Getting error "Extension activation failed".', 
10, '2024-11-18 11:15:00', '2024-11-18 15:30:00', NULL, NULL),

('TICK-2024-003', 17, 'Access', 'High', 'Open', 'Cannot access CRM system', 
'Getting "Access Denied" error when trying to log into Salesforce CRM. Need urgent access for client meeting.', 
NULL, '2024-11-19 08:00:00', '2024-11-19 08:00:00', NULL, NULL),

('TICK-2024-004', 13, 'Network', 'Low', 'Resolved', 'VPN connection slow', 
'VPN connection has been very slow for the past week. Takes forever to access network drives.', 
9, '2024-11-10 14:20:00', '2024-11-12 10:15:00', '2024-11-12 10:15:00', 
'Identified routing issue. Updated VPN configuration. Speed improved significantly.'),

('TICK-2024-005', 12, 'Hardware', 'Medium', 'Open', 'Request for additional monitor', 
'Would like to request a second external monitor for my workstation to improve productivity.', 
NULL, '2024-11-19 10:00:00', '2024-11-19 10:00:00', NULL, NULL);

-- ========================================
-- Insert Network Configurations
-- ========================================

INSERT INTO NetworkConfigurations (EmployeeID, IPAddress, MACAddress, VPNAccess, NetworkDriveAccess, WiFiProfile, LastConnected, Status) VALUES
(5, '192.168.1.105', '00:1B:44:11:3A:B7', 1, '["\\\\fileserver\\HR", "\\\\fileserver\\Shared"]', 'MACAE-Corp-WiFi', '2024-11-19 08:30:00', 'Active'),
(8, '192.168.1.108', '00:1B:44:11:3A:C2', 1, '["\\\\fileserver\\IT", "\\\\fileserver\\Shared", "\\\\fileserver\\Engineering"]', 'MACAE-Corp-WiFi', '2024-11-19 07:45:00', 'Active'),
(12, '192.168.1.112', '00:1B:44:11:3A:D5', 1, '["\\\\fileserver\\Engineering", "\\\\fileserver\\Shared"]', 'MACAE-Corp-WiFi', '2024-11-19 09:15:00', 'Active'),
(14, '192.168.1.114', '00:1B:44:11:3A:E8', 1, '["\\\\fileserver\\Engineering", "\\\\fileserver\\Shared"]', 'MACAE-Corp-WiFi', '2024-11-18 16:30:00', 'Active'),
(17, '192.168.1.117', '00:1B:44:11:3A:F2', 1, '["\\\\fileserver\\Sales", "\\\\fileserver\\Shared"]', 'MACAE-Corp-WiFi', '2024-11-19 08:00:00', 'Active');

-- ========================================
-- Insert System Permissions
-- ========================================

INSERT INTO SystemPermissions (EmployeeID, SystemName, AccessLevel, GrantedDate, ExpiryDate, GrantedBy, Status) VALUES
(5, 'HR Management System', 'Full', '2024-11-01', NULL, 4, 'Active'),
(5, 'Payroll System', 'Read', '2024-11-01', NULL, 4, 'Active'),
(5, 'Microsoft 365', 'Write', '2024-11-01', NULL, 7, 'Active'),
(8, 'Azure Portal', 'Admin', '2021-03-01', NULL, 2, 'Active'),
(8, 'Active Directory', 'Admin', '2021-03-01', NULL, 2, 'Active'),
(8, 'Microsoft 365 Admin', 'Admin', '2021-03-01', NULL, 2, 'Active'),
(10, 'ServiceNow', 'Write', '2023-04-15', NULL, 7, 'Active'),
(10, 'Active Directory', 'Read', '2023-04-15', NULL, 7, 'Active'),
(12, 'Azure DevOps', 'Write', '2021-05-15', NULL, 11, 'Active'),
(12, 'GitHub', 'Write', '2021-05-15', NULL, 11, 'Active'),
(12, 'Azure Portal', 'Write', '2021-05-15', NULL, 2, 'Active'),
(14, 'Azure DevOps', 'Read', '2023-06-01', NULL, 11, 'Active'),
(14, 'GitHub', 'Write', '2023-06-01', NULL, 11, 'Active'),
(17, 'Salesforce CRM', 'Write', '2022-11-01', '2025-11-01', 15, 'Active'),
(17, 'Microsoft 365', 'Write', '2022-11-01', NULL, 7, 'Active');
