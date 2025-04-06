from gemini_client import GeminiClient
from opensearch_client import OpenSearchClient
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenSearch client
opensearch_client = OpenSearchClient(
    host='localhost',
    port=9200,
    user='admin',
    password='YourStrongPassword123!',
    index='yash-index'  # make sure this is the one you indexed docs into
)

# Initialize Gemini client
gemini_client = GeminiClient(
    api_key="AIzaSyDbsRL_6x0nQCdvuE5lIV3GHsKTTiYB4c0"  # ✅ Replace this in production
)

def get_relevant_chunk(question, index_name):
    """
    Embed question using Gemini, retrieve most relevant chunk from OpenSearch.
    """
    try:
        logger.info("🔍 Generating embedding for the question...")
        question_embedding = gemini_client.create_embeddings(question)

        search_body = {
            "size": 1,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": question_embedding,
                        "k": 1
                    }
                }
            }
        }

        logger.info("📡 Querying OpenSearch for the most relevant chunk...")
        response = opensearch_client.search(index=index_name, body=search_body)
        hits = response.get("hits", {}).get("hits", [])
        
        if hits:
            logger.info("✅ Found relevant chunk.")
            return hits[0]["_source"]["text"]
        else:
            logger.warning("⚠️ No relevant chunk found.")
            return None
    except Exception as e:
        logger.error(f"❌ Error retrieving relevant chunk: {e}")
        return None

def process_question_with_gemini(question, index_name):
    """
    Fetch relevant context from OpenSearch, use Gemini to answer.
    """
    try:
        relevant_chunk = get_relevant_chunk(question, index_name)
        if not relevant_chunk:
            print("🚫 No relevant chunk found.")
            return

        prompt = f"Question: {question}\nContext: {relevant_chunk}\nAnswer:"
        logger.info("🧠 Sending prompt to Gemini...")
        
        gemini_response = gemini_client.execute_prompt(
            prompt=prompt,
            model="gemini-2.0-flash-exp"  # or the model you're using
        )

        print("\n🧾 Response from Gemini:")
        print(gemini_response)

    except Exception as e:
        logger.error(f"❌ Error processing the question: {e}")

if __name__ == "__main__":
    index_name = "yash-index"  # make sure it's consistent
    try:
        question = input("🤔 Enter your question: ")
        process_question_with_gemini(question, index_name)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user.")
