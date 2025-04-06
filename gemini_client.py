
import logging
import os
import google.generativeai as genai

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class GeminiClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)

    def create_embeddings(self, text: str, model: str = "models/embedding-001") -> list:
        try:
            response = genai.embed_content(
                model=model,
                content=text,
                task_type="retrieval_document"
            )
            return response.get("embedding")
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return None

    def execute_prompt(self, prompt: str, model: str = "gemini-2.0-flash-exp", temperature: float = 0, max_tokens: int = None, response_format: str = "application/json") -> str:
        max_tokens = max_tokens or int(os.getenv("MAX_OUTPUT_TOKENS_LLM", 2500))
        try:
            model = genai.GenerativeModel(model)
            genai_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type=response_format
            )
            response = model.generate_content(prompt, generation_config=genai_config)
            return response.text if response else ""
        except Exception as e:
            logger.error(f"Prompt execution error: {e}")
            return ""
