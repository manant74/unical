"""
System prompts per gli agenti del BDI Framework

Questo modulo carica i system prompts dai file Markdown nella directory prompts/
"""

import os
from pathlib import Path

# Cache per i prompts caricati
_prompts_cache = {}

def _load_prompt_from_file(agent_name: str) -> str:
    """
    Carica un system prompt da file Markdown

    Args:
        agent_name: Nome dell'agente (es. 'ali', 'believer')

    Returns:
        Il contenuto del file markdown come stringa

    Raises:
        FileNotFoundError: Se il file non esiste
    """
    # Costruisci il percorso del file
    current_dir = Path(__file__).parent.parent
    prompt_file = current_dir / "prompts" / f"{agent_name}_system_prompt.md"

    if not prompt_file.exists():
        raise FileNotFoundError(f"File prompt non trovato: {prompt_file}")

    # Leggi il contenuto del file
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()

def get_prompt(agent_name: str, use_cache: bool = True) -> str:
    """
    Restituisce il system prompt per un agente specifico

    Args:
        agent_name: Nome dell'agente ('ali', 'believer', 'cuma', 'genius')
        use_cache: Se True, usa la cache (default). Se False, ricarica sempre da file.

    Returns:
        Il system prompt corrispondente

    Raises:
        ValueError: Se l'agente non è riconosciuto
        FileNotFoundError: Se il file prompt non esiste
    """
    agent_name_lower = agent_name.lower()
    available_agents = ['ali', 'believer', 'cuma', 'genius', 'auditor']

    if agent_name_lower not in available_agents:
        raise ValueError(
            f"Agente '{agent_name}' non riconosciuto. "
            f"Agenti disponibili: {available_agents}"
        )

    # Se uso la cache e il prompt è già caricato, restituiscilo
    if use_cache and agent_name_lower in _prompts_cache:
        return _prompts_cache[agent_name_lower]

    # Carica il prompt dal file
    prompt = _load_prompt_from_file(agent_name_lower)

    # Memorizza in cache
    _prompts_cache[agent_name_lower] = prompt

    return prompt

def clear_cache():
    """
    Svuota la cache dei prompts.
    Utile se i file vengono modificati e si vuole ricaricarli.
    """
    global _prompts_cache
    _prompts_cache = {}

def get_all_prompts(use_cache: bool = True) -> dict:
    """
    Restituisce tutti i system prompts disponibili

    Args:
        use_cache: Se True, usa la cache

    Returns:
        Dizionario con tutti i prompts {agent_name: prompt_text}
    """
    agents = ['ali', 'believer', 'cuma', 'genius', 'auditor']
    prompts = {}

    for agent in agents:
        try:
            prompts[agent] = get_prompt(agent, use_cache=use_cache)
        except FileNotFoundError:
            prompts[agent] = f"[Prompt non disponibile per {agent}]"

    return prompts
