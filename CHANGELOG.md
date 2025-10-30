# Changelog

Tutte le modifiche significative a questo progetto saranno documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## Release - 2025-01-30

### Home Page

- **Traduzione completa in inglese**

### 🎯 Nuova Architettura Sessioni

**SessionManager** - Sistema completo di gestione sessioni multi-utente. La Sessione ora è una area di lavoro  su cui più utenti possono lavorare anche in giorni diversi per arrivare al completamento

- CRUD operations per sessioni (create, read, update, delete)
- Persistenza su filesystem in formato JSON
- Metadata tracking: created_at, updated_at, status
- Gestione sessione attiva e switching tra sessioni
- Export/Import sessioni complete

Il modulo di Gestione della Sessione ha preso il nome di **Compass** e permette di configurare:

- Nome e Descrizione
- LLM da usare e configuraizone parametri LLM (temperature, max_tokens, top_p)
- Nome della Knowledge Base da usare con relativi dettagli

Compass permette di tracciare e visualizza tutti i Beliefs e i Desire emersi durante le fasi del workflow
Permette editing diretto dei desire e dei beliefs emersi

***Struttura Dati Sessione***

```json
{
  "metadata": {
    "name": "Session Name",
    "description": "...",
    "created_at": "ISO-8601",
    "updated_at": "ISO-8601",
    "status": "active|archived"
  },
  "config": {
    "context": "context_name",
    "llm_provider": "Claude|Gemini|OpenAI",
    "llm_model": "model-name",
    "llm_settings": {
      "temperature": 0.7,
      "max_tokens": 2000,
      "top_p": 0.9
    }
  },
  "belief_base": [...],
  "current_bdi": {...}
}
```

#### 🗂️ Nuovo Modulo di Gestione del Contesto

**Knol** - E' il nuovo nome del modulo per la gestione delle knowledge base

- Gestione di più Knowledge Base usabili nelle varie sessioni
- Caricamento di PDF, file di testo, pagine web, file markdown
- Struttura dati separata per ogni contesto
- Export/Import contesti in formato ZIP
- Generazione automatica Vector Store del contesto
- Estrazione Automatica dei Beliefs di base associabili al contesto
- Visualizzaizone delle fonti presenti nel contesto

***Struttura Directory Contesti***

```text
data/contexts/
  ├── context_name_1/
  │   ├── context_metadata.json
  │   ├── belief_base.json
  │   └── chroma_db/
  ├── context_name_2/
  │   ├── context_metadata.json
  │   ├── belief_base.json
  │   └── chroma_db/
```

#### 🎯 Ali & Believer Updates

***Ali (Desires Agent)***

- Integrazione con nuovo sistema sessioni
- Caricamento automatico sessione attiva
- Accesso al contesto della sessione
- Salvataggio desires nel BDI della sessione
- UI ottimizzata con session badge
- Link rapido a Compass

***Believer (Beliefs Agent)***

- Integrazione con sistema sessioni
- Gestione beliefs BDI separati da belief base
- Auto-recovery sessione attiva
- Parsing migliorato per beliefs strutturati
- UI con session context

### 🎯 Auditor System

#### Nuova Feature: Auditor Agent

- **Sistema di auditing automatico** per desires e beliefs
- Validazione strutturale e semantica delle proposte dell'agente
- Feedback loop per miglioramento iterativo
- Parsing JSON automatico delle risposte
- Gestione errori e retry logic
- Integrazione in **Ali**: Auditor valida desires prima del salvataggio
- Integrazione in **Believer**: Auditor valida beliefs estratti
- UI per visualizzazione feedback auditor

### 🤖 Miglioramenti Prompts

#### Ali System Prompt

- **Ristrutturazione completa** del prompt per Ali
- Migliore guida per estrazione desires
- Istruzioni più chiare per formato JSON
- Supporto per domini e personas

#### Belief Base Extraction

- Creato prompt dedicato per estrazione beliefs
- Generazione automatica da knowledge base
- Formato JSON strutturato
- Validazione automatica

#### Suggerimenti Migliorati

- Sistema di suggerimenti contestuali più intelligente
- Suggerimenti basati su history conversazione
- Personalizzazione per dominio
