"""
Configurazione dei parametri LLM per ogni modello supportato.
Questa configurazione è usata da Compass per renderizzare dinamicamente
i controlli UI in base al modello selezionato.
"""

# Dizionario centrale con metadati di tutti i parametri per ogni modello
MODEL_PARAMETERS = {
    # ==================== OPENAI - MODELLI CON REASONING ====================
    "gpt-5": {
        "reasoning_effort": {
            "type": "selectbox",
            "options": ["low", "medium", "high"],
            "default": "medium",
            "label": "Reasoning Effort",
            "help": "Livello di ragionamento: low=veloce, high=accurato"
        }
    },
    "gpt-5-nano": {
        "reasoning_effort": {
            "type": "selectbox",
            "options": ["low", "medium", "high"],
            "default": "medium",
            "label": "Reasoning Effort",
            "help": "Livello di ragionamento: low=veloce, high=accurato"
        }
    },
    "gpt-5-mini": {
        "reasoning_effort": {
            "type": "selectbox",
            "options": ["low", "medium", "high"],
            "default": "medium",
            "label": "Reasoning Effort",
            "help": "Livello di ragionamento: low=veloce, high=accurato"
        }
    },

    # ==================== OPENAI - GPT-5.1 SERIES ====================
    "gpt-5.1": {
        "reasoning_effort": {
            "type": "selectbox",
            "options": ["none", "low", "medium", "high"],
            "default": "medium",
            "label": "Reasoning Effort",
            "help": "none=veloce senza reasoning, high=reasoning profondo"
        }
    },
    "gpt-5.1-chat-latest": {
        "reasoning_effort": {
            "type": "selectbox",
            "options": ["none", "low", "medium", "high"],
            "default": "none",
            "label": "Reasoning Effort",
            "help": "Instant model: usa 'none' per latenza minima (consigliato)"
        }
    },
    "gpt-5.2": {
        "reasoning_effort": {
            "type": "selectbox",
            "options": ["none", "low", "medium", "high"],
            "default": "medium",
            "label": "Reasoning Effort",
            "help": "Livello di ragionamento per GPT-5.2: low=veloce, high=molto accurato"
        }
    },
    "gpt-5.2-pro": {
        "reasoning_effort": {
            "type": "selectbox",
            "options": ["none", "low", "medium", "high"],
            "default": "high",
            "label": "Reasoning Effort",
            "help": "Versione Pro: default su 'high' per massima accuratezza"
        }
    },
    "gpt-5.2-chat-latest": {
        "reasoning_effort": {
            "type": "selectbox",
            "options": ["none", "low", "medium", "high"],
            "default": "none",
            "label": "Reasoning Effort",
            "help": "Instant model: usa 'none' per latenza minima (consigliato)"
        }
    },

    # ==================== GOOGLE GEMINI ====================
    "gemini-2.5-flash-lite": {
        "temperature": {
            "type": "slider",
            "min": 0.0,
            "max": 2.0,
            "step": 0.1,
            "default": 1.0,
            "label": "Temperature",
            "help": "Controlla creatività della risposta"
        },
        "max_output_tokens": {
            "type": "number",
            "min": 1,
            "max": 65536,
            "step": 512,
            "default": 4096,
            "label": "Max Output Tokens",
            "help": "Lunghezza massima output (supporta fino a 64k)"
        },
        "top_p": {
            "type": "slider",
            "min": 0.0,
            "max": 1.0,
            "step": 0.05,
            "default": 0.95,
            "label": "Top P",
            "help": "Nucleus sampling per Gemini"
        }
    },
    "gemini-2.5-flash": {
        "temperature": {
            "type": "slider",
            "min": 0.0,
            "max": 2.0,
            "step": 0.1,
            "default": 1.0,
            "label": "Temperature",
            "help": "Controlla creatività della risposta"
        },
        "max_output_tokens": {
            "type": "number",
            "min": 1,
            "max": 65536,
            "step": 1024,
            "default": 8192,
            "label": "Max Output Tokens",
            "help": "Lunghezza massima output"
        },
        "top_p": {
            "type": "slider",
            "min": 0.0,
            "max": 1.0,
            "step": 0.05,
            "default": 0.95,
            "label": "Top P",
            "help": "Nucleus sampling per Gemini"
        }
    },
    "gemini-2.5-pro": {
        "temperature": {
            "type": "slider",
            "min": 0.0,
            "max": 2.0,
            "step": 0.1,
            "default": 1.0,
            "label": "Temperature",
            "help": "Controlla creatività della risposta"
        },
        "max_output_tokens": {
            "type": "number",
            "min": 1,
            "max": 65536,
            "step": 1024,
            "default": 8192,
            "label": "Max Output Tokens",
            "help": "Lunghezza massima output"
        },
        "top_p": {
            "type": "slider",
            "min": 0.0,
            "max": 1.0,
            "step": 0.05,
            "default": 0.95,
            "label": "Top P",
            "help": "Nucleus sampling per Gemini"
        }
    },

    # ==================== GOOGLE GEMINI 3 ====================
    "gemini-3-pro-preview": {
        "temperature": {
            "type": "slider",
            "min": 0.0,
            "max": 2.0,
            "step": 0.1,
            "default": 1.0,
            "label": "Temperature",
            "help": "Controlla creatività della risposta"
        },
        "max_output_tokens": {
            "type": "number",
            "min": 1,
            "max": 65536,
            "step": 1024,
            "default": 8192,
            "label": "Max Output Tokens",
            "help": "Lunghezza massima output (supporta fino a 64k)"
        },
        "top_p": {
            "type": "slider",
            "min": 0.0,
            "max": 1.0,
            "step": 0.05,
            "default": 0.95,
            "label": "Top P",
            "help": "Nucleus sampling per Gemini 3"
        }
    }
}
