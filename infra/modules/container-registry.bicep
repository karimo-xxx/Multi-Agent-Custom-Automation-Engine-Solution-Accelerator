@description('Required. Name of the Azure Container Registry.')
param name string

@description('Optional. Location for the Azure Container Registry.')
param location string = resourceGroup().location

@description('Optional. SKU of the Azure Container Registry.')
@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param sku string = 'Basic'

@description('Optional. Enable admin user that have push / pull permission to the registry.')
param adminUserEnabled bool = true

@description('Optional. Tags for the Azure Container Registry.')
param tags object = {}

@description('Optional. Whether to enable anonymous pull access.')
param anonymousPullEnabled bool = false

@description('Optional. Whether to enable data endpoint (for Premium SKU).')
param dataEndpointEnabled bool = false

@description('Optional. Whether to enable public network access.')
@allowed([
  'Enabled'
  'Disabled'
])
param publicNetworkAccess string = 'Enabled'

@description('Optional. The network rule set for the container registry.')
param networkRuleSet object = {}

@description('Optional. Array of role assignments to create.')
param roleAssignments array = []

var builtInRoleNames = {
  AcrDelete: subscriptionResourceId(
    'Microsoft.Authorization/roleDefinitions',
    'c2f4ef07-c644-48eb-af81-4b1b4947fb11'
  )
  AcrImageSigner: subscriptionResourceId(
    'Microsoft.Authorization/roleDefinitions',
    '6cef56e8-d556-48e5-a04f-b8e64114680f'
  )
  AcrPull: subscriptionResourceId(
    'Microsoft.Authorization/roleDefinitions',
    '7f951dda-4ed3-4680-a7ca-43fe172d538d'
  )
  AcrPush: subscriptionResourceId(
    'Microsoft.Authorization/roleDefinitions',
    '8311e382-0749-4cb8-b61a-304f252e45ec'
  )
  AcrQuarantineReader: subscriptionResourceId(
    'Microsoft.Authorization/roleDefinitions',
    'cdda3590-29a3-44f6-95f2-9f980659eb04'
  )
  AcrQuarantineWriter: subscriptionResourceId(
    'Microsoft.Authorization/roleDefinitions',
    'c8d4ff99-41c3-41a8-9f60-21dfdad59608'
  )
  Contributor: subscriptionResourceId(
    'Microsoft.Authorization/roleDefinitions',
    'b24988ac-6180-42a0-ab88-20f7382dd24c'
  )
  Owner: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8e3af657-a8ff-443c-a75c-2fe8c4bcb635')
  Reader: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'acdd72a7-3385-48ef-bd42-f606fba81ae7')
  'Role Based Access Control Administrator': subscriptionResourceId(
    'Microsoft.Authorization/roleDefinitions',
    'f58310d9-a9f6-439a-9e8d-f62e7b41a168'
  )
  'User Access Administrator': subscriptionResourceId(
    'Microsoft.Authorization/roleDefinitions',
    '18d7d88d-d35e-4fb5-a5c3-7773c20a72d9'
  )
}

var formattedRoleAssignments = [
  for (roleAssignment, index) in (roleAssignments ?? []): union(roleAssignment, {
    roleDefinitionId: builtInRoleNames[?roleAssignment.roleDefinitionIdOrName] ?? (contains(
        roleAssignment.roleDefinitionIdOrName,
        '/providers/Microsoft.Authorization/roleDefinitions/'
      )
      ? roleAssignment.roleDefinitionIdOrName
      : subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleAssignment.roleDefinitionIdOrName))
  })
]

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' = {
  name: name
  location: location
  sku: {
    name: sku
  }
  tags: tags
  properties: {
    adminUserEnabled: adminUserEnabled
    anonymousPullEnabled: anonymousPullEnabled
    dataEndpointEnabled: dataEndpointEnabled
    publicNetworkAccess: publicNetworkAccess
    networkRuleSet: !empty(networkRuleSet) ? networkRuleSet : null
  }
}

resource containerRegistry_roleAssignments 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for (roleAssignment, index) in (formattedRoleAssignments ?? []): {
    name: roleAssignment.?name ?? guid(
      containerRegistry.id,
      roleAssignment.principalId,
      roleAssignment.roleDefinitionId
    )
    properties: {
      roleDefinitionId: roleAssignment.roleDefinitionId
      principalId: roleAssignment.principalId
      description: roleAssignment.?description
      principalType: roleAssignment.?principalType
      condition: roleAssignment.?condition
      conditionVersion: !empty(roleAssignment.?condition) ? (roleAssignment.?conditionVersion ?? '2.0') : null
      delegatedManagedIdentityResourceId: roleAssignment.?delegatedManagedIdentityResourceId
    }
    scope: containerRegistry
  }
]

@description('The resource ID of the container registry.')
output resourceId string = containerRegistry.id

@description('The name of the container registry.')
output name string = containerRegistry.name

@description('The login server of the container registry.')
output loginServer string = containerRegistry.properties.loginServer

@description('The location of the container registry.')
output location string = containerRegistry.location

@description('The resource group of the container registry.')
output resourceGroupName string = resourceGroup().name
