import asyncio
import datetime

from pinecone.grpc import PineconeGRPC as Pinecone
import voyageai
from voyageai.object import RerankingObject

from app_config import get_settings
from schemas.document import Document
from schemas.query_result import QueryResult
from schemas.rerank_result import RerankResult
from services.anthropic_service import AnthropicService


class VectorService:
    _instance = None
    _pinecone_client: Pinecone

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorService, cls).__new__(cls)
            cls._instance._pinecone_client = Pinecone(api_key=get_settings().PINECONE_API_KEY)
            cls._instance._index = cls._instance._pinecone_client.Index("voyage-finance-production")
            cls._instance._voyage_client = voyageai.AsyncClient(api_key=get_settings().VOYAGEAI_API_KEY)
        return cls._instance

    async def store_document(self, document: Document) -> None:
        """
        Using the input document, embed the text and upsert into Pinecone
        """
        result = await self._voyage_client.embed([document.text], model="voyage-finance-2", input_type="document")
        metadata = {"content": document.text, "date_published": document.date_published.timestamp()}
        self._index.upsert([{"id": document.hash, "values": result.embeddings[0], "metadata": metadata}])

    async def retrieve_top_k_results(self, query: str, date_cutoff: datetime.datetime, k: int = 64) -> list[QueryResult]:
        query_embeddings = await self._voyage_client.embed([query], model="voyage-finance-2", input_type="query")

        search_filter = {"date_published": {"$gte": int(date_cutoff.timestamp())}}

        # Search the index for the three most similar vectors
        results = self._index.query(
            vector=query_embeddings.embeddings[0], top_k=k, include_values=False, include_metadata=True, filter=search_filter
        )
        return list(
            map(
                lambda result: QueryResult(
                    id=result.get("id"),
                    content=result.get("metadata").get("content"),
                    date_published=result.get("metadata").get("date_published"),
                ),
                results.get("matches"),
            )
        )

    async def rerank_results(self, query: str, results: list[QueryResult]) -> list[RerankResult]:

        documents: list[str] = list(map(lambda doc: doc.content, results))
        results: RerankingObject = await self._voyage_client.rerank(query, documents, model="rerank-2", top_k=32)
        return list(map(lambda result: RerankResult(index=result.index, content=result.document), results.results))

    def describe_index_stats(self):
        print(self._index.describe_index_stats())
