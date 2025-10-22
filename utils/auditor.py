import json
import re
from typing import Any, Dict, List, Optional

from utils.prompts import get_prompt


class ConversationAuditor:
    """Gestisce le chiamate all'agente Auditor per valutare le risposte degli altri agenti."""

    def __init__(self, llm_manager):
        self._llm_manager = llm_manager
        self._system_prompt = get_prompt("auditor")

    def review(
        self,
        provider: str,
        model: str,
        conversation: List[Dict[str, str]],
        module_name: str,
        module_goal: str,
        expected_outcome: str,
        context_summary: Optional[Dict[str, Any]] = None,
        last_user_message: Optional[str] = None,
        assistant_message: Optional[str] = None,
        history_limit: int = 8,
        temperature: float = 0.15,
        max_tokens: int = 900,
        top_p: float = 0.6,
    ) -> Optional[Dict[str, Any]]:
        """Invia la conversazione all'Auditor e restituisce il giudizio strutturato."""

        if not self._llm_manager or not provider or not model:
            return None

        excerpt = self._trim_history(conversation, history_limit)

        payload: Dict[str, Any] = {
            "module_name": module_name,
            "module_goal": module_goal,
            "expected_outcome": expected_outcome,
            "conversation_excerpt": excerpt,
            "latest_exchange": {
                "user": last_user_message or self._extract_last_role(excerpt, "user"),
                "assistant": assistant_message or self._extract_last_role(excerpt, "assistant"),
            },
            "context_summary": context_summary or {},
        }

        message_content = json.dumps(payload, ensure_ascii=False, indent=2)

        response = self._llm_manager.chat(
            provider=provider,
            model=model,
            messages=[{"role": "user", "content": message_content}],
            system_prompt=self._system_prompt,
            context=None,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stop_sequences=None,
        )

        parsed = self._extract_json(response)
        if parsed is not None:
            parsed["raw_response"] = response
        else:
            parsed = {"error": "parse_error", "raw_response": response}

        return parsed

    @staticmethod
    def _trim_history(history: List[Dict[str, str]], limit: int) -> List[Dict[str, str]]:
        trimmed = history[-limit:] if limit and len(history) > limit else history
        return [msg.copy() for msg in trimmed]

    @staticmethod
    def _extract_last_role(history: List[Dict[str, str]], role: str) -> str:
        for message in reversed(history):
            if message.get("role") == role:
                return message.get("content", "")
        return ""

    @staticmethod
    def _extract_json(text: str) -> Optional[Dict[str, Any]]:
        if not text:
            return None

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Cerca un blocco JSON all'interno del testo
        fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
        if fenced:
            try:
                return json.loads(fenced.group(1))
            except json.JSONDecodeError:
                pass

        # Fallback: trova la prima occorrenza di una struttura JSON
        brace_match = re.search(r"(\{.*\})", text, re.DOTALL)
        if brace_match:
            candidate = brace_match.group(1)
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                return None

        return None
