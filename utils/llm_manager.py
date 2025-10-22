import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from anthropic import Anthropic
from openai import OpenAI

# Carica le variabili d'ambiente dal file .env
load_dotenv()

class LLMManager:
    """Gestisce le interazioni con diversi modelli LLM"""

    MODELS = {
        "Gemini": {
            "gemini-2.5-flash-lite": "Gemini 2.5 Flash Lite",
            "gemini-2.5-flash": "Gemini 2.5 Flash",
            "gemini-2.5-pro": "Gemini 2.5 Pro"
        },
        "Claude": {
            "claude-3.7-sonnet": "Claude 3.7 Sonnet",
            "claude-4-sonnet": "Claude 4 Sonnet",
            "claude-4-opus": "Claude 4 Opus",
             "claude-4.5-sonnet": "Claude 4.5 Sonnet"
       },
        "OpenAI": {
            "gpt-4o": "GPT-4o",
            "gpt-4o-mini": "GPT-4o Mini",
            "gpt-4.1": "GPT-4.1",
            "gpt-4-turbo": "GPT-4 Turbo",
            "gpt-5": "GPT-5",
            "gpt-5-nano": "GPT-5 Nano",
            "gpt-5-mini": "GPT-5 Mini",
            "o1-mini": "o1 Mini",
            "o1-pro": "o1 Pro",
            "03-mini": "03 Mini"
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

        # Claude
        if os.getenv("ANTHROPIC_API_KEY"):
            self.clients["Claude"] = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


    def get_available_providers(self) -> List[str]:
        """Restituisce la lista dei provider disponibili"""
        return list(self.clients.keys())

    def get_models_for_provider(self, provider: str) -> Dict[str, str]:
        """Restituisce i modelli disponibili per un provider"""
        return self.MODELS.get(provider, {})

    def chat(self, provider: str, model: str, messages: List[Dict],
             system_prompt: Optional[str] = None, context: Optional[str] = None,
             temperature: float = 0.7, max_tokens: int = 2000, top_p: float = 0.9,
             stop_sequences: Optional[List[str]] = None) -> str:
        """
        Invia una richiesta di chat al modello selezionato

        Args:
            provider: Provider LLM (Gemini, Claude, OpenAI)
            model: Nome del modello
            messages: Lista di messaggi della conversazione
            system_prompt: Prompt di sistema (opzionale)
            context: Contesto aggiuntivo da RAG (opzionale)
            temperature: Controllo creatività (0.0-2.0, default 0.7)
            max_tokens: Lunghezza massima risposta (default 2000)
            top_p: Nucleus sampling (0.0-1.0, default 0.9)
            stop_sequences: Sequenze di stop (opzionale)

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
            return self._chat_gemini(model, messages, system_prompt, temperature, max_tokens, top_p, stop_sequences)
        elif provider == "Claude":
            return self._chat_claude(model, messages, system_prompt, temperature, max_tokens, top_p, stop_sequences)
        elif provider == "OpenAI":
            return self._chat_openai(model, messages, system_prompt, temperature, max_tokens, top_p, stop_sequences)

        raise ValueError(f"Provider {provider} non supportato")

    def _chat_gemini(self, model: str, messages: List[Dict], system_prompt: Optional[str],
                     temperature: float, max_tokens: int, top_p: float,
                     stop_sequences: Optional[List[str]]) -> str:
        """Chat con Gemini"""
        # Configura i parametri di generazione
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,  # Gemini usa "max_output_tokens"
            "top_p": top_p,
        }

        if stop_sequences:
            generation_config["stop_sequences"] = stop_sequences

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

    def _chat_claude(self, model: str, messages: List[Dict], system_prompt: Optional[str],
                     temperature: float, max_tokens: int, top_p: float,
                     stop_sequences: Optional[List[str]]) -> str:
        """Chat con Claude"""
        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        if stop_sequences:
            kwargs["stop_sequences"] = stop_sequences[:4]  # Claude supporta max 4

        response = self.clients["Claude"].messages.create(**kwargs)
        return response.content[0].text

    def _chat_openai(self, model: str, messages: List[Dict], system_prompt: Optional[str],
                     temperature: float, max_tokens: int, top_p: float,
                     stop_sequences: Optional[List[str]]) -> str:
        """Chat con OpenAI"""
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
        }

        if stop_sequences:
            kwargs["stop"] = stop_sequences[:4]  # OpenAI supporta max 4

        client = self.clients["OpenAI"]

        try:
            response = client.chat.completions.create(**kwargs)
        except Exception as exc:  # pylint: disable=broad-except
            error_text = str(exc)
            needs_completion_tokens = (
                "max_tokens" in error_text
                and "max_completion_tokens" in error_text
            )
            needs_output_tokens = (
                "max_tokens" in error_text
                and "max_output_tokens" in error_text
            )

            if needs_completion_tokens or needs_output_tokens:
                kwargs.pop("max_tokens", None)
                fallback_key = "max_completion_tokens" if needs_completion_tokens else "max_output_tokens"
                kwargs[fallback_key] = max_tokens
                response = client.chat.completions.create(**kwargs)
            else:
                raise

        return response.choices[0].message.content
