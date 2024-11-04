from pinecone.grpc import PineconeGRPC as Pinecone
import voyageai

from app_config import get_settings
from schemas.document import Document


class VectorService:
    _instance = None
    _pinecone_client: Pinecone

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorService, cls).__new__(cls)
            cls._instance._pinecone_client = Pinecone(api_key=get_settings().PINECONE_API_KEY)
            cls._instance._index = cls._instance._pinecone_client.Index("voyage-finance-production")
            cls._instance._embedder = voyageai.AsyncClient(api_key=get_settings().VOYAGEAI_API_KEY)
        return cls._instance

    async def store_document(self, document: Document) -> None:
        """
        Using the input document, embed the text and upsert into Pinecone
        """
        result = await self._embedder.embed([document.text], model="voyage-finance-2", input_type="document")
        metadata = {"content": document.text, "date_published": document.date_published.timestamp()}
        self._index.upsert([{"id": document.hash, "values": result.embeddings[0], "metadata": metadata}])

    def describe_index_stats(self):
        print(self._index.describe_index_stats())
