"""
RAG search capabilities for ReasoningAgentTemplate using AzureAISearchCollection.
Based on Semantic Kernel text search patterns with Hybrid Search and Semantic Ranking.
"""

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from v3.magentic_agents.models.agent_models import SearchConfig
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
import os


class ReasoningSearch:
    """Handles Azure AI Search integration for reasoning agents with hybrid search and semantic ranking."""

    def __init__(self, search_config: SearchConfig | None = None):
        self.search_config = search_config
        self.search_client: SearchClient | None = None
        self.openai_client: AzureOpenAI | None = None
        self.embedding_deployment: str | None = None
        self.embedding_dimensions: int = 3072  # text-embedding-3-large

    async def initialize(self, kernel: Kernel) -> bool:
        """Initialize the search collection with embeddings and add it to the kernel."""
        if (
            not self.search_config
            or not self.search_config.endpoint
            or not self.search_config.index_name
        ):
            print("Search configuration not available")
            return False

        try:
            # Initialize Azure AI Search client
            self.search_client = SearchClient(
                endpoint=self.search_config.endpoint,
                credential=AzureKeyCredential(self.search_config.api_key),
                index_name=self.search_config.index_name,
            )

            # Initialize Azure OpenAI client for embeddings
            openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            self.embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
            embedding_dimensions_str = os.getenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS", "3072")
            
            try:
                self.embedding_dimensions = int(embedding_dimensions_str)
            except ValueError:
                self.embedding_dimensions = 3072
            
            if openai_endpoint and self.embedding_deployment:
                try:
                    credential = DefaultAzureCredential()
                    self.openai_client = AzureOpenAI(
                        azure_endpoint=openai_endpoint,
                        api_version="2024-12-01-preview",
                        azure_ad_token_provider=lambda: credential.get_token(
                            "https://cognitiveservices.azure.com/.default"
                        ).token
                    )
                    print(f"✅ OpenAI client initialized for embeddings ({self.embedding_deployment})")
                except Exception as e:
                    print(f"⚠️  Could not initialize OpenAI client for embeddings: {e}")
                    print("   Falling back to keyword-only search")
                    self.openai_client = None
            else:
                print("⚠️  Embedding configuration not found, using keyword-only search")
                self.openai_client = None

            # Add this class as a plugin so the agent can call search_documents
            kernel.add_plugin(self, plugin_name="knowledge_search")

            search_mode = "Hybrid + Semantic" if self.openai_client else "Keyword"
            print(
                f"✅ Added Azure AI Search plugin for index: {self.search_config.index_name} ({search_mode})"
            )
            return True

        except Exception as ex:
            print(f"❌ Could not initialize Azure AI Search: {ex}")
            return False

    def _generate_embedding(self, text: str) -> list[float] | None:
        """Generate embedding vector for text using Azure OpenAI."""
        if not self.openai_client or not self.embedding_deployment:
            return None
        
        try:
            # Truncate text if too long (max 8191 tokens for text-embedding-3-large)
            max_chars = 8191 * 4  # Rough estimate: 1 token ≈ 4 characters
            if len(text) > max_chars:
                text = text[:max_chars]
            
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.embedding_deployment
            )
            return response.data[0].embedding
        
        except Exception as e:
            print(f"⚠️  Error generating embedding: {e}")
            return None

    @kernel_function(
        name="search_documents",
        description="Search the knowledge base for relevant documents and information using hybrid search (keyword + semantic). Use this when you need to find specific information from internal documents or data.",
    )
    async def search_documents(self, query: str, limit: str = "3") -> str:
        """Search function that the agent can invoke to find relevant documents using hybrid search and semantic ranking."""
        if not self.search_client:
            return "Search service is not available."

        try:
            limit_int = int(limit)
            search_results = []

            # Generate embedding for vector search if available
            query_vector = None
            if self.openai_client:
                query_vector = self._generate_embedding(query)
            
            # Prepare search parameters
            search_params = {
                "search_text": query,
                "select": ["id", "title", "content", "type", "customer_id", "order_id"],
                "top": limit_int,
            }
            
            # Add vector search if embedding is available (Hybrid Search)
            if query_vector:
                vector_query = VectorizedQuery(
                    vector=query_vector,
                    k_nearest_neighbors=limit_int,
                    fields="content_vector"
                )
                search_params["vector_queries"] = [vector_query]
                search_params["query_type"] = "semantic"  # Enable semantic ranking
                search_params["semantic_configuration_name"] = "altyca-semantic-config"
            else:
                # Fallback to simple keyword search
                search_params["query_type"] = "simple"

            # Execute search
            results = self.search_client.search(**search_params)

            # Format results
            for result in results:
                doc_type = result.get('type', 'document')
                title = result.get('title', 'Untitled')
                content = result.get('content', '')
                
                # Include document type and title for better context
                formatted_result = f"[{doc_type}] {title}\n{content}"
                
                # Add customer/order references if available
                customer_id = result.get('customer_id')
                order_id = result.get('order_id')
                if customer_id:
                    formatted_result += f"\nCustomer: {customer_id}"
                if order_id:
                    formatted_result += f"\nOrder: {order_id}"
                
                search_results.append(formatted_result)

            if not search_results:
                return f"No relevant documents found for query: '{query}'"

            return "\n\n---\n\n".join(search_results)

        except Exception as ex:
            return f"Search failed: {str(ex)}"

    def is_available(self) -> bool:
        """Check if search functionality is available."""
        return self.search_client is not None


# Simple factory function
async def create_reasoning_search(
    kernel: Kernel, search_config: SearchConfig | None
) -> ReasoningSearch:
    """Create and initialize a ReasoningSearch instance."""
    search = ReasoningSearch(search_config)
    await search.initialize(kernel)
    return search
