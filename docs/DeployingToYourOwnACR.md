# Deployment mit eigener Azure Container Registry (ACR)

Diese Lösung erstellt automatisch eine eigene Azure Container Registry (ACR) während des Deployments. Dieses Dokument erklärt, wie Sie die Docker-Images in Ihre neu erstellte ACR hochladen und verwenden.

## 📋 Übersicht

Nach dem erfolgreichen Deployment der Infrastruktur mit `azd up` oder manuell wird automatisch eine Azure Container Registry erstellt mit:
- **Name-Format**: `cr<solutionname><uniquetext>` (z.B. `crmacaeabc12`)
- **SKU**: Basic (kann bei Bedarf auf Standard oder Premium erhöht werden)
- **Admin-Zugriff**: Aktiviert
- **Berechtigungen**: 
  - Ihre User Managed Identity hat `AcrPull` Rechte
  - Ihr Deployment-Benutzer hat `AcrPush` Rechte

## 🎯 Schnellstart - Komplettes Deployment

### Automatisiertes Deployment mit Skript (Empfohlen)

Das einfachste und schnellste Verfahren:

```powershell
# Schritt 1: Infrastruktur deployen
azd up

# Schritt 2: Docker-Images bauen und pushen (automatisch)
.\scripts\build-and-push-images.ps1

# Schritt 3: Services neu deployen mit den neuen Images
azd deploy
```

Das Skript erkennt automatisch Ihre ACR und baut alle drei Images. Fertig! 🎉

### Manuelle Schritt-für-Schritt-Anleitung

Falls Sie mehr Kontrolle möchten oder das Skript nicht verwenden können:

## 🚀 Docker-Images zur eigenen ACR pushen

### Automatisiert mit PowerShell-Skript (Empfohlen)

Wir haben ein praktisches Skript erstellt, das alles automatisiert:

```powershell
# Alle Images bauen und pushen (ACR wird automatisch erkannt)
.\scripts\build-and-push-images.ps1

# Nur bestimmte Components
.\scripts\build-and-push-images.ps1 -Components "backend,frontend"

# Mit spezifischem Tag
.\scripts\build-and-push-images.ps1 -ImageTag "v2.0"

# Manuell ACR angeben
.\scripts\build-and-push-images.ps1 -AcrName "crmacaeabc12" -ImageTag "v1.0"

# Hilfe anzeigen
Get-Help .\scripts\build-and-push-images.ps1 -Detailed
```

### Manuell (für mehr Kontrolle)

### Schritt 1: ACR-Informationen abrufen

Nach dem Deployment finden Sie die ACR-Details in den Outputs:

```bash
# Mit azd
azd env get-values | grep CONTAINER_REGISTRY

# Oder im Azure Portal
# Navigieren Sie zu Ihrer Resource Group → Container Registry
```

Die wichtigen Werte sind:
- `CONTAINER_REGISTRY_NAME`: Name der Registry (z.B. `crmacaeabc12`)
- `CONTAINER_REGISTRY_LOGIN_SERVER`: Login Server URL (z.B. `crmacaeabc12.azurecr.io`)

### Schritt 2: Bei ACR anmelden

```powershell
# Mit Azure CLI
az acr login --name <CONTAINER_REGISTRY_NAME>

# Beispiel
az acr login --name crmacaeabc12
```

### Schritt 3: Docker-Images bauen und pushen

#### Backend Image

```powershell
# Setzen Sie Ihre ACR-Variablen
$ACR_LOGIN_SERVER = "<your-acr-name>.azurecr.io"  # z.B. crmacaeabc12.azurecr.io

# Image bauen (vom Root-Verzeichnis des Repos)
docker build --no-cache -f src/backend/Dockerfile -t ${ACR_LOGIN_SERVER}/macaebackend:latest_v3 .

# Image pushen
docker push ${ACR_LOGIN_SERVER}/macaebackend:latest_v3
```

#### Frontend Image

```powershell
# Image bauen (vom Root-Verzeichnis des Repos)
docker build --no-cache -f src/frontend/Dockerfile -t ${ACR_LOGIN_SERVER}/macaefrontend:latest_v3 .

# Image pushen
docker push ${ACR_LOGIN_SERVER}/macaefrontend:latest_v3
```

#### MCP Server Image

```powershell
# Image bauen (vom Root-Verzeichnis des Repos)
docker build --no-cache -f src/mcp_server/Dockerfile -t ${ACR_LOGIN_SERVER}/macaemcp:latest_v3 .

# Image pushen
docker push ${ACR_LOGIN_SERVER}/macaemcp:latest_v3
```

### Schritt 4: Alle Images auf einmal bauen und pushen

```powershell
# Variablen setzen
$ACR_LOGIN_SERVER = "<your-acr-name>.azurecr.io"
$IMAGE_TAG = "latest_v3"

# Bei ACR anmelden
az acr login --name <your-acr-name>

# Stelle sicher, dass Sie im Root-Verzeichnis des Repos sind
cd C:\Users\Karim-MichaelAitOuka\git\AI_for_Breakfast\Multi-Agent-Custom-Automation-Engine-Solution-Accelerator

# Backend
docker build --no-cache -f src/backend/Dockerfile -t ${ACR_LOGIN_SERVER}/macaebackend:${IMAGE_TAG} .
docker push ${ACR_LOGIN_SERVER}/macaebackend:${IMAGE_TAG}

# Frontend
docker build --no-cache -f src/frontend/Dockerfile -t ${ACR_LOGIN_SERVER}/macaefrontend:${IMAGE_TAG} .
docker push ${ACR_LOGIN_SERVER}/macaefrontend:${IMAGE_TAG}

# MCP
docker build --no-cache -f src/mcp_server/Dockerfile -t ${ACR_LOGIN_SERVER}/macaemcp:${IMAGE_TAG} .
docker push ${ACR_LOGIN_SERVER}/macaemcp:${IMAGE_TAG}
```

## 🔄 Images mit neuen Tags deployen

Wenn Sie eine neue Version Ihrer Images erstellen möchten:

1. **Bauen und pushen Sie mit einem neuen Tag:**

```powershell
$NEW_TAG = "v2.0"
docker build --no-cache -f src/backend/Dockerfile -t ${ACR_LOGIN_SERVER}/macaebackend:${NEW_TAG} .
docker push ${ACR_LOGIN_SERVER}/macaebackend:${NEW_TAG}
```

2. **Aktualisieren Sie die Parameter und deployen Sie erneut:**

```powershell
# In .env oder azure.yaml
$env:AZURE_ENV_IMAGE_TAG = "v2.0"

# Re-deploy nur die betroffenen Ressourcen
azd deploy
```

Alternativ können Sie die Container App und App Service im Azure Portal manuell aktualisieren:

### Backend Container App manuell aktualisieren

1. Gehen Sie zu Ihrer **Container App** im [Azure Portal](https://portal.azure.com)
2. Wählen Sie im linken Menü **Containers**
3. Unter Ihrem Container, aktualisieren Sie:
   - **Image source** → Azure Container Registry
   - **Registry** → Ihre ACR
   - **Image name** → `macaebackend`
   - **Tag** → neuer Tag (z.B. `v2.0`)
4. Klicken Sie auf **Save** → dies erstellt automatisch eine neue Revision

### Frontend App Service manuell aktualisieren

1. Gehen Sie zu Ihrem **App Service** im [Azure Portal](https://portal.azure.com)
2. Wählen Sie im linken Menü **Deployment Center**
3. Unter Container settings konfigurieren Sie:
   - **Image Source** → Azure Container Registry
   - **Registry** → Ihre ACR
   - **Image Name** → `macaefrontend`
   - **Tag** → neuer Tag (z.B. `v2.0`)
4. Klicken Sie auf **Save**

## ✅ Verifizierung

Prüfen Sie, ob die Images erfolgreich gepusht wurden:

```powershell
az acr repository list --name <your-acr-name> --output table
```

Sie sollten die folgenden Repositories sehen:
- `macaebackend`
- `macaefrontend`
- `macaemcp`

Um alle Tags für ein bestimmtes Image zu sehen:

```powershell
az acr repository show-tags --name <your-acr-name> --repository macaebackend --output table
```

## 🔐 Berechtigungen und Sicherheit

Die Bicep-Vorlage konfiguriert automatisch:

1. **User Managed Identity** mit `AcrPull` Berechtigung
   - Ermöglicht Container Apps und App Services, Images zu pullen
   
2. **Ihr Benutzer-Account** mit `AcrPush` Berechtigung
   - Ermöglicht Ihnen, Images zu pushen

3. **Admin-Zugriff** ist aktiviert
   - Kann bei Bedarf deaktiviert werden für erhöhte Sicherheit

### Private Networking (WAF-Modus)

Wenn `enablePrivateNetworking` auf `true` gesetzt ist:
- ACR hat `publicNetworkAccess: 'Disabled'`
- Zugriff nur über Private Endpoints möglich
- Sie benötigen VPN oder Bastion-Zugriff zum Pushen von Images

## 📝 Best Practices

1. **Verwenden Sie aussagekräftige Tags**
   - Statt nur `latest`, nutzen Sie Versionsnummern wie `v1.0.0`, `v2.0.0`
   - Oder verwenden Sie Git Commit SHAs: `abc1234`

2. **Automatisieren Sie mit CI/CD**
   - Richten Sie GitHub Actions oder Azure DevOps Pipelines ein
   - Automatisches Bauen und Pushen bei Code-Änderungen

3. **Multi-Stage Builds**
   - Verwenden Sie Docker Multi-Stage Builds um Image-Größe zu reduzieren
   - Siehe vorhandene Dockerfiles als Beispiel

4. **Image-Scanning**
   - Aktivieren Sie Defender for Containers für Vulnerability Scanning
   - Überprüfen Sie regelmäßig auf Sicherheitslücken

## 🛠️ Troubleshooting

### Fehler: "unauthorized: authentication required"

```powershell
# Melden Sie sich erneut an
az acr login --name <your-acr-name>
```

### Fehler: "denied: requested access to the resource is denied"

- Überprüfen Sie, ob Sie die `AcrPush` Rolle haben
- Im Azure Portal: Container Registry → Access Control (IAM)

### Image-Pull-Fehler in Container App

- Überprüfen Sie, ob die User Managed Identity `AcrPull` Rechte hat
- Überprüfen Sie, ob das Image und der Tag korrekt sind

### Langsamer Image-Push

- Prüfen Sie Ihre Internetverbindung
- Erwägen Sie, auf Standard oder Premium SKU zu upgraden
- Aktivieren Sie Geo-Replication für Premium SKU

## 📚 Weitere Ressourcen

- [Azure Container Registry Dokumentation](https://learn.microsoft.com/azure/container-registry/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Container App Image Updates](https://learn.microsoft.com/azure/container-apps/revisions)
- [App Service Container Configuration](https://learn.microsoft.com/azure/app-service/configure-custom-container)
