// ========== sql.bicep ========== //
// Azure SQL Server and Database with Managed Identity authentication

@description('Required. The name of the SQL Server.')
param sqlServerName string

@description('Required. The name of the SQL Database.')
param sqlDatabaseName string

@description('Required. Azure region for the SQL resources.')
param location string

@description('Optional. Tags for the resources.')
param tags object = {}

@description('Required. The Azure AD admin object ID (User Assigned Managed Identity).')
param azureAdAdminObjectId string

@description('Required. The Azure AD admin principal name.')
param azureAdAdminPrincipalName string

@description('Optional. SQL Database SKU. Basic tier for demo environments.')
@allowed([
  'Basic'
  'S0'
  'S1'
  'S2'
])
param databaseSku string = 'Basic'

@description('Optional. Enable public network access.')
param enablePublicNetworkAccess bool = true

// SQL Server Resource
resource sqlServer 'Microsoft.Sql/servers@2023-08-01-preview' = {
  name: sqlServerName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    minimalTlsVersion: '1.2'
    publicNetworkAccess: enablePublicNetworkAccess ? 'Enabled' : 'Disabled'
    administrators: {
      administratorType: 'ActiveDirectory'
      azureADOnlyAuthentication: true
      login: azureAdAdminPrincipalName
      sid: azureAdAdminObjectId
      tenantId: tenant().tenantId
      principalType: 'Application'
    }
  }
}

// Firewall rule to allow Azure services
resource allowAzureServices 'Microsoft.Sql/servers/firewallRules@2023-08-01-preview' = {
  parent: sqlServer
  name: 'AllowAllWindowsAzureIps'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// SQL Database Resource
resource sqlDatabase 'Microsoft.Sql/servers/databases@2023-08-01-preview' = {
  parent: sqlServer
  name: sqlDatabaseName
  location: location
  tags: tags
  sku: {
    name: databaseSku
    tier: databaseSku == 'Basic' ? 'Basic' : 'Standard'
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    maxSizeBytes: 2147483648 // 2 GB
    catalogCollation: 'SQL_Latin1_General_CP1_CI_AS'
    zoneRedundant: false
    readScale: 'Disabled'
    requestedBackupStorageRedundancy: 'Local'
  }
}

@description('The resource ID of the SQL Server.')
output sqlServerId string = sqlServer.id

@description('The name of the SQL Server.')
output sqlServerName string = sqlServer.name

@description('The fully qualified domain name of the SQL Server.')
output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName

@description('The resource ID of the SQL Database.')
output sqlDatabaseId string = sqlDatabase.id

@description('The name of the SQL Database.')
output sqlDatabaseName string = sqlDatabase.name

@description('The connection string for Managed Identity authentication.')
output connectionString string = 'Server=tcp:${sqlServer.properties.fullyQualifiedDomainName},1433;Initial Catalog=${sqlDatabaseName};Authentication=Active Directory Default;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;'
