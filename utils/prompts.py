"""
System prompts for BDI Framework agents

This module loads system prompts from Markdown files in the prompts/ directory
"""

import os
from pathlib import Path

# Cache per i prompts caricati
_prompts_cache = {}

def _load_prompt_from_file(agent_name: str, prompt_suffix: str = "system_prompt") -> str:
    """
    Loads a system prompt from a Markdown file

    Args:
        agent_name: Agent name (e.g., 'ali', 'believer')
        prompt_suffix: Prompt file suffix (default: 'system_prompt')

    Returns:
        The markdown file content as a string

    Raises:
        FileNotFoundError: If the file does not exist
    """
    # Costruisci il percorso del file
    current_dir = Path(__file__).parent.parent
    prompt_file = current_dir / "prompts" / f"{agent_name}_{prompt_suffix}.md"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    # Leggi il contenuto del file
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()

def get_prompt(agent_name: str, use_cache: bool = True, prompt_suffix: str = "system_prompt") -> str:
    """
    Returns the system prompt for a specific agent

    Args:
        agent_name: Agent name ('ali', 'believer', 'cuma', 'genius')
        use_cache: If True, use cache (default). If False, always reload from file.
        prompt_suffix: Prompt file suffix (default: 'system_prompt')

    Returns:
        The corresponding system prompt

    Raises:
        ValueError: If the agent is not recognized
        FileNotFoundError: If the prompt file does not exist
    """
    agent_name_lower = agent_name.lower()
    available_agents = [
        'ali',
        'believer',
        'cuma',
        'genius',
        'auditor',
        'desires_auditor',
        'belief_auditor',
    ]

    if agent_name_lower not in available_agents:
        raise ValueError(
            f"Agent '{agent_name}' not recognized. "
            f"Available agents: {available_agents}"
        )

    # Crea una chiave di cache che include il suffisso
    cache_key = f"{agent_name_lower}_{prompt_suffix}"

    # Se uso la cache e il prompt è già caricato, restituiscilo
    if use_cache and cache_key in _prompts_cache:
        return _prompts_cache[cache_key]

    # Carica il prompt dal file
    prompt = _load_prompt_from_file(agent_name_lower, prompt_suffix)

    # Memorizza in cache
    _prompts_cache[cache_key] = prompt

    return prompt

def clear_cache():
    """
    Clears the prompts cache.
    Useful if files are modified and need to be reloaded.
    """
    global _prompts_cache
    _prompts_cache = {}

def get_all_prompts(use_cache: bool = True) -> dict:
    """
    Returns all available system prompts

    Args:
        use_cache: If True, use cache

    Returns:
        Dictionary with all prompts {agent_name: prompt_text}
    """
    agents = [
        'ali',
        'believer',
        'cuma',
        'genius',
        'auditor',
        'desires_auditor',
        'belief_auditor',
    ]
    prompts = {}

    for agent in agents:
        try:
            prompts[agent] = get_prompt(agent, use_cache=use_cache)
        except FileNotFoundError:
            prompts[agent] = f"[Prompt not available for {agent}]"

    return prompts
