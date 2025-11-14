# Fabric Data Agent Backend Integration Guide

**Status:** 🔴 Not Implemented (✅ API Validated via Microsoft Learn)  
**Priority:** High  
**Estimated Effort:** 6-8 hours (inkl. Azure AI Foundry Connection Setup)

---

## 🎯 **Executive Summary**

Dieses Dokument beschreibt die **vollständige Backend-Integration** für Fabric Data Agent in das Multi-Agent Custom Automation Engine System. Die Integration ermöglicht es Azure AI Foundry Agents (CustomerDataAgent, OrderDataAgent), den Fabric Data Agent "RetailCustomerSuccessAgent" zu nutzen, um Queries gegen RetailWarehouse und RetailLakehouse auszuführen.

### **Was wird erreicht:**
- ✅ CustomerDataAgent und OrderDataAgent können Fabric Data Agent aufrufen
- ✅ Identity Passthrough (On-Behalf-Of) für sichere Datenzugriffe
- ✅ Hybrid-Queries: Warehouse (quantitative) + Lakehouse (qualitative)
- ✅ Keine RAG-Index mehr erforderlich (ersetzt durch Fabric Data Agent)

### **API Validation:**
- ✅ **Microsoft Learn MCP** verwendet zur Validierung aller Code-Patterns
- ✅ **FabricTool API bestätigt:** `FabricTool(connection_id=conn_id)` + `.definitions`
- ✅ **Code-Samples aus Microsoft Docs** als Referenz verwendet
- ✅ **SDK Version:** `azure-ai-agents>=1.1.0b3` (Preview, aber stable API)

### **Machbarkeit: ✅ VALIDIERT**
Die Implementation ist **technisch machbar** und folgt offiziellen Microsoft Patterns. Alle API-Calls sind in Microsoft Learn dokumentiert und durch Code-Samples belegt.

---

## 📋 Current State

### ✅ Completed:
- `retail.json` konfiguriert mit:
  - `use_fabric: true`
  - `fabric_connection_id: "RetailCustomerSuccessAgent"`
  - `workspace_id: "adbf7690-4c8b-4ba2-acbf-9cedcb6a2bfe"`
  - `artifact_id: "79a39492-2460-47d9-abb6-5573e562ccf6"`
- System messages für CustomerDataAgent und OrderDataAgent optimiert
- Fabric Data Agent published und verfügbar
- **Microsoft Learn API validiert:** FabricTool API bestätigt mit Code-Samples

### ❌ Missing:
- Backend unterstützt `use_fabric` Flag noch NICHT
- FabricTool aus `azure-ai-agents` SDK nicht integriert
- Modelle (`AgentConfig`, `TeamConfiguration`) fehlen Fabric-Felder
- **KRITISCH:** Azure AI Foundry Connection muss erstellt werden (siehe Prerequisites)

### ⚠️ Prerequisites (aus Microsoft Docs):
1. **Azure AI Foundry Connection erstellen:**
   - Im Azure AI Foundry Portal → Project → "Connected Resources"
   - Add Connection → Type: "Fabric Data Agent"
   - Custom Keys:
     - `workspace-id`: `adbf7690-4c8b-4ba2-acbf-9cedcb6a2bfe`
     - `artifact-id`: `79a39492-2460-47d9-abb6-5573e562ccf6`
   - Connection Name: z.B. `RetailCustomerSuccessAgent-Connection`
   - **Resultierende connection_id:** `/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.MachineLearningServices/workspaces/{project}/connections/RetailCustomerSuccessAgent-Connection`

2. **User muss AI Developer Role haben:**
   - Developers und End-Users benötigen mindestens `AI Developer` RBAC Role in Azure AI Foundry

3. **Fabric Tenant Settings aktiviert:**
   - Fabric data agent tenant settings
   - Cross-geo processing for AI
   - Cross-geo storing for AI

---

## 🔧 Required Code Changes

### **1. Update Data Models**

**File:** `src/backend/common/models/messages_kernel.py`

**Current:**
```python
class AgentConfig(KernelBaseModel):
    """Represents an agent configuration."""
    
    input_key: str
    type: str
    name: str
    deployment_name: str
    system_message: str = ""
    description: str = ""
    icon: str
    index_name: str = ""
    use_rag: bool = False
    use_mcp: bool = False
    use_bing: bool = False
    use_reasoning: bool = False
    coding_tools: bool = False
```

**Required Update:**
```python
class AgentConfig(KernelBaseModel):
    """Represents an agent configuration."""
    
    input_key: str
    type: str
    name: str
    deployment_name: str
    system_message: str = ""
    description: str = ""
    icon: str
    index_name: str = ""
    use_rag: bool = False
    use_mcp: bool = False
    use_bing: bool = False
    use_reasoning: bool = False
    use_fabric: bool = False  # ← NEW
    fabric_connection_id: str = ""  # ← NEW
    workspace_id: str = ""  # ← NEW
    artifact_id: str = ""  # ← NEW
    coding_tools: bool = False
```

---

### **2. Create FabricConfig Class**

**File:** `src/backend/v3/magentic_agents/models/agent_models.py`

**Add new class:**
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class FabricConfig:
    """Configuration for Fabric Data Agent integration."""
    
    fabric_connection_id: str
    workspace_id: str
    artifact_id: str
    endpoint_url: str = "https://api.fabric.microsoft.com/v1"
    
    @classmethod
    def from_agent_config(cls, agent_obj) -> Optional["FabricConfig"]:
        """Create FabricConfig from agent configuration object."""
        if not getattr(agent_obj, "use_fabric", False):
            return None
        
        workspace_id = getattr(agent_obj, "workspace_id", "")
        artifact_id = getattr(agent_obj, "artifact_id", "")
        fabric_connection_id = getattr(agent_obj, "fabric_connection_id", "")
        
        if not all([workspace_id, artifact_id, fabric_connection_id]):
            raise ValueError(
                f"Agent '{agent_obj.name}' has use_fabric=True but missing required fields: "
                f"workspace_id={workspace_id}, artifact_id={artifact_id}, "
                f"fabric_connection_id={fabric_connection_id}"
            )
        
        return cls(
            fabric_connection_id=fabric_connection_id,
            workspace_id=workspace_id,
            artifact_id=artifact_id
        )
    
    def get_endpoint_url(self) -> str:
        """Get full Fabric Data Agent endpoint URL."""
        return f"{self.endpoint_url}/workspaces/{self.workspace_id}/aiskills/{self.artifact_id}/aiassistant/openai"
```

---

### **3. Update Agent Factory**

**File:** `src/backend/v3/magentic_agents/magentic_agent_factory.py`

**Current lines 88-93:**
```python
# Only create configs for explicitly requested capabilities
search_config = (
    SearchConfig.from_env() if getattr(agent_obj, "use_rag", False) else None
)
mcp_config = (
    MCPConfig.from_env() if getattr(agent_obj, "use_mcp", False) else None
)
```

**Required Update:**
```python
from v3.magentic_agents.models.agent_models import FabricConfig, MCPConfig, SearchConfig

# Only create configs for explicitly requested capabilities
search_config = (
    SearchConfig.from_env() if getattr(agent_obj, "use_rag", False) else None
)
mcp_config = (
    MCPConfig.from_env() if getattr(agent_obj, "use_mcp", False) else None
)
fabric_config = (
    FabricConfig.from_agent_config(agent_obj) if getattr(agent_obj, "use_fabric", False) else None
)
```

**Update FoundryAgentTemplate instantiation (line ~115):**
```python
else:
    agent = FoundryAgentTemplate(
        agent_name=agent_obj.name,
        agent_description=getattr(agent_obj, "description", ""),
        agent_instructions=getattr(agent_obj, "system_message", ""),
        model_deployment_name=deployment_name,
        enable_code_interpreter=getattr(agent_obj, "coding_tools", False),
        mcp_config=mcp_config,
        search_config=search_config,
        fabric_config=fabric_config,  # ← NEW
    )
```

---

### **4. Update FoundryAgentTemplate**

**File:** `src/backend/v3/magentic_agents/foundry_agent.py`

**Current `__init__` signature:**
```python
def __init__(
    self,
    agent_name: str,
    agent_description: str,
    agent_instructions: str,
    model_deployment_name: str,
    enable_code_interpreter: bool = False,
    search_config: Optional[SearchConfig] = None,
    mcp_config: Optional[MCPConfig] = None,
):
```

**Required Update:**
```python
from typing import Optional
from v3.magentic_agents.models.agent_models import FabricConfig, MCPConfig, SearchConfig

def __init__(
    self,
    agent_name: str,
    agent_description: str,
    agent_instructions: str,
    model_deployment_name: str,
    enable_code_interpreter: bool = False,
    search_config: Optional[SearchConfig] = None,
    mcp_config: Optional[MCPConfig] = None,
    fabric_config: Optional[FabricConfig] = None,  # ← NEW
):
    # ... existing code ...
    
    self._search_config = search_config
    self._mcp_config = mcp_config
    self._fabric_config = fabric_config  # ← NEW
```

**Add FabricTool integration in `open()` method:**

```python
async def open(self):
    """Initialize the agent and its tools."""
    # Import FabricTool from azure.ai.agents.models
    from azure.ai.agents.models import FabricTool
    
    # Code Interpreter Tool
    if self._enable_code_interpreter:
        tools.append(CodeInterpreterTool())
    
    # RAG/Search Tool
    if self._search_config:
        tools.append(AzureAISearchTool(
            index_name=self._search_config.index_name,
            # ... existing config ...
        ))
    
    # MCP Tool
    if self._mcp_config:
        # ... existing MCP setup ...
        pass
    
    # Fabric Data Agent Tool (NEW)
    if self._fabric_config:
        try:
            # IMPORTANT: connection_id format from Microsoft Docs:
            # /subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/
            # Microsoft.MachineLearningServices/workspaces/{project-name}/connections/{connection-name}
            #
            # For Fabric Data Agent published endpoint, the connection_id should be created
            # in Azure AI Foundry Portal under "Connected Resources"
            
            self.logger.info(
                f"Initializing FabricTool for agent '{self._agent_name}' with "
                f"connection_id='{self._fabric_config.fabric_connection_id}'"
            )
            
            # Create FabricTool with connection_id
            # API validated from Microsoft Learn:
            # https://learn.microsoft.com/en-us/fabric/data-science/data-agent-foundry
            fabric_tool = FabricTool(connection_id=self._fabric_config.fabric_connection_id)
            
            # CRITICAL: FabricTool returns .definitions property for agent tools
            # This is the official API pattern from Microsoft documentation
            if not hasattr(fabric_tool, 'definitions'):
                raise AttributeError(
                    "FabricTool does not have 'definitions' attribute. "
                    "Ensure you're using azure-ai-agents >= 1.1.0b3"
                )
            
        except ImportError:
            self.logger.error(
                "FabricTool requires 'azure-ai-agents' SDK. "
                "Install with: pip install azure-ai-agents>=1.1.0b3"
            )
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize FabricTool: {e}")
            raise
    
    # Create AI Agent with tools
    # API Pattern from Microsoft Docs:
    # agent = project_client.agents.create_agent(
    #     model=deployment_name,
    #     name=agent_name,
    #     instructions=instructions,
    #     tools=fabric_tool.definitions,  # ← Use .definitions property
    # )
    
    # Collect all tool definitions
    all_tools = []
    if self._enable_code_interpreter:
        all_tools.extend(code_interpreter_tool.definitions)
    if self._search_config:
        all_tools.extend(search_tool.definitions)
    if self._mcp_config:
        all_tools.extend(mcp_tool.definitions)
    if self._fabric_config:
        all_tools.extend(fabric_tool.definitions)  # ← Add Fabric tool definitions
    
    self._ai_agent = self._client.agents.create_agent(
        model=self._model_deployment_name,
        name=self._agent_name,
        instructions=self._agent_instructions,
        tools=all_tools,  # ← Pass combined tool definitions
    )
    
    self.logger.info(f"Successfully created agent '{self._agent_name}' with {len(all_tools)} tools")
```

---

### **5. Update Team Service**

**File:** `src/backend/v3/common/services/team_service.py`

**Current lines 140-145:**
```python
agent_config = AgentConfig(
    input_key=agent_data.get("input_key", ""),
    type=agent_data.get("type", ""),
    name=agent_data.get("name"),
    deployment_name=agent_data.get("deployment_name", ""),
    use_rag=agent_data.get("use_rag", False),
    use_mcp=agent_data.get("use_mcp", False),
    use_bing=agent_data.get("use_bing", False),
    # ... more fields ...
)
```

**Required Update:**
```python
agent_config = AgentConfig(
    input_key=agent_data.get("input_key", ""),
    type=agent_data.get("type", ""),
    name=agent_data.get("name"),
    deployment_name=agent_data.get("deployment_name", ""),
    use_rag=agent_data.get("use_rag", False),
    use_mcp=agent_data.get("use_mcp", False),
    use_bing=agent_data.get("use_bing", False),
    use_fabric=agent_data.get("use_fabric", False),  # ← NEW
    fabric_connection_id=agent_data.get("fabric_connection_id", ""),  # ← NEW
    workspace_id=agent_data.get("workspace_id", ""),  # ← NEW
    artifact_id=agent_data.get("artifact_id", ""),  # ← NEW
    # ... more fields ...
)
```

---

### **6. Update Agents Service**

**File:** `src/backend/v3/common/services/agents_service.py`

**Lines 81-82 und 96-97:** Füge Fabric-Felder hinzu

```python
# Line ~81 (when converting from object to dict)
"use_rag": getattr(a, "use_rag", False),
"use_mcp": getattr(a, "use_mcp", False),
"use_fabric": getattr(a, "use_fabric", False),  # ← NEW
"fabric_connection_id": getattr(a, "fabric_connection_id", ""),  # ← NEW
"workspace_id": getattr(a, "workspace_id", ""),  # ← NEW
"artifact_id": getattr(a, "artifact_id", ""),  # ← NEW

# Line ~96 (when converting from dict)
"use_rag": a.get("use_rag", False),
"use_mcp": a.get("use_mcp", False),
"use_fabric": a.get("use_fabric", False),  # ← NEW
"fabric_connection_id": a.get("fabric_connection_id", ""),  # ← NEW
"workspace_id": a.get("workspace_id", ""),  # ← NEW
"artifact_id": a.get("artifact_id", ""),  # ← NEW
```

---

## 📦 Required Dependencies

**File:** `requirements.txt` or `pyproject.toml`

```txt
azure-ai-agents>=1.1.0b3  # Preview version with FabricTool support
azure-ai-projects>=1.0.0  # AIProjectClient for Azure AI Foundry
azure-identity>=1.15.0    # DefaultAzureCredential for authentication
```

**Installation:**
```bash
pip install azure-ai-agents azure-ai-projects azure-identity
```

**Important from Microsoft Docs:**
> "You should use the latest beta/preview version of the Azure AI Agents Python SDK"

**Package Links:**
- PyPI: https://pypi.org/project/azure-ai-agents/1.1.0b3/
- GitHub: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents

---

## 🧪 Testing Strategy

### **Unit Tests:**

**File:** `src/backend/tests/test_fabric_integration.py`

```python
import pytest
from v3.magentic_agents.models.agent_models import FabricConfig
from types import SimpleNamespace

def test_fabric_config_creation():
    """Test FabricConfig creation from agent object."""
    agent_obj = SimpleNamespace(
        name="TestAgent",
        use_fabric=True,
        workspace_id="adbf7690-4c8b-4ba2-acbf-9cedcb6a2bfe",
        artifact_id="79a39492-2460-47d9-abb6-5573e562ccf6",
        fabric_connection_id="RetailCustomerSuccessAgent"
    )
    
    config = FabricConfig.from_agent_config(agent_obj)
    
    assert config is not None
    assert config.workspace_id == "adbf7690-4c8b-4ba2-acbf-9cedcb6a2bfe"
    assert config.artifact_id == "79a39492-2460-47d9-abb6-5573e562ccf6"
    assert config.fabric_connection_id == "RetailCustomerSuccessAgent"

def test_fabric_config_missing_fields():
    """Test FabricConfig raises error when fields missing."""
    agent_obj = SimpleNamespace(
        name="TestAgent",
        use_fabric=True,
        workspace_id="",  # Missing
        artifact_id="79a39492-2460-47d9-abb6-5573e562ccf6",
        fabric_connection_id="RetailCustomerSuccessAgent"
    )
    
    with pytest.raises(ValueError, match="missing required fields"):
        FabricConfig.from_agent_config(agent_obj)

def test_fabric_config_disabled():
    """Test FabricConfig returns None when use_fabric=False."""
    agent_obj = SimpleNamespace(
        name="TestAgent",
        use_fabric=False
    )
    
    config = FabricConfig.from_agent_config(agent_obj)
    assert config is None
```

### **Integration Tests:**

**Testschritte:**
1. Lade `retail.json` mit Fabric-Configuration
2. Erstelle `MagenticAgentFactory`
3. Rufe `create_agent_from_config()` für CustomerDataAgent
4. Verifiziere: `agent._fabric_config` ist not None
5. Verifiziere: FabricTool wurde zu `tools` hinzugefügt
6. Teste Abfrage: "How many orders did Emily Thompson place?"
7. Verifiziere Response enthält Daten aus RetailWarehouse

---

## 📝 Implementation Checklist

### Phase 1: Models & Configuration (1-2 hours)
- [ ] Update `AgentConfig` in `messages_kernel.py` (add 4 fields)
- [ ] Create `FabricConfig` in `agent_models.py`
- [ ] Update `team_service.py` (agent config parsing)
- [ ] Update `agents_service.py` (dict conversions)
- [ ] Write unit tests for `FabricConfig`

### Phase 2: Agent Factory Integration (2-3 hours)
- [ ] Update `magentic_agent_factory.py` (import FabricConfig)
- [ ] Add `fabric_config` parameter to factory methods
- [ ] Pass `fabric_config` to `FoundryAgentTemplate`
- [ ] Add validation for Fabric requirements

### Phase 3: FoundryAgentTemplate Integration (2-3 hours)
- [ ] Update `foundry_agent.py` `__init__` signature
- [ ] Add FabricTool initialization in `open()` method
- [ ] Handle `FabricConnection` creation
- [ ] Add error handling for missing SDK
- [ ] Add logging for Fabric setup

### Phase 4: Testing & Validation (1-2 hours)
- [ ] Install `azure-ai-agents` dependency
- [ ] Run unit tests
- [ ] Test with retail.json configuration
- [ ] Verify CustomerDataAgent can query Fabric Data Agent
- [ ] Test end-to-end: UI → Backend → Fabric Data Agent → RetailWarehouse
- [ ] Validate error handling (missing credentials, failed queries)

---

## 🚨 Known Issues & Considerations

### **1. Authentication:**
- Fabric Data Agent requires **On-Behalf-Of (OBO) token** from user
- **Microsoft Docs bestätigt:** "The Fabric data agent only supports user identity authentication. Service Principal Name (SPN) authentication is not supported."
- Backend muss User-Token von Frontend empfangen und an Azure AI Project Client übergeben
- `DefaultAzureCredential()` wird verwendet für Authentication
- **WICHTIG:** Connection muss in Azure AI Foundry Portal unter "Connected Resources" erstellt werden mit `workspace_id` und `artifact_id` als Custom Keys

### **2. SDK Version:**
- `azure-ai-agents>=1.1.0b3` erforderlich (Preview Version)
- **Microsoft Docs:** "You should use the latest beta/preview version of the Azure AI Agents Python SDK"
- API ist **stabil dokumentiert**: `FabricTool(connection_id=conn_id)` + `.definitions` property
- Connection ID Format: `/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.MachineLearningServices/workspaces/{project}/connections/{name}`

### **3. Error Handling:**
- Fabric Data Agent Queries können fehlschlagen (timeout, auth, query error)
- Backend muss gracefully degraden
- User-friendly error messages erforderlich

### **4. Performance:**
- Fabric Data Agent Queries können langsam sein (5-10 Sekunden)
- Überlege Caching für häufige Queries
- Timeout-Handling erforderlich

---

## 📚 Reference Documentation

- **Microsoft Learn:** [Consume Fabric Data Agent](https://learn.microsoft.com/en-us/fabric/data-science/consume-data-agent)
- **Azure AI Agents SDK:** [GitHub](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents)
- **FabricTool API:** Check latest SDK docs for exact API

---

## 🎯 Next Steps

1. **Immediate:** Implementiere Phase 1 (Models & Configuration)
2. **Then:** Teste mit `retail.json` ob Fabric-Felder korrekt geladen werden
3. **Then:** Implementiere Phase 2 & 3 (Agent Integration)
4. **Finally:** End-to-End Test mit Retail Customer Success Team

**Estimated Total Time:** 6-10 hours (je nach SDK-Dokumentation und Auth-Komplexität)

---

**Status:** 📝 Documented, ready for implementation
