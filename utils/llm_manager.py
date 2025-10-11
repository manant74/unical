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
            "gemini-1.5-pro": "Gemini 1.5 Pro",
            "gemini-1.5-flash": "Gemini 1.5 Flash",
            "gemini-pro": "Gemini Pro"
        },
        "Claude": {
            "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet",
            "claude-3-opus-20240229": "Claude 3 Opus",
            "claude-3-haiku-20240307": "Claude 3 Haiku"
        },
        "OpenAI": {
            "gpt-4-turbo-preview": "GPT-4 Turbo",
            "gpt-4": "GPT-4",
            "gpt-3.5-turbo": "GPT-3.5 Turbo"
        }
    }

    def __init__(self):
        self.clients = {}
        self._initialize_clients()

    def _initialize_clients(self):
        """Inizializza i client per i diversi provider"""
        # Gemini
        if os.getenv("GOOGLE_API_KEY"):
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.clients["Gemini"] = genai

        # Claude
        if os.getenv("ANTHROPIC_API_KEY"):
            self.clients["Claude"] = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            self.clients["OpenAI"] = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_available_providers(self) -> List[str]:
        """Restituisce la lista dei provider disponibili"""
        return list(self.clients.keys())

    def get_models_for_provider(self, provider: str) -> Dict[str, str]:
        """Restituisce i modelli disponibili per un provider"""
        return self.MODELS.get(provider, {})

    def chat(self, provider: str, model: str, messages: List[Dict],
             system_prompt: Optional[str] = None, context: Optional[str] = None) -> str:
        """Invia una richiesta di chat al modello selezionato"""

        if provider not in self.clients:
            raise ValueError(f"Provider {provider} non disponibile. Verifica le API keys.")

        # Prepara il contesto se disponibile
        if context:
            context_message = f"\n\nContesto RAG:\n{context}\n\n"
            if messages:
                messages[0]["content"] = context_message + messages[0]["content"]

        if provider == "Gemini":
            return self._chat_gemini(model, messages, system_prompt)
        elif provider == "Claude":
            return self._chat_claude(model, messages, system_prompt)
        elif provider == "OpenAI":
            return self._chat_openai(model, messages, system_prompt)

        raise ValueError(f"Provider {provider} non supportato")

    def _chat_gemini(self, model: str, messages: List[Dict], system_prompt: Optional[str]) -> str:
        """Chat con Gemini"""
        genai_model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt
        )

        # Converti messaggi
        chat_history = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [msg["content"]]})

        chat = genai_model.start_chat(history=chat_history)
        response = chat.send_message(messages[-1]["content"])

        return response.text

    def _chat_claude(self, model: str, messages: List[Dict], system_prompt: Optional[str]) -> str:
        """Chat con Claude"""
        kwargs = {
            "model": model,
            "max_tokens": 4096,
            "messages": messages
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.clients["Claude"].messages.create(**kwargs)
        return response.content[0].text

    def _chat_openai(self, model: str, messages: List[Dict], system_prompt: Optional[str]) -> str:
        """Chat con OpenAI"""
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        response = self.clients["OpenAI"].chat.completions.create(
            model=model,
            messages=messages
        )

        return response.choices[0].message.content
