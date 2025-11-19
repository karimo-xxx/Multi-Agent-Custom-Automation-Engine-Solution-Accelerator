"""
Azure AI Search Data Ingestion with Embeddings
==============================================
This script ingests JSON documents into a hybrid search index with:
- Text content for keyword search
- Vector embeddings (text-embedding-3-large) for semantic search
- Metadata extraction from JSON structure

Usage:
    python ingest_data_with_embeddings.py <ai_search_endpoint> <openai_endpoint> <embedding_deployment> [<index_name>] [<data_directory>]

Example:
    python ingest_data_with_embeddings.py https://mysearch.search.windows.net https://myopenai.openai.azure.com text-embedding-3-large macae-hybrid-index ../data/datasets
"""

from azure.identity import AzureCliCredential
from azure.search.documents import SearchClient
from openai import AzureOpenAI
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

def generate_embedding(client: AzureOpenAI, text: str, deployment_name: str) -> List[float]:
    """
    Generate embedding vector for text using Azure OpenAI.
    
    Args:
        client: AzureOpenAI client
        text: Text to embed
        deployment_name: Name of the embedding deployment
        
    Returns:
        List of floats representing the embedding vector
    """
    try:
        # Truncate text if too long (max 8191 tokens for text-embedding-3-large)
        # Rough estimate: 1 token ≈ 4 characters
        max_chars = 8191 * 4
        if len(text) > max_chars:
            text = text[:max_chars]
            print(f"   ⚠️  Text truncated to {max_chars} characters")
        
        response = client.embeddings.create(
            input=text,
            model=deployment_name
        )
        return response.data[0].embedding
    
    except Exception as e:
        print(f"   ❌ Error generating embedding: {e}")
        raise


def load_json_documents(data_directory: str) -> List[Dict[str, Any]]:
    """
    Load all JSON documents from the data directory.
    
    Args:
        data_directory: Path to directory containing JSON files
        
    Returns:
        List of parsed JSON documents
    """
    documents = []
    data_path = Path(data_directory)
    
    if not data_path.exists():
        print(f"❌ Directory not found: {data_directory}")
        sys.exit(1)
    
    json_files = list(data_path.glob("altyca_doc_*.json"))
    
    if not json_files:
        print(f"❌ No JSON files found matching pattern 'altyca_doc_*.json' in {data_directory}")
        sys.exit(1)
    
    print(f"\n📂 Loading {len(json_files)} JSON documents from {data_directory}...")
    
    for json_file in sorted(json_files):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                doc = json.load(f)
                documents.append({
                    'filename': json_file.name,
                    'data': doc
                })
        except Exception as e:
            print(f"   ⚠️  Error loading {json_file.name}: {e}")
            continue
    
    print(f"✅ Loaded {len(documents)} documents\n")
    return documents


def prepare_document_for_indexing(
    doc_data: Dict[str, Any],
    embedding_vector: List[float]
) -> Dict[str, Any]:
    """
    Prepare document for Azure AI Search indexing.
    
    Args:
        doc_data: Original JSON document data
        embedding_vector: Pre-computed embedding vector
        
    Returns:
        Document formatted for Azure AI Search
    """
    metadata = doc_data.get('metadata', {})
    
    # Extract customer_id and order_id from cross_references or metadata
    cross_refs = doc_data.get('cross_references', {})
    customer_id = None
    order_id = None
    
    # Try to find customer_id
    if 'customer_id' in cross_refs:
        customer_id = cross_refs['customer_id']
    elif 'customer_profile_id' in metadata:
        customer_id = metadata['customer_profile_id']
    
    # Try to find order_id
    if 'orders' in cross_refs and cross_refs['orders']:
        order_id = cross_refs['orders'][0] if isinstance(cross_refs['orders'], list) else cross_refs['orders']
    elif 'order_id' in metadata:
        order_id = metadata['order_id']
    
    # Parse created_date
    created_date_str = metadata.get('created_date', metadata.get('date', metadata.get('incident_date')))
    created_date = None
    if created_date_str:
        try:
            # Try ISO format first
            created_date = datetime.fromisoformat(created_date_str.replace('Z', '+00:00')).isoformat()
        except:
            try:
                # Try parsing DD.MM.YYYY format (German)
                dt = datetime.strptime(created_date_str, '%d.%m.%Y')
                created_date = dt.isoformat()
            except:
                # Default to current date
                created_date = datetime.utcnow().isoformat()
    else:
        created_date = datetime.utcnow().isoformat()
    
    # Extract tags
    tags = metadata.get('tags', [])
    if isinstance(tags, str):
        tags = [tags]
    
    # Build the indexed document
    indexed_doc = {
        'id': doc_data['id'],
        'type': doc_data['type'],
        'title': doc_data['title'],
        'content': doc_data['content'],
        'content_vector': embedding_vector,
        'company': metadata.get('company', 'ALTYCA GmbH'),
        'created_date': created_date,
        'customer_id': customer_id,
        'order_id': order_id,
        'tags': tags
    }
    
    return indexed_doc


def ingest_documents_with_embeddings(
    ai_search_endpoint: str,
    openai_endpoint: str,
    embedding_deployment: str,
    index_name: str = "macae-hybrid-index",
    data_directory: str = "../data/datasets"
):
    """
    Ingest JSON documents into Azure AI Search with embeddings.
    
    Args:
        ai_search_endpoint: Azure AI Search endpoint URL
        openai_endpoint: Azure OpenAI endpoint URL
        embedding_deployment: Name of the embedding deployment (text-embedding-3-large)
        index_name: Name of the search index
        data_directory: Path to directory containing JSON documents
    """
    
    # Ensure endpoints are properly formatted
    if not ai_search_endpoint.__contains__("search.windows.net"):
        ai_search_endpoint = f"https://{ai_search_endpoint}.search.windows.net"
    
    if not openai_endpoint.__contains__("openai.azure.com"):
        openai_endpoint = f"https://{openai_endpoint}.openai.azure.com"
    
    print(f"\n🚀 Azure AI Search Data Ingestion with Embeddings")
    print(f"=" * 60)
    print(f"📍 Search Endpoint: {ai_search_endpoint}")
    print(f"🤖 OpenAI Endpoint: {openai_endpoint}")
    print(f"📊 Embedding Model: {embedding_deployment}")
    print(f"📇 Index Name: {index_name}")
    print(f"📁 Data Directory: {data_directory}\n")
    
    # Initialize clients
    credential = AzureCliCredential()
    
    try:
        openai_client = AzureOpenAI(
            azure_endpoint=openai_endpoint,
            api_version="2024-12-01-preview",
            azure_ad_token_provider=lambda: credential.get_token("https://cognitiveservices.azure.com/.default").token
        )
        print("✅ OpenAI client initialized")
    except Exception as e:
        print(f"❌ Error initializing OpenAI client: {e}")
        sys.exit(1)
    
    try:
        search_client = SearchClient(
            endpoint=ai_search_endpoint,
            index_name=index_name,
            credential=credential
        )
        print("✅ Search client initialized\n")
    except Exception as e:
        print(f"❌ Error initializing Search client: {e}")
        sys.exit(1)
    
    # Load documents
    documents = load_json_documents(data_directory)
    
    # Process and index documents
    indexed_documents = []
    success_count = 0
    fail_count = 0
    
    print(f"🔄 Processing {len(documents)} documents...\n")
    
    for idx, doc in enumerate(documents, start=1):
        filename = doc['filename']
        doc_data = doc['data']
        doc_id = doc_data.get('id', f'doc_{idx}')
        doc_title = doc_data.get('title', 'Untitled')
        
        print(f"[{idx}/{len(documents)}] Processing: {filename}")
        print(f"   📄 ID: {doc_id}")
        print(f"   📝 Title: {doc_title}")
        
        try:
            # Generate embedding for content
            content = doc_data.get('content', '')
            print(f"   🧠 Generating embedding ({len(content)} chars)...")
            
            embedding_vector = generate_embedding(
                openai_client,
                content,
                embedding_deployment
            )
            
            print(f"   ✅ Embedding generated ({len(embedding_vector)} dimensions)")
            
            # Prepare document for indexing
            indexed_doc = prepare_document_for_indexing(doc_data, embedding_vector)
            indexed_documents.append(indexed_doc)
            
            print(f"   ✅ Document prepared for indexing\n")
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ Error processing document: {e}\n")
            fail_count += 1
            continue
    
    # Upload documents to index
    if indexed_documents:
        print(f"\n📤 Uploading {len(indexed_documents)} documents to index '{index_name}'...")
        
        try:
            # Upload in batches of 10 to avoid timeout
            batch_size = 10
            for i in range(0, len(indexed_documents), batch_size):
                batch = indexed_documents[i:i + batch_size]
                result = search_client.upload_documents(documents=batch)
                print(f"   ✅ Uploaded batch {i // batch_size + 1}/{(len(indexed_documents) + batch_size - 1) // batch_size} ({len(batch)} documents)")
            
            print(f"\n✅ Successfully uploaded {len(indexed_documents)} documents!")
            
        except Exception as e:
            print(f"\n❌ Error uploading documents: {e}")
            sys.exit(1)
    else:
        print("\n❌ No documents to upload")
        sys.exit(1)
    
    # Summary
    print(f"\n" + "=" * 60)
    print(f"📊 INGESTION SUMMARY")
    print(f"=" * 60)
    print(f"✅ Success: {success_count} documents")
    print(f"❌ Failed: {fail_count} documents")
    print(f"📇 Index: {index_name}")
    print(f"\n🎯 Index is ready for:")
    print(f"   ✓ Keyword search (BM25)")
    print(f"   ✓ Vector search (semantic similarity)")
    print(f"   ✓ Hybrid search (keyword + vector)")
    print(f"   ✓ Semantic ranking (Bing re-ranking)")
    print(f"\n🔍 Test your index with: python test_hybrid_search.py\n")


def main():
    """Main entry point for the script."""
    
    if len(sys.argv) < 4:
        print("Usage: python ingest_data_with_embeddings.py <ai_search_endpoint> <openai_endpoint> <embedding_deployment> [<index_name>] [<data_directory>]")
        print("\nExample:")
        print("  python ingest_data_with_embeddings.py https://mysearch.search.windows.net https://myopenai.openai.azure.com text-embedding-3-large")
        print("  python ingest_data_with_embeddings.py mysearch myopenai text-embedding-3-large macae-hybrid-index ../data/datasets")
        sys.exit(1)
    
    ai_search_endpoint = sys.argv[1]
    openai_endpoint = sys.argv[2]
    embedding_deployment = sys.argv[3]
    index_name = sys.argv[4] if len(sys.argv) > 4 else "macae-hybrid-index"
    data_directory = sys.argv[5] if len(sys.argv) > 5 else "../data/datasets"
    
    ingest_documents_with_embeddings(
        ai_search_endpoint,
        openai_endpoint,
        embedding_deployment,
        index_name,
        data_directory
    )


if __name__ == "__main__":
    main()
