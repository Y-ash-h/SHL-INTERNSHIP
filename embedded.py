

from pymongo import MongoClient
from opensearch_client import OpenSearchClient
from gemini_client import GeminiClient
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB config
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["shl_db"]
mongo_collection = mongo_db["products_rag"]

# OpenSearch config
opensearch_client = OpenSearchClient(
    host='localhost',
    port=9200,
    user='admin',
    password='YourStrongPassword123!',
    index='yash-index'
)

# Gemini API config
gemini_client = GeminiClient(api_key="AIzaSyDbsRL_6x0nQCdvuE5lIV3GHsKTTiYB4c0")


def create_opensearch_index(index_name: str, dimension: int = 768):
    """
    Create an OpenSearch index with KNN vector support for embeddings.
    """
    index_body = {
        "settings": {
            "index": {
                "knn": True,
                "knn.algo_param": {
                    "ef_search": 100
                }
            }
        },
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "text": {"type": "text"},
                "embeddings": {
                    "type": "knn_vector",
                    "dimension": dimension,
                    "method": {
                        "engine": "faiss",
                        "space_type": "l2",
                        "name": "hnsw"
                    }
                }
            }
        }
    }

    if not opensearch_client.client.indices.exists(index=index_name):
        opensearch_client.client.indices.create(index=index_name, body=index_body)
        logger.info(f"✅ Index '{index_name}' created.")
    else:
        logger.info(f"ℹ️ Index '{index_name}' already exists.")


def process_and_store_embeddings(mongo_collection, index_name: str):
    """
    Generate embeddings from MongoDB documents and store them in OpenSearch.
    """
    create_opensearch_index(index_name)

    records = mongo_collection.find({}, {"text": 1, "content": 1})  # Include content field in query

    for record in records:
        record_id = str(record.get("_id"))
        text = record.get("text") or record.get("content")

        if not text:
            logger.warning(f"⚠️ Skipping record '{record_id}': missing 'text' or 'content' field.")
            continue

        embedding = gemini_client.create_embeddings(text)
        if not embedding:
            logger.warning(f"⚠️ Failed to generate embedding for record {record_id}")
            continue

        doc = {
            "id": record_id,
            "text": text,
            "embeddings": embedding
        }

        try:
            response_id = opensearch_client.index_doc(doc)
            logger.info(f"✅ Document {response_id} indexed successfully.")
        except Exception as e:
            logger.error(f"❌ Error indexing document {record_id}: {e}")


if __name__ == "__main__":
    process_and_store_embeddings(mongo_collection, "yash-index")
