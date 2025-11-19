# Build and Deployment Guide

This guide documents the complete build and deployment process for the Multi-Agent Custom Automation Engine Solution Accelerator.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Backend Build & Deployment](#backend-build--deployment)
- [Frontend Deployment](#frontend-deployment)
- [Post-Deployment Configuration](#post-deployment-configuration)
- [Troubleshooting](#troubleshooting)

---

## Architecture Overview

**Services:**
- **Backend**: Container App (`ca-devpikfl`) - Python FastAPI, Multi-Agent Orchestration
- **Frontend**: App Service (`app-devpikfl`) - Static Web App
- **MCP Server**: Container App (`ca-mcp-devpikfl`) - Model Context Protocol Server
- **Container Registry**: Azure Container Registry (`crdevpikfl.azurecr.io`)
- **AI Services**: Azure AI Foundry (`aif-devpikfl`), Azure AI Search (`srch-devpikfl`)
- **Storage**: Cosmos DB (`cosmos-devpikfl`), Storage Account (`stdevpikfl`)

---

## Backend Build & Deployment

### 1. Build Backend Container Image

Build the backend Docker image in Azure Container Registry (remote build):

```powershell
# Build backend with version tag (e.g., v7, v8, v9)
az acr build --registry crdevpikfl `
  --image macaebackend:latest_v7 `
  --file src/backend/Dockerfile.NoCache `
  src/backend
```

**Build Process:**
- Pulls Python 3.11-slim base image
- Installs UV package manager
- Installs dependencies from `uv.lock` and `pyproject.toml`
- Copies backend source code
- Creates optimized production image
- **Duration**: ~5-8 minutes

**Expected Output:**
```
Queued a build with ID: cg9
Step 1/16 : FROM python:3.11-slim-bullseye AS base
...
Step 16/16 : ENTRYPOINT ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
Successfully tagged crdevpikfl.azurecr.io/macaebackend:latest_v7
```

### 2. Update Backend Container App

After successful build, update the Container App to use the new image:

```powershell
# Update backend to use new image version
az containerapp update `
  --name ca-devpikfl `
  --resource-group rg-karim `
  --image crdevpikfl.azurecr.io/macaebackend:latest_v7
```

**Update Process:**
- Creates new revision (e.g., `ca-devpikfl--0000003`)
- Pulls new container image from ACR
- Updates environment variables from existing configuration
- Performs zero-downtime deployment
- **Duration**: ~2-3 minutes

**Expected Output:**
```json
{
  "properties": {
    "provisioningState": "Succeeded",
    "runningStatus": "Running",
    "latestRevisionName": "ca-devpikfl--0000003",
    "template": {
      "containers": [{
        "image": "crdevpikfl.azurecr.io/macaebackend:latest_v7"
      }]
    }
  }
}
```

### 3. Update Environment Variables (if needed)

Update specific environment variables without rebuilding:

```powershell
# Update single environment variable
az containerapp update `
  --name ca-devpikfl `
  --resource-group rg-karim `
  --set-env-vars AZURE_AI_SEARCH_INDEX_NAME=macae-hybrid-index

# Update multiple environment variables
az containerapp update `
  --name ca-devpikfl `
  --resource-group rg-karim `
  --set-env-vars `
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large `
    AZURE_OPENAI_EMBEDDING_MODEL=text-embedding-3-large `
    AZURE_OPENAI_EMBEDDING_DIMENSIONS=3072
```

### 4. Verify Backend Deployment

Check backend status and configuration:

```powershell
# Check running status
az containerapp show `
  --name ca-devpikfl `
  --resource-group rg-karim `
  --query "properties.runningStatus" -o tsv

# Check current image
az containerapp show `
  --name ca-devpikfl `
  --resource-group rg-karim `
  --query "properties.template.containers[0].image" -o tsv

# Check specific environment variable
az containerapp show `
  --name ca-devpikfl `
  --resource-group rg-karim `
  --query "properties.template.containers[0].env[?name=='AZURE_AI_SEARCH_INDEX_NAME']" -o json

# View recent logs (last 50 lines)
az containerapp logs show `
  --name ca-devpikfl `
  --resource-group rg-karim `
  --tail 50 `
  --follow false
```

---

## Frontend Deployment

### 1. Deploy Frontend via Azure Developer CLI

The frontend is deployed as part of the full solution deployment:

```powershell
# Deploy all services (backend, frontend, mcp)
azd deploy
```

**What happens:**
- Runs `infra/scripts/package_frontend.ps1` (pre-package hook)
- Packages frontend static files to `src/frontend/dist`
- Deploys to App Service (`app-devpikfl`)
- Executes post-deployment hooks (team config upload, data indexing)
- **Duration**: ~1-2 minutes (frontend only)

### 2. Manual Frontend Build (if needed)

If you only want to rebuild frontend assets:

```powershell
# Navigate to frontend directory
cd src/frontend

# Run frontend packaging script
../../infra/scripts/package_frontend.ps1

# Verify dist folder created
ls dist
```

### 3. Access Frontend

Open the deployed frontend application:

```
https://app-devpikfl.azurewebsites.net
```

---

## Post-Deployment Configuration

### 1. Upload Team Configurations

Upload agent team configurations to Cosmos DB:

```powershell
# Using .venv Python environment
.\.venv\Scripts\python.exe infra\scripts\upload_team_config.py `
  "https://ca-devpikfl.gentleocean-9b2e934f.northeurope.azurecontainerapps.io" `
  "data/agent_teams"
```

**What this does:**
- Reads JSON files from `data/agent_teams/` (retail.json, hr.json, marketing.json)
- Uploads team configurations to Cosmos DB `macae` database, `memory` container
- Agents are created dynamically at runtime based on these configurations

**Expected Output:**
```
Scanning directory: data/agent_teams
Uploading file: hr.json
Successfully uploaded team configuration: Human Resources Team (team_id: 00000000-0000-0000-0000-000000000001)
Uploading file: marketing.json
Successfully uploaded team configuration: Product Marketing Team (team_id: 00000000-0000-0000-0000-000000000002)
Uploading file: retail.json
Successfully uploaded team configuration: Retail Customer Success Team (team_id: 00000000-0000-0000-0000-000000000003)
Completed uploading 3 team configurations
```

### 2. Create and Populate Search Index

#### Step 2a: Create Hybrid Search Index

```powershell
.\.venv\Scripts\python.exe infra\scripts\create_hybrid_search_index.py `
  srch-devpikfl `
  macae-hybrid-index
```

**What this creates:**
- Index with 9 fields: id, type, title, content, content_vector (3072 dims), company, created_date, customer_id, order_id
- HNSW vector search algorithm (m=4, efConstruction=400, efSearch=500, cosine similarity)
- Semantic configuration: `altyca-semantic-config` (title + content fields)
- German language analyzer: `de.microsoft`

**Expected Output:**
```
🔧 Creating Hybrid Search Index: macae-hybrid-index
📍 Endpoint: https://srch-devpikfl.search.windows.net
📝 Creating index with configuration:
   - Fields: 9
   - Vector dimensions: 3072 (text-embedding-3-large)
   - Algorithm: HNSW (cosine similarity)
   - Semantic config: altyca-semantic-config
   - Language analyzer: German (de.microsoft)
✅ Index 'macae-hybrid-index' created successfully!
```

#### Step 2b: Ingest Documents with Embeddings

```powershell
.\.venv\Scripts\python.exe infra\scripts\ingest_data_with_embeddings.py `
  srch-devpikfl `
  aif-devpikfl `
  text-embedding-3-large `
  macae-hybrid-index `
  data/datasets
```

**What this does:**
- Loads JSON documents from `data/datasets/`
- Generates embeddings via Azure OpenAI `text-embedding-3-large` (3072 dimensions)
- Uploads documents in batches (10 per batch)
- Handles optional fields (customer_id, order_id)

**Expected Output:**
```
📂 Loading documents from: data/datasets
✅ Loaded 25 documents

🔄 Processing Batch 1/3 (10 documents)
   [1/10] Generating embedding for: Sarah Weber - Premium Kundin... ✅
   ...
   [10/10] Generating embedding for: Loyalty Program Overview... ✅
📤 Uploading batch 1 (10 documents)... ✅ Success

...

📊 Upload Summary:
   ✅ Successfully uploaded: 25 documents
   ❌ Failed: 0 documents

🎯 Index is ready for:
   ✓ Keyword search (BM25 ranking)
   ✓ Vector search (semantic similarity)
   ✓ Hybrid search (keyword + vector)
   ✓ Semantic ranking (Bing re-ranking models)
```

### 3. Delete Azure AI Foundry Agents (After Config Changes)

**When to delete agents:**
- After changing `index_name` in team configuration
- After updating search index structure
- After changing agent tools or instructions

**How to delete:**
1. Navigate to Azure AI Foundry: https://ai.azure.com
2. Select Project: `proj-devpikfl`
3. Go to **Agents** in left menu
4. Delete agents: `CustomerDataAgent`, `OrderDataAgent`, `AnalysisRecommendationAgent`, etc.

**Why:** Agents are cached in Azure AI Foundry with their initial configuration. Deleting forces recreation with updated settings.

---

## Complete Deployment Workflow

### Full Deployment (New Environment)

```powershell
# 1. Provision infrastructure and deploy services
azd up --no-prompt

# 2. Upload team configurations
.\.venv\Scripts\python.exe infra\scripts\upload_team_config.py `
  "https://ca-devpikfl.gentleocean-9b2e934f.northeurope.azurecontainerapps.io" `
  "data/agent_teams"

# 3. Create search index
.\.venv\Scripts\python.exe infra\scripts\create_hybrid_search_index.py `
  srch-devpikfl `
  macae-hybrid-index

# 4. Ingest data with embeddings
.\.venv\Scripts\python.exe infra\scripts\ingest_data_with_embeddings.py `
  srch-devpikfl `
  aif-devpikfl `
  text-embedding-3-large `
  macae-hybrid-index `
  data/datasets
```

### Backend Code Update Deployment

```powershell
# 1. Build new backend image with incremented version
az acr build --registry crdevpikfl `
  --image macaebackend:latest_v8 `
  --file src/backend/Dockerfile.NoCache `
  src/backend

# 2. Update container app with new image
az containerapp update `
  --name ca-devpikfl `
  --resource-group rg-karim `
  --image crdevpikfl.azurecr.io/macaebackend:latest_v8

# 3. Delete agents in AI Foundry (if agent logic changed)
# Manual step via portal: https://ai.azure.com

# 4. Test in frontend
# Open: https://app-devpikfl.azurewebsites.net
```

### Environment Variable Update Only

```powershell
# Update environment variables without rebuild
az containerapp update `
  --name ca-devpikfl `
  --resource-group rg-karim `
  --set-env-vars `
    AZURE_AI_SEARCH_INDEX_NAME=macae-hybrid-index `
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large

# Delete agents in AI Foundry (to pick up new env vars)
# Manual step via portal: https://ai.azure.com
```

---

## Troubleshooting

### Issue: "No index with the name 'X' was found"

**Cause:** Backend environment variable `AZURE_AI_SEARCH_INDEX_NAME` doesn't match actual index name.

**Solution:**
```powershell
# Check current index name in backend
az containerapp show `
  --name ca-devpikfl `
  --resource-group rg-karim `
  --query "properties.template.containers[0].env[?name=='AZURE_AI_SEARCH_INDEX_NAME']" -o json

# Update to correct index name
az containerapp update `
  --name ca-devpikfl `
  --resource-group rg-karim `
  --set-env-vars AZURE_AI_SEARCH_INDEX_NAME=macae-hybrid-index

# Delete agents in AI Foundry to force recreation
```

### Issue: "UNAUTHORIZED: authentication required" (ACR Pull Error)

**Cause:** Container App doesn't have permission to pull images from Azure Container Registry.

**Solution:**
```powershell
# Grant AcrPull permission to managed identity
az role assignment create `
  --assignee bc6dac22-e904-4080-8edb-ea0dd8085f4d `
  --role AcrPull `
  --scope /subscriptions/6009a250-7363-474d-85b6-2fba12522cf0/resourceGroups/rg-karim/providers/Microsoft.ContainerRegistry/registries/crdevpikfl

# Configure registry with managed identity
az containerapp registry set `
  --name ca-devpikfl `
  --resource-group rg-karim `
  --server crdevpikfl.azurecr.io `
  --identity /subscriptions/6009a250-7363-474d-85b6-2fba12522cf0/resourcegroups/rg-karim/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id-devpikfl
```

### Issue: Agents use old configuration after update

**Cause:** Agents are cached in Azure AI Foundry with initial configuration.

**Solution:**
1. Navigate to https://ai.azure.com
2. Select Project: `proj-devpikfl`
3. Go to **Agents** → Delete all relevant agents
4. Start new conversation in frontend → Agents will be recreated automatically

### Issue: Backend logs show errors

**Check logs:**
```powershell
# View last 50 log lines
az containerapp logs show `
  --name ca-devpikfl `
  --resource-group rg-karim `
  --tail 50 `
  --follow false

# Follow logs in real-time
az containerapp logs show `
  --name ca-devpikfl `
  --resource-group rg-karim `
  --follow true
```

### Issue: Frontend shows old version after deployment

**Solution:**
```powershell
# Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
# Or clear browser cache

# Verify deployment timestamp in Azure Portal
az webapp show `
  --name app-devpikfl `
  --resource-group rg-karim `
  --query "lastModifiedTimeUtc" -o tsv
```

---

## Quick Reference Commands

### Get Environment Values
```powershell
azd env get-values
```

### Check All Service Status
```powershell
# Backend status
az containerapp show --name ca-devpikfl --resource-group rg-karim --query "properties.runningStatus" -o tsv

# Frontend status
az webapp show --name app-devpikfl --resource-group rg-karim --query "state" -o tsv

# Search index document count
az search index show --service-name srch-devpikfl --name macae-hybrid-index --query "fields[0]" -o json
```

### Test Hybrid Search (Local Script)
```powershell
.\.venv\Scripts\python.exe scripts\test_hybrid_search.py `
  srch-devpikfl `
  aif-devpikfl `
  text-embedding-3-large `
  macae-hybrid-index
```

---

## Version History

- **v7** (2025-11-19): Hybrid Search + Semantic Ranking implementation
  - Added embedding generation with text-embedding-3-large
  - Created macae-hybrid-index with 3072-dimensional vectors
  - Updated reasoning_search.py with VectorizedQuery support
  - Configured semantic ranking with altyca-semantic-config
  
- **v3** (Previous): Initial deployment with keyword-only search
  - Simple BM25 keyword search
  - Index: sample-dataset-index

---

## Additional Resources

- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure AI Search Hybrid Search](https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview)
- [Azure Developer CLI (azd)](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/)
- [Dockerfile.NoCache Documentation](../src/backend/Dockerfile.NoCache)
