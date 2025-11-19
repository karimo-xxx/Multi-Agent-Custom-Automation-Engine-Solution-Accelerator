"""
Delete Old Azure AI Search Index
=================================
This script safely deletes the old 'sample-dataset-index' from Azure AI Search.
Use this before creating the new hybrid search index.

Usage:
    python delete_old_index.py <ai_search_endpoint> [<index_name>]

Example:
    python delete_old_index.py https://mysearch.search.windows.net
    python delete_old_index.py mysearch sample-dataset-index
"""

from azure.identity import AzureCliCredential, DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
import sys
import os


def delete_index(ai_search_endpoint: str, index_name: str = "sample-dataset-index"):
    """
    Delete an Azure AI Search index.
    
    Args:
        ai_search_endpoint: Azure AI Search endpoint URL
        index_name: Name of the index to delete
    """
    
    # Ensure endpoint is properly formatted
    if not ai_search_endpoint.__contains__("search.windows.net"):
        ai_search_endpoint = f"https://{ai_search_endpoint}.search.windows.net"
    
    print(f"\n🗑️  Deleting Azure AI Search Index")
    print(f"=" * 60)
    print(f"📍 Endpoint: {ai_search_endpoint}")
    print(f"📇 Index: {index_name}\n")
    
    # Initialize credential - try API key first, then DefaultAzureCredential
    api_key = os.getenv("AZURE_AI_SEARCH_API_KEY")
    
    if api_key and api_key != "<Deployed-Search-ApiKey>":
        print("🔑 Using API Key authentication")
        credential = AzureKeyCredential(api_key)
    else:
        print("🔑 Using DefaultAzureCredential")
        credential = DefaultAzureCredential()
    
    search_index_client = SearchIndexClient(endpoint=ai_search_endpoint, credential=credential)
    
    try:
        # Check if index exists
        print(f"🔍 Checking if index '{index_name}' exists...")
        
        try:
            existing_index = search_index_client.get_index(index_name)
            print(f"✅ Index found: {existing_index.name}")
            
            # Get index statistics
            stats = search_index_client.get_index_statistics(index_name)
            
            # Handle both dict and object response
            if isinstance(stats, dict):
                doc_count = stats.get('document_count', 0)
                storage_size = stats.get('storage_size', 0) / (1024 * 1024)  # Convert to MB
            else:
                doc_count = stats.document_count if hasattr(stats, 'document_count') else 0
                storage_size = (stats.storage_size if hasattr(stats, 'storage_size') else 0) / (1024 * 1024)
            
            print(f"\n📊 Index Statistics:")
            print(f"   - Documents: {doc_count}")
            print(f"   - Storage: {storage_size:.2f} MB")
            
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                print(f"✅ Index '{index_name}' does not exist (already deleted or never created)")
                print(f"\n✨ Nothing to delete!")
                return
            else:
                raise
        
        # Confirm deletion
        print(f"\n⚠️  WARNING: This will permanently delete the index and all its data!")
        print(f"⚠️  Index: {index_name}")
        print(f"⚠️  Documents: {doc_count}")
        
        response = input(f"\n❓ Type 'DELETE' to confirm deletion: ")
        
        if response.strip().upper() != "DELETE":
            print(f"\n❌ Deletion cancelled by user")
            print(f"   Index '{index_name}' was NOT deleted")
            return
        
        # Delete the index
        print(f"\n🗑️  Deleting index '{index_name}'...")
        search_index_client.delete_index(index_name)
        
        print(f"\n✅ Index '{index_name}' deleted successfully!")
        print(f"💾 Freed {storage_size:.2f} MB of storage")
        print(f"\n🎯 Next step: Create new hybrid search index")
        print(f"   python infra/scripts/create_hybrid_search_index.py {ai_search_endpoint.split('.')[0].replace('https://', '')}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def main():
    """Main entry point for the script."""
    
    if len(sys.argv) < 2:
        print("Usage: python delete_old_index.py <ai_search_endpoint> [<index_name>]")
        print("\nExample:")
        print("  python delete_old_index.py https://mysearch.search.windows.net")
        print("  python delete_old_index.py mysearch sample-dataset-index")
        print("\nThis will delete the old index to make room for the new hybrid search index.")
        sys.exit(1)
    
    ai_search_endpoint = sys.argv[1]
    index_name = sys.argv[2] if len(sys.argv) > 2 else "sample-dataset-index"
    
    delete_index(ai_search_endpoint, index_name)


if __name__ == "__main__":
    main()
