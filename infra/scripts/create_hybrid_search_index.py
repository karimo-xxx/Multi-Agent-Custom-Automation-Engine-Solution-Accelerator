"""
Azure AI Search Hybrid Index Creation Script
============================================
This script creates a hybrid search index with:
- Vector fields for semantic search (text-embedding-3-large, 3072 dimensions)
- Text fields for keyword search
- Semantic configuration for re-ranking
- HNSW algorithm for efficient vector search

Usage:
    python create_hybrid_search_index.py <ai_search_endpoint> [<ai_search_index_name>]

Example:
    python create_hybrid_search_index.py https://mysearch.search.windows.net macae-hybrid-index
"""

from azure.identity import AzureCliCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch
)
import sys

def create_hybrid_search_index(ai_search_endpoint: str, index_name: str = "macae-hybrid-index"):
    """
    Creates a hybrid search index with vector and text fields.
    
    Args:
        ai_search_endpoint: Azure AI Search endpoint URL
        index_name: Name of the index to create (default: macae-hybrid-index)
    """
    
    # Ensure endpoint is properly formatted
    if not ai_search_endpoint.__contains__("search.windows.net"):
        ai_search_endpoint = f"https://{ai_search_endpoint}.search.windows.net"
    
    print(f"\n🔧 Creating Hybrid Search Index: {index_name}")
    print(f"📍 Endpoint: {ai_search_endpoint}\n")
    
    # Initialize credential and client
    credential = AzureCliCredential()
    search_index_client = SearchIndexClient(endpoint=ai_search_endpoint, credential=credential)
    
    # Define index fields
    fields = [
        # Key field
        SimpleField(
            name="id",
            type=SearchFieldDataType.String,
            key=True,
            filterable=True,
            sortable=True
        ),
        
        # Document type (customer_profile, order_fulfillment, incident_report, etc.)
        SimpleField(
            name="type",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True
        ),
        
        # Title field (searchable, used for semantic ranking)
        SearchableField(
            name="title",
            type=SearchFieldDataType.String,
            searchable=True,
            filterable=True,
            sortable=True
        ),
        
        # Content field (main text for keyword search and semantic ranking)
        SearchableField(
            name="content",
            type=SearchFieldDataType.String,
            searchable=True,
            analyzer_name="de.microsoft"  # German language analyzer for ALTYCA GmbH
        ),
        
        # Vector field for semantic similarity search (text-embedding-3-large: 3072 dimensions)
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=3072,
            vector_search_profile_name="hnsw-profile"
        ),
        
        # Metadata fields for filtering and faceting
        SimpleField(
            name="company",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True
        ),
        
        SimpleField(
            name="created_date",
            type=SearchFieldDataType.DateTimeOffset,
            filterable=True,
            sortable=True
        ),
        
        # Customer/Order references for cross-document relationships
        SearchableField(
            name="customer_id",
            type=SearchFieldDataType.String,
            filterable=True,
            searchable=True
        ),
        
        SearchableField(
            name="order_id",
            type=SearchFieldDataType.String,
            filterable=True,
            searchable=True
        ),
        
        # Tags for categorization
        SearchableField(
            name="tags",
            type=SearchFieldDataType.Collection(SearchFieldDataType.String),
            filterable=True,
            facetable=True,
            searchable=True
        )
    ]
    
    # Configure vector search with HNSW algorithm
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-algorithm",
                parameters={
                    "m": 4,  # Number of bi-directional links (higher = better recall, more storage)
                    "efConstruction": 400,  # Size of dynamic candidate list (higher = better index quality)
                    "efSearch": 500,  # Size of dynamic candidate list for search (higher = better recall)
                    "metric": "cosine"  # Cosine similarity for text embeddings
                }
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="hnsw-profile",
                algorithm_configuration_name="hnsw-algorithm"
            )
        ]
    )
    
    # Configure semantic search (Bing models for re-ranking)
    semantic_config = SemanticConfiguration(
        name="altyca-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="title"),
            content_fields=[
                SemanticField(field_name="content")
            ],
            keywords_fields=[
                SemanticField(field_name="tags")
            ]
        )
    )
    
    semantic_search = SemanticSearch(
        configurations=[semantic_config]
    )
    
    # Create the index
    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search
    )
    
    try:
        print("📝 Creating index with configuration:")
        print(f"   - Fields: {len(fields)}")
        print(f"   - Vector dimensions: 3072 (text-embedding-3-large)")
        print(f"   - Algorithm: HNSW (cosine similarity)")
        print(f"   - Semantic config: altyca-semantic-config")
        print(f"   - Language analyzer: German (de.microsoft)\n")
        
        result = search_index_client.create_or_update_index(index=index)
        
        print(f"✅ Index '{index_name}' created successfully!")
        print(f"🔍 Index is ready for:")
        print(f"   ✓ Keyword search (BM25 ranking)")
        print(f"   ✓ Vector search (semantic similarity)")
        print(f"   ✓ Hybrid search (keyword + vector)")
        print(f"   ✓ Semantic ranking (Bing re-ranking models)")
        print(f"\n🎯 Next step: Run ingest_data_with_embeddings.py to populate the index\n")
        
        return result
        
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        sys.exit(1)


def main():
    """Main entry point for the script."""
    
    if len(sys.argv) < 2:
        print("Usage: python create_hybrid_search_index.py <ai_search_endpoint> [<ai_search_index_name>]")
        print("\nExample:")
        print("  python create_hybrid_search_index.py https://mysearch.search.windows.net")
        print("  python create_hybrid_search_index.py mysearch.search.windows.net macae-hybrid-index")
        sys.exit(1)
    
    ai_search_endpoint = sys.argv[1]
    ai_search_index_name = sys.argv[2] if len(sys.argv) > 2 else "macae-hybrid-index"
    
    create_hybrid_search_index(ai_search_endpoint, ai_search_index_name)


if __name__ == "__main__":
    main()
