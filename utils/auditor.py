import json
import re
from typing import Any, Dict, List, Optional

from utils.prompts import get_prompt


FINALIZATION_KEYWORDS = [
    "formalizza",
    "formalizzare",
    "formalizzato",
    "formalizzazione",
    "formalization",
    "finalizza",
    "finalizzare",
    "finalizzato",
    "finalizzazione",
    "finalization",
    "report",
    "report finale",
    "report json",
    "json finale",
    "genera il report",
    "generate the report",
    "generate report",
    "genera il json",
    "generate the json",
    "produce il report",
    "produce il json",
    "produrre il report",
    "produrre il json",
    "passiamo al report",
    "procedi con il report",
    "procedere con il report",
    "procedi con il json",
    "dammi il report",
    "dammi il json",
    "rilascia il json",
    "salva in json",
    "chiudi con il json",
    "chiudi il modulo",
    "concludi con il report",
    "checkpoint finale",
    "check finale",
    "riassunto finale",
    "json conclusivo"
]

EXPECTED_FINALIZATION_KEYWORDS = [
    "report",
    "json",
    "formalizzazione",
    "finalizzazione",
    "conclusione",
]

MODULE_FINALIZATION_LABELS = {
    "ali": {
        "object": "desire",
        "json_label": "report JSON dei desire",
    },
    "believer": {
        "object": "belief",
        "json_label": "report JSON dei belief",
    },
    "default": {
        "object": "output",
        "json_label": "report JSON richiesto",
    }
}


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

        enforcement = self._force_json_if_needed(
            module_name=module_name,
            expected_outcome=expected_outcome,
            last_user_message=last_user_message,
            assistant_message=assistant_message,
            excerpt=excerpt,
        )
        if enforcement:
            return enforcement

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
            top_p=top_p
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

    def _force_json_if_needed(
        self,
        module_name: str,
        expected_outcome: Optional[str],
        last_user_message: Optional[str],
        assistant_message: Optional[str],
        excerpt: Optional[List[Dict[str, str]]]
    ) -> Optional[Dict[str, Any]]:
        if not assistant_message:
            return None

        user_message = last_user_message
        if not user_message and excerpt:
            user_message = self._extract_last_role(excerpt, "user")

        if not user_message:
            return None

        user_lower = user_message.lower()
        finalization_requested = any(keyword in user_lower for keyword in FINALIZATION_KEYWORDS)

        if not finalization_requested and expected_outcome:
            expected_lower = expected_outcome.lower()
            finalization_requested = any(keyword in expected_lower for keyword in EXPECTED_FINALIZATION_KEYWORDS)

        if not finalization_requested:
            return None

        has_json = self._extract_json(assistant_message) is not None
        if has_json:
            return None

        labels = MODULE_FINALIZATION_LABELS.get(module_name, MODULE_FINALIZATION_LABELS["default"])
        json_label = labels["json_label"]

        summary = (
            f"L'utente ha richiesto la formalizzazione/generazione del {json_label}, "
            "ma la risposta non contiene alcun JSON. Il report è necessario prima di proseguire."
        )

        issues = [{
            "type": "format",
            "severity": "high",
            "message": f"Richiesto {json_label} di finalizzazione ma l'assistente ha risposto senza fornire un JSON valido."
        }]

        improvements = [
            f"Quando l'utente chiede di formalizzare o generare il {json_label}, fornisci subito il JSON completo prima di cambiare argomento."
        ]

        suggested_reply = {
            "message": f"Per favore genera ora il {json_label} completo prima di procedere.",
            "why": f"Senza il {json_label} non possiamo salvare e confermare l'output del modulo."
        }

        next_focus = f"Produrre il {json_label} richiesto dall'utente prima di passare ad altro."

        return {
            "status": "revise",
            "summary": summary,
            "issues": issues,
            "assistant_improvements": improvements,
            "suggested_user_replies": [suggested_reply],
            "next_focus": next_focus,
            "confidence": "high"
        }
