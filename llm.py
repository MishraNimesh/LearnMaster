import os
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")

PRIMARY_MODEL = "gemini-3.5-flash-lite"
FALLBACK_MODELS = ["gemini-3.5-flash", "gemini-2.0-flash-lite", "gemini-2.0-flash"]


def _extract_text_content(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
        return "\n".join(parts)
    return str(content)


class SmartLLM:
    def invoke(self, prompt):
        models = [PRIMARY_MODEL] + FALLBACK_MODELS
        last_error = ""

        for model_name in models:
            try:
                chat = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=google_api_key,
                    temperature=0.7
                )
                res = chat.invoke(prompt)
                if res and hasattr(res, 'content') and res.content:
                    res.content = _extract_text_content(res.content)
                    return res
            except Exception as e:
                err_msg = str(e)
                last_error = err_msg
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    time.sleep(1.5)
                continue

        class ErrorFallbackResponse:
            content = f"Unable to reach LLM API. Details: {last_error}"

        return ErrorFallbackResponse()


llm = SmartLLM()
