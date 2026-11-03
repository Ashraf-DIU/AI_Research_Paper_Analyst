import json
import re

from app.config import settings


class LLMNotConfigured(RuntimeError):
    pass


def get_llm(temperature: float = 0.1):
    if not settings.llm_api_key:
        raise LLMNotConfigured("LLM_API_KEY is not set. Configure an OpenAI-compatible provider.")
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url or None,
        temperature=temperature,
        timeout=settings.llm_timeout,
        max_retries=2,
    )


def complete(system: str, user: str, temperature: float = 0.1) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage

    resp = get_llm(temperature).invoke([SystemMessage(content=system), HumanMessage(content=user)])
    content = resp.content
    if isinstance(content, list):  # some providers return content blocks
        content = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in content)
    return str(content).strip()


def parse_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object in model output")
    return json.loads(text[start : end + 1])


def complete_json(system: str, user: str) -> dict:
    last = None
    for attempt in range(2):
        out = complete(system, user if attempt == 0 else user + "\n\nReturn valid JSON only.", temperature=0.0)
        try:
            return parse_json(out)
        except Exception as exc:  # retry once
            last = exc
    raise ValueError(f"Model did not return valid JSON: {last}")
