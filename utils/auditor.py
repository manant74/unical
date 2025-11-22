import json
import re
from typing import Any, Dict, List, Optional

from utils.prompts import get_prompt


FINALIZATION_KEYWORDS = [
    "procedi con il report",
    "procediamo con il report",
    "passiamo al report",
    "genera il report",
    "genera il json",
    "genera il report json",
    "produce il report",
    "produci il report",
    "produci il json",
    "dammi il report",
    "dammi il json",
    "mandami il report",
    "mandami il json",
    "rilascia il json",
    "salva in json",
    "chiudi con il json",
    "chiudiamo con il json",
    "concludi con il report",
    "formalizza il desire",
    "formalizza il report",
    "formalizza in json",
    "formalizza tutto",
    "finalizza il report",
    "finalizza in json",
    "report json finale",
    "json conclusivo",
    "checkpoint finale",
    "checkpoint pronto al report",
    "genera il riepilogo json",
]

FINALIZATION_VERBS = [
    "formalizza",
    "formalizzare",
    "formalizzi",
    "finalizza",
    "finalizzare",
    "finalizzi",
    "genera",
    "generare",
    "generami",
    "produci",
    "produrre",
    "prepara",
    "preparami",
    "procedi",
    "procediamo",
    "passiamo",
    "concludi",
    "concludiamo",
    "dammi",
    "mandami",
    "rilascia",
    "rilasciami",
    "chiudi",
    "chiudiamo",
    "completa",
]

FINALIZATION_OBJECTS = [
    "report",
    "json",
    "desire",
    "desiderio",
    "desideri",
    "desires",
    "belief",
    "beliefs",
    "output",
]

EXPECTED_FINALIZATION_KEYWORDS = [
    "report json finale",
    "report finale",
    "json conclusivo",
    "produrre il report",
    "generare il report",
    "formalizzare in json",
    "finalizzare in json",
    "chiudere con il report",
    "completare il report",
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

MODULE_STRUCTURED_MARKERS = {
    "ali": [
        "desire:",
        "desiderio:",
        "motivazione:",
        "motivation:",
        "successo:",
        "success metrics",
        "metriche di successo",
        "criteri di successo",
    ],
    "believer": [
        "belief:",
        "soggetto:",
        "relazione:",
        "oggetto:",
        "fonte:",
        "metadati:",
        "livello di confidenza",
    ]
}

MODULE_STRUCTURED_THRESHOLDS = {
    "ali": 2,
    "believer": 2,
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

        user_lower = user_message.lower() if user_message else ""

        user_finalization = self._user_requests_finalization(user_lower)
        structured_finalization = self._detect_structured_finalization(module_name, assistant_message)
        recent_json = self._assistant_recently_produced_json(excerpt)

        expected_finalization = False
        if expected_outcome:
            expected_finalization = self._expected_requests_finalization(expected_outcome)
            if expected_finalization and recent_json:
                expected_finalization = False

        finalization_requested = user_finalization or expected_finalization

        if not finalization_requested and not structured_finalization:
            return None

        has_json = self._extract_json(assistant_message) is not None
        if has_json:
            return None

        labels = MODULE_FINALIZATION_LABELS.get(module_name, MODULE_FINALIZATION_LABELS["default"])
        json_label = labels["json_label"]

        if user_finalization:
            summary = (
                f"L'utente ha richiesto la formalizzazione/generazione del {json_label}, "
                "ma la risposta non contiene alcun JSON. Il report e' necessario prima di proseguire."
            )
        elif expected_finalization:
            summary = (
                f"Il flusso corrente richiede il {json_label}, ma la risposta non contiene alcun JSON. "
                "Serve fornire il report prima di cambiare argomento."
            )
        else:
            summary = (
                f"Hai dichiarato una formalizzazione (es. Desire/Motivazione/Successo) senza fornire il {json_label}. "
                "Il contenuto non puo' essere salvato finche' non invii il JSON completo."
            )

        if user_finalization or expected_finalization:
            issue_message = f"Richiesto {json_label} di finalizzazione ma l'assistente ha risposto senza fornire un JSON valido."
            improvements = [
                f"Quando l'utente chiede di formalizzare o generare il {json_label}, fornisci subito il JSON completo prima di cambiare argomento."
            ]
        else:
            issue_message = f"Hai indicato Desire/Motivazione/Successo ma non hai prodotto il {json_label}; senza JSON non e' possibile salvare la formalizzazione."
            improvements = [
                f"Quando dichiari di aver formalizzato il {labels['object']}, fornisci immediatamente il {json_label}."
            ]

        issues = [{
            "type": "format",
            "severity": "high",
            "message": issue_message
        }]

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

    def _detect_structured_finalization(self, module_name: str, assistant_message: str) -> bool:
        text = assistant_message.lower()
        markers = MODULE_STRUCTURED_MARKERS.get(module_name, [])
        if not markers:
            return False

        hits = sum(1 for marker in markers if marker in text)
        threshold = MODULE_STRUCTURED_THRESHOLDS.get(module_name, 3)
        return hits >= threshold

    @staticmethod
    def _assistant_recently_produced_json(excerpt: Optional[List[Dict[str, str]]]) -> bool:
        if not excerpt:
            return False

        skip_current = True
        for message in reversed(excerpt):
            if message.get("role") != "assistant":
                continue

            if skip_current:
                skip_current = False
                continue

            content = message.get("content", "")
            if content and ConversationAuditor._extract_json(content) is not None:
                return True
            break

        return False

    @staticmethod
    def _user_requests_finalization(text: str) -> bool:
        if not text:
            return False

        for phrase in FINALIZATION_KEYWORDS:
            if phrase in text:
                return True

        if any(verb in text for verb in FINALIZATION_VERBS):
            if any(obj in text for obj in FINALIZATION_OBJECTS):
                return True

        return False

    @staticmethod
    def _expected_requests_finalization(expected_text: Optional[str]) -> bool:
        if not expected_text:
            return False

        text = expected_text.lower()
        for phrase in FINALIZATION_KEYWORDS + EXPECTED_FINALIZATION_KEYWORDS:
            if phrase in text:
                return True

        if any(verb in text for verb in FINALIZATION_VERBS):
            if any(obj in text for obj in FINALIZATION_OBJECTS):
                return True

        return False

