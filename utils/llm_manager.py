import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI
from utils.llm_manager_config import MODEL_PARAMETERS

# Carica le variabili d'ambiente dal file .env
load_dotenv()

class LLMManager:
    """Gestisce le interazioni con diversi modelli LLM"""

    MODELS = {
        "Gemini": {
            "gemini-2.5-flash-lite": "Gemini 2.5 Flash Lite",
            "gemini-2.5-flash": "Gemini 2.5 Flash",
            "gemini-2.5-pro": "Gemini 2.5 Pro",
            "gemini-3-pro-preview": "Gemini 3 Pro (Preview)"
        },
        "OpenAI": {
            "gpt-5": "GPT-5",
            "gpt-5-nano": "GPT-5 Nano",
            "gpt-5-mini": "GPT-5 Mini",
            "gpt-5.1": "GPT-5.1 (Thinking)",
            "gpt-5.1-chat-latest": "GPT-5.1 Instant",
            "gpt-5.2": "GPT-5.2",
            "gpt-5.2-pro": "GPT-5.2 Pro",
            "gpt-5.2-chat-latest": "GPT-5.2 Instant"
        }
    }

    def __init__(self):
        self.clients = {}
        self._initialize_clients()

    def _initialize_clients(self):
        """Inizializza i client per i diversi provider"""
        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            self.clients["OpenAI"] = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Gemini
        if os.getenv("GOOGLE_API_KEY"):
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.clients["Gemini"] = genai


    def get_available_providers(self) -> List[str]:
        """Restituisce la lista dei provider disponibili"""
        return list(self.clients.keys())

    def get_models_for_provider(self, provider: str) -> Dict[str, str]:
        """Restituisce i modelli disponibili per un provider"""
        return self.MODELS.get(provider, {})

    def get_model_parameters(self, model: str) -> Dict[str, Dict]:
        """
        Restituisce i parametri supportati da un modello specifico.

        Args:
            model: Nome del modello (es: "gpt-5.1", "gemini-2.5-flash")

        Returns:
            Dizionario dei parametri con metadata per rendering UI.
            Se il modello non è configurato, restituisce dizionario vuoto.
        """
        return MODEL_PARAMETERS.get(model, {})

    def chat(self, provider: str, model: str, messages: List[Dict],
             system_prompt: Optional[str] = None, context: Optional[str] = None,
             temperature: float = 1.0, max_tokens: int = 65536, top_p: float = 1,
             reasoning_effort: Optional[str] = 'medium', use_defaults: bool = False) -> str:
        """
        Invia una richiesta di chat al modello selezionato

        Args:
            provider: Provider LLM (Gemini, OpenAI)
            model: Nome del modello
            messages: Lista di messaggi della conversazione
            system_prompt: Prompt di sistema (opzionale)
            context: Contesto aggiuntivo da RAG (opzionale)
            temperature: Controllo creatività (0.0-2.0, default 0.7) - Ignorato per modelli GPT-5/GPT-5.1/o1/o3
            max_tokens: Lunghezza massima risposta (default 2000) - Ignorato per modelli GPT-5/GPT-5.1/o1/o3
            top_p: Nucleus sampling (0.0-1.0, default 0.9) - Ignorato per modelli GPT-5/GPT-5.1/o1/o3
            reasoning_effort: Effort di reasoning per modelli GPT-5/GPT-5.1/o1/o3 ("none", "low", "medium", "high")
                - "none": Disabilita il reasoning (GPT-5.1 si comporta come modello standard)
                - "low", "medium", "high": Abilita reasoning con diversi livelli
            use_defaults: Se True, usa i parametri di default del provider e ignora temperature/max_tokens/top_p

        Returns:
            Risposta del modello LLM
        """

        if provider not in self.clients:
            raise ValueError(f"Provider {provider} non disponibile. Verifica le API keys.")

        # Prepara il contesto se disponibile
        if context:
            context_message = f"\n\nContesto RAG:\n{context}\n\n"
            if messages:
                messages[0]["content"] = context_message + messages[0]["content"]

        if provider == "Gemini":
            return self._chat_gemini(model, messages, system_prompt, temperature, max_tokens, top_p, use_defaults)
        elif provider == "OpenAI":
            return self._chat_openai(model, messages, system_prompt, temperature, max_tokens, top_p, reasoning_effort, use_defaults)

        raise ValueError(f"Provider {provider} non supportato")

    def _chat_gemini(self, model: str, messages: List[Dict], system_prompt: Optional[str],
                     temperature: float, max_tokens: int, top_p: float, use_defaults: bool = False) -> str:
        """Chat con Gemini"""
        # Configura i parametri di generazione solo se use_defaults è False
        generation_config = None
        if not use_defaults:
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,  # Gemini usa "max_output_tokens"
                "top_p": top_p,
            }

        genai_model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt,
            generation_config=generation_config
        )

        # Converti messaggi
        chat_history = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [msg["content"]]})

        chat = genai_model.start_chat(history=chat_history)
        response = chat.send_message(messages[-1]["content"])

        return response.text

    def _chat_openai(self, model: str, messages: List[Dict], system_prompt: Optional[str],
                     temperature: float, max_tokens: int, top_p: float,
                     reasoning_effort: Optional[str] = None, use_defaults: bool = False) -> str:
        """Chat con OpenAI"""
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        kwargs = {
            "model": model,
            "messages": messages,
        }

        # I modelli GPT-5, GPT-5.1 e o1/o3 hanno restrizioni sui parametri
        # Supportano solo reasoning_effort, non temperature/top_p
        is_reasoning_model = model.startswith(("gpt-5", "o1", "o3"))

        if is_reasoning_model:
            # Modelli con reasoning: usa solo reasoning_effort
            # Nota: GPT-5.1 supporta reasoning_effort = "none" per comportamento non-reasoning
            if reasoning_effort:
                kwargs["reasoning_effort"] = reasoning_effort
        else:
            # Modelli standard supportano tutti i parametri
            # Aggiungi parametri solo se use_defaults è False
            if not use_defaults:
                kwargs["max_tokens"] = max_tokens
                kwargs["temperature"] = temperature
                kwargs["top_p"] = top_p

        client = self.clients["OpenAI"]

        try:
            response = client.chat.completions.create(**kwargs)
        except Exception as exc:  # pylint: disable=broad-except
            error_text = str(exc)
            needs_completion_tokens = (
                "max_tokens" in error_text
            )
            needs_output_tokens = (
                "max_tokens" in error_text
            )

            if needs_completion_tokens or needs_output_tokens:
                kwargs.pop("max_tokens", None)
                response = client.chat.completions.create(**kwargs)
            else:
                raise

        return response.choices[0].message.content
