"""
Azure AI Search Hybrid Search Testing Script
============================================
This script tests different search methods (keyword, vector, hybrid, semantic) against the hybrid search index.
It validates search relevance and compares results across different approaches.

Usage:
    python test_hybrid_search.py <ai_search_endpoint> <openai_endpoint> <embedding_deployment> [<index_name>]

Example:
    python test_hybrid_search.py https://mysearch.search.windows.net https://myopenai.openai.azure.com text-embedding-3-large macae-hybrid-index
"""

from azure.identity import AzureCliCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI
import sys
from typing import List, Dict, Any


class SearchTester:
    """Test suite for Azure AI Search hybrid search capabilities."""
    
    def __init__(
        self,
        search_endpoint: str,
        openai_endpoint: str,
        embedding_deployment: str,
        index_name: str = "macae-hybrid-index"
    ):
        # Ensure endpoints are properly formatted
        if not search_endpoint.__contains__("search.windows.net"):
            search_endpoint = f"https://{search_endpoint}.search.windows.net"
        
        if not openai_endpoint.__contains__("openai.azure.com"):
            openai_endpoint = f"https://{openai_endpoint}.openai.azure.com"
        
        self.search_endpoint = search_endpoint
        self.openai_endpoint = openai_endpoint
        self.embedding_deployment = embedding_deployment
        self.index_name = index_name
        
        # Initialize clients
        credential = AzureCliCredential()
        
        print(f"\n🧪 Hybrid Search Test Suite")
        print(f"=" * 70)
        print(f"📍 Search Endpoint: {search_endpoint}")
        print(f"🤖 OpenAI Endpoint: {openai_endpoint}")
        print(f"📊 Embedding Model: {embedding_deployment}")
        print(f"📇 Index Name: {index_name}\n")
        
        try:
            self.search_client = SearchClient(
                endpoint=search_endpoint,
                index_name=index_name,
                credential=credential
            )
            print("✅ Search client initialized")
        except Exception as e:
            print(f"❌ Error initializing Search client: {e}")
            sys.exit(1)
        
        try:
            self.openai_client = AzureOpenAI(
                azure_endpoint=openai_endpoint,
                api_version="2024-12-01-preview",
                azure_ad_token_provider=lambda: credential.get_token(
                    "https://cognitiveservices.azure.com/.default"
                ).token
            )
            print("✅ OpenAI client initialized\n")
        except Exception as e:
            print(f"❌ Error initializing OpenAI client: {e}")
            sys.exit(1)
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text."""
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.embedding_deployment
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
            raise
    
    def format_result(self, result: Dict[str, Any], rank: int) -> str:
        """Format search result for display."""
        title = result.get('title', 'Untitled')
        doc_type = result.get('type', 'document')
        content = result.get('content', '')[:200]  # First 200 chars
        score = result.get('@search.score', 0)
        
        formatted = f"\n   [{rank}] Score: {score:.4f}"
        formatted += f"\n       Type: {doc_type}"
        formatted += f"\n       Title: {title}"
        formatted += f"\n       Preview: {content}..."
        
        customer_id = result.get('customer_id')
        order_id = result.get('order_id')
        if customer_id:
            formatted += f"\n       Customer: {customer_id}"
        if order_id:
            formatted += f"\n       Order: {order_id}"
        
        return formatted
    
    def test_keyword_search(self, query: str, top: int = 5):
        """Test 1: Pure keyword search (BM25)."""
        print(f"\n{'='*70}")
        print(f"🔍 TEST 1: Keyword Search (BM25)")
        print(f"{'='*70}")
        print(f"Query: '{query}'\n")
        
        try:
            results = self.search_client.search(
                search_text=query,
                query_type="simple",
                select=["id", "title", "content", "type", "customer_id", "order_id"],
                top=top
            )
            
            result_list = list(results)
            
            if result_list:
                print(f"📊 Found {len(result_list)} results:")
                for idx, result in enumerate(result_list, start=1):
                    print(self.format_result(result, idx))
            else:
                print("❌ No results found")
            
            return result_list
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def test_vector_search(self, query: str, top: int = 5):
        """Test 2: Pure vector search (semantic similarity)."""
        print(f"\n{'='*70}")
        print(f"🔍 TEST 2: Vector Search (Semantic Similarity)")
        print(f"{'='*70}")
        print(f"Query: '{query}'\n")
        
        try:
            print("🧠 Generating query embedding...")
            query_vector = self.generate_embedding(query)
            print(f"✅ Embedding generated ({len(query_vector)} dimensions)\n")
            
            vector_query = VectorizedQuery(
                vector=query_vector,
                k_nearest_neighbors=top,
                fields="content_vector"
            )
            
            results = self.search_client.search(
                search_text=None,  # No keyword component
                vector_queries=[vector_query],
                select=["id", "title", "content", "type", "customer_id", "order_id"],
                top=top
            )
            
            result_list = list(results)
            
            if result_list:
                print(f"📊 Found {len(result_list)} results:")
                for idx, result in enumerate(result_list, start=1):
                    print(self.format_result(result, idx))
            else:
                print("❌ No results found")
            
            return result_list
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def test_hybrid_search(self, query: str, top: int = 5):
        """Test 3: Hybrid search (keyword + vector)."""
        print(f"\n{'='*70}")
        print(f"🔍 TEST 3: Hybrid Search (Keyword + Vector)")
        print(f"{'='*70}")
        print(f"Query: '{query}'\n")
        
        try:
            print("🧠 Generating query embedding...")
            query_vector = self.generate_embedding(query)
            print(f"✅ Embedding generated ({len(query_vector)} dimensions)\n")
            
            vector_query = VectorizedQuery(
                vector=query_vector,
                k_nearest_neighbors=top,
                fields="content_vector"
            )
            
            results = self.search_client.search(
                search_text=query,  # Keyword component
                vector_queries=[vector_query],  # Vector component
                select=["id", "title", "content", "type", "customer_id", "order_id"],
                top=top
            )
            
            result_list = list(results)
            
            if result_list:
                print(f"📊 Found {len(result_list)} results:")
                for idx, result in enumerate(result_list, start=1):
                    print(self.format_result(result, idx))
            else:
                print("❌ No results found")
            
            return result_list
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def test_semantic_ranking(self, query: str, top: int = 5):
        """Test 4: Hybrid search with semantic re-ranking (Bing models)."""
        print(f"\n{'='*70}")
        print(f"🔍 TEST 4: Hybrid Search + Semantic Ranking (Bing Re-ranking)")
        print(f"{'='*70}")
        print(f"Query: '{query}'\n")
        
        try:
            print("🧠 Generating query embedding...")
            query_vector = self.generate_embedding(query)
            print(f"✅ Embedding generated ({len(query_vector)} dimensions)\n")
            
            vector_query = VectorizedQuery(
                vector=query_vector,
                k_nearest_neighbors=top * 2,  # Get more candidates for re-ranking
                fields="content_vector"
            )
            
            results = self.search_client.search(
                search_text=query,
                vector_queries=[vector_query],
                query_type="semantic",  # Enable semantic ranking
                semantic_configuration_name="altyca-semantic-config",
                select=["id", "title", "content", "type", "customer_id", "order_id"],
                top=top
            )
            
            result_list = list(results)
            
            if result_list:
                print(f"📊 Found {len(result_list)} results (re-ranked by Bing):")
                for idx, result in enumerate(result_list, start=1):
                    print(self.format_result(result, idx))
                    # Show reranker score if available
                    reranker_score = result.get('@search.rerankerScore')
                    if reranker_score:
                        print(f"       Reranker Score: {reranker_score:.4f}")
            else:
                print("❌ No results found")
            
            return result_list
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def run_all_tests(self):
        """Run comprehensive test suite."""
        test_queries = [
            "Sarah Weber customer satisfaction",
            "Produkte für Homeoffice Setup",
            "Lieferverzögerung durch Wetter",
            "ProStream Gaming Headset",
            "Loyalty Program Platinum Status"
        ]
        
        print(f"\n{'#'*70}")
        print(f"# COMPREHENSIVE TEST SUITE - {len(test_queries)} Queries")
        print(f"{'#'*70}")
        
        for idx, query in enumerate(test_queries, start=1):
            print(f"\n\n{'█'*70}")
            print(f"█ QUERY {idx}/{len(test_queries)}: {query}")
            print(f"{'█'*70}")
            
            # Test all 4 methods
            self.test_keyword_search(query, top=3)
            self.test_vector_search(query, top=3)
            self.test_hybrid_search(query, top=3)
            self.test_semantic_ranking(query, top=3)
        
        # Final summary
        print(f"\n\n{'='*70}")
        print(f"✅ TEST SUITE COMPLETE")
        print(f"{'='*70}")
        print(f"\n📊 RESULTS INTERPRETATION:")
        print(f"   - Keyword Search: Good for exact term matches (names, IDs, specific words)")
        print(f"   - Vector Search: Good for semantic meaning, context understanding")
        print(f"   - Hybrid Search: Best of both worlds (Microsoft recommended)")
        print(f"   - Semantic Ranking: Bing re-ranking for most relevant results")
        print(f"\n💡 RECOMMENDATION:")
        print(f"   Use Hybrid Search + Semantic Ranking for production (best relevance)")
        print(f"   Expected relevance improvement: 15-30% vs. keyword-only\n")


def main():
    """Main entry point."""
    if len(sys.argv) < 4:
        print("Usage: python test_hybrid_search.py <ai_search_endpoint> <openai_endpoint> <embedding_deployment> [<index_name>]")
        print("\nExample:")
        print("  python test_hybrid_search.py https://mysearch.search.windows.net https://myopenai.openai.azure.com text-embedding-3-large")
        print("  python test_hybrid_search.py mysearch myopenai text-embedding-3-large macae-hybrid-index")
        sys.exit(1)
    
    ai_search_endpoint = sys.argv[1]
    openai_endpoint = sys.argv[2]
    embedding_deployment = sys.argv[3]
    index_name = sys.argv[4] if len(sys.argv) > 4 else "macae-hybrid-index"
    
    tester = SearchTester(
        ai_search_endpoint,
        openai_endpoint,
        embedding_deployment,
        index_name
    )
    
    tester.run_all_tests()


if __name__ == "__main__":
    main()
