# Changelog

Tutte le modifiche significative a questo progetto saranno documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## Release - 2026-01-12

### ✨ Nuove Features

### 🤖 Miglioramenti Prompts

- Arricchito prompt del Believer con sezione dedicata ai livelli di rilevanza dei Beliefs
- in CUMA Specificato formato JSON finale con tracciamento relazioni:
  - `linked_desire_id`: Collegamento univoco tra Intention e Desire
  - `linked_beliefs`: Riferimento univoco ai Beliefs necessari per l'esecuzione

### 🎨 Interventi UX

- Miglioramento sezione Analytics in Compass
- Grafo delle relazioni BDI più interattivo

### 🔧 Bug Fix e Miglioramenti


## Release - 2025-12-15

### 🤖 Miglioramenti Prompts 0

- Alì: modifica del prompt per la generazione dei Desire allineato a nuovo standard Json:

```json
{
  "desire_id": "D1",
  "desire_statement": "Formulazione chiara del desiderio dal punto di vista del beneficiario.",
  "motivation": "Motivazione profonda (perché questo desire è importante).",
  "success_metrics": [
    "Indicatore di successo #1",
    "Indicatore di successo #2"
  ]
}
```

- Believer: modifica del prompt del Believer per generare Beliefs secondo nuovo standard Json. Aggiornamento di tutte le componenti applicative che facevano uso dei belief i json:

```json
{
  "subject": "Entità soggetto",
  "definition": "Descrizione breve: WHAT it is, WHY it matters, HOW it works",
  "semantic_relations": "tipo_di_relazione",
  "object": "Entità oggetto",
  "source": "Fonte testuale",
  "importance": 0.85,
  "confidence": 0.9,
  "prerequisites": ["Concetto prerequisito"],
  "related_concepts": ["Concetto correlato"],
  "enables": ["Concetto abilitato"],
  "part_of": ["Concetto padre"],
  "sub_concepts": ["Sottoconcetto"],
  "tags": ["tag1", "tag2"],
  "metadata": {"subject_type": "Tipo di entità", "object_type": "Tipo di entità"},
  "related_desires": [{"desire_id": "D1", "relevance_level": "CRITICO", "definition": "Spiegazione della correlazione"}]
}
```

- Rimozione logica dei chackpoint dai vari prompt

- Revisione del prompt di Alì per generare i desire individuando i maniera più chiara persone e beneficiari

### ✨ Features

#### **Cuma: l'agente che genera Intentions**

- Creata una prima versione di prompt per Cuma, l'agente che sualla base dei desire e dei belief definiti è in grado di generare diverse Intentions
Al momento l'implementazione non integra Oracolo o Auditor per poter guidare la generazione di Intentions
E' statio progettato un prompt ad hoc che va nella direzione di generare possibili piano per soddisfare i Desire

#### **Integrazione Modelli LLM**

- **OpenAI**:
  - Aggiunto supporto a **ChatGPT 5.1** per le modalità *Thinking* e *Instant*
  - Integrati nuovi modelli **ChatGPT 5.2** disponibili nelle modalità *Standard*, *Thinking* e *Instant*
  - Integrati nuovi modelli **Gemini 3 Pro** disponibili per ora in modalità preview via API

### ✨ UI/UX Improvements

- Gestone messaggi personalizzati nelle fasi in cui LLM pensa e sta elaborando
- Sempligicazione modulo Knol

### 🔧 Bug Fix e Miglioramenti 0

#### **Believer Module**

- Risolto problema su chat Believer che rimaneva bloccata

#### Miglioramenti Auditor

- Ottimizzazione logica di controllo e validazione
- Miglioramento finalizzazione JSON delle risposte
- Doppio passaggio di verifica per maggiore affidabilità

## Release - 2025-11-15

### 🎨 Home Page Redesign

- **Rebranding**: "LUMIA" → "LumIA" per evidenziare il riferimento all'Intelligenza Artificiale
- **Workflow ottimizzato**: Nuovo ordine Knol → Compass → Alì → Believer con descrizioni aggiornate
- **Riorganizzazione moduli** in 3 sezioni tematiche:
  - ⚙️ Configuration: Compass, Knol
  - 🎯 Domain Definition: Alì, Believer, Cuma
  - ⚡ Live Sessions: Genius
- **UI migliorata**:
  - Layout pulito con separatori orizzontali tra sezioni
  - Titoli sezioni allineati a sinistra con gradient viola

#### Knol Module

- **Editor Beliefs Modale**: Editor per beliefs di base con funzionalità complete

- **Revisione Layout Sidebar**:

#### Alì Agent

- Modificato il comportamento dell'Agente per indirizzare l'utente a definire una sola personas, con l'Auditor che agisce in retroazione sul Alì per garantire che l'agente guidi l'utente a definire la singola personas  

#### Believer Agent

- Inserita funzionalità per poter chiedere al Believer di generare, senza interazioni in  chat, i Beliefs derivandoli dai desire e individuando quali di quelli di base sono collegati ai Desire individuati

#### LLM Module

- Inserita logica per ipoter avere parametri di default per gli LLM, e per poter gestire parametri di configurazone diversi per ogni tipo di LLM

- Inserito parametro per GPT-5 per poter impostare il livello di reasoning

- Eliminato Anthropic tra gli LLM disponibili

### 📊 Compass - Analytics Dashboard (WIP)

- **Nuova tab Analytics**: Dashboard completo per analisi BDI in [Compass](pages/0_Compass.py)
  - **Statistiche aggregate**: Metriche su desires, beliefs, coverage e domains/personas
  - **Grafici interattivi** (Plotly):
  - **Grafo delle relazioni**: Visualizzazione interattiva rete Desire-Belief

#### UI Improvements 2

- Ottimizzazione Spazi

---

## Release - 2025-10-30

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

### 🤖 Miglioramenti Prompts old

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
