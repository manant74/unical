# Changelog

Tutte le modifiche rilevanti al progetto LUMIA Studio saranno documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Non Rilasciato] - 2025-01-20

### 🎉 Aggiunte

#### Nuove Pagine e Sistemi Core

- **`pages/0_Compass.py`**: Nuova pagina di gestione sessioni e configurazione
  - Crea, modifica e gestisci sessioni di lavoro
  - Configura provider LLM e modelli per sessione
  - Visualizza e modifica belief di base per contesti
  - Gestione stato sessione (attiva/archiviata)

- **`pages/1_Knol.py`**: Nuova pagina di gestione knowledge base (rinominata da Contextual)
  - Carica documenti (PDF, TXT, MD) in knowledge base specifiche per contesto
  - Estrai belief di base dai documenti usando LLM
  - Gestione documenti context-aware
  - Lista documenti e statistiche

- **`utils/session_manager.py`**: Sistema completo di gestione sessioni
  - Creazione sessioni con ID univoci
  - Storage dati BDI (Beliefs, Desires, Intentions)
  - Gestione metadata e configurazione sessione
  - Gestione belief base per sessione
  - Stato sessione attiva/archiviata

- **`utils/context_manager.py`**: Sistema di isolamento contesti
  - Crea e gestisci contesti multipli isolati
  - Storage ChromaDB specifico per contesto
  - File belief base per contesto
  - Metadata e descrizioni contesto

#### Miglioramenti Agente Believer

- **Integrazione Belief di Base** (`pages/3_Believer.py`)
  - Rilevamento automatico belief di base esistenti nella sessione
  - Scelta interattiva all'inizio conversazione: creare belief specializzati o verificare belief di base
  - Pulsanti visuali per scelta utente (🎯 Crea / 📋 Verifica)
  - Pulsante "Vai a Compass" condizionale in sidebar (compare solo quando utente sceglie di verificare)
  - Visualizzazione conteggio belief di base disponibili in sidebar

- **Accumulo Incrementale Belief** (`pages/3_Believer.py`)
  - Bug risolto: belief da risposte JSON multiple ora si accumulano invece di essere sovrascritti

#### Miglioramenti Agente Alì

- **Accumulo Incrementale Desire** (`pages/2_Ali.py`)
  - Bug risolto: desire da risposte JSON multiple ora si accumulano invece di essere sovrascritti

### 🔧 Modifiche

#### Miglioramenti Document Processor (`utils/document_processor.py`)

- **Architettura Context-Aware**
  - Aggiunto parametro `context_name` al costruttore
  - Path ChromaDB dinamico basato su contesto: `./data/contexts/{context_name}/chroma_db`
  - Naming collection con informazioni contesto
  - Arricchimento metadata con campo context

- **Nuovi Metodi**
  - `get_all_documents()`: Recupera tutti i documenti con metadata
  - `get_belief_base_path()`: Ottieni path al file belief base del contesto
  - `_normalize_collection_name()`: Assicura nomi compatibili ChromaDB

#### Aggiornamenti LLM Manager (`utils/llm_manager.py`)

- Selezione modelli migliorata per tutti i provider
- Gestione errori e validazione migliorata
- Supporto migliore per diverse configurazioni modelli

#### Integrazione Sessioni

- **Alì** (`pages/2_Ali.py`)
  - Inizializzazione document processor session-aware
  - Lazy initialization del document processor
  - Contesto caricato da sessione attiva
  - Desire salvati direttamente nei dati BDI sessione

- **Believer** (`pages/3_Believer.py`)
  - Inizializzazione document processor session-aware
  - Desire caricati da dati BDI sessione
  - Belief salvati nei dati BDI sessione
  - Supporto per struttura domains/personas nei dati BDI

#### Aggiornamenti Documentazione

- **`README.md`**: Riscrittura completa
  - Panoramica architettura aggiornata
  - Nuova documentazione workflow (Compass → Knol → Alì → Believer)
  - Documentazione gestione sessioni e contesti
  - Istruzioni setup aggiornate

### 🗑️ Rimozioni

#### Pagine Deprecate

- **`pages/1_Contextual.py`**: Sostituita da `pages/1_Knol.py`
  - Rimosso vecchio approccio single-context
  - Funzionalità migrata a pagina Knol context-aware

- **`pages/4_Validator.py`**: Rimossa pagina validator
  - Funzionalità da riprogettare in versioni future

### 🐛 Correzioni

#### Bug Critici Risolti

- **Sovrascrittura Belief/Desire** (Alta Priorità)
  - Risolto in Alì e Believer: risposte JSON multiple ora si accumulano correttamente
  - Aggiunto `extend()` invece di assegnazione per preservare dati precedenti
  - Calcolo ID corretto basato su ID massimo esistente

- **Gestione Session State**
  - Risolto caricamento sessione in Alì e Believer
  - Fallback corretto all'ultima sessione attiva
  - Inizializzazione corretta session state

### 🔄 Refactoring

#### Cambiamenti Architetturali

- **Da Single Context a Multi-Context**
  - Migrazione da `data/chroma_db/` centralizzato a `data/contexts/{context}/chroma_db/`
  - Belief base ora per-contesto invece che globali
  - Storage dati BDI specifico per sessione

- **Da File-Based a Session-Based**
  - Desire e belief ora memorizzati in dati BDI sessione
  - Cronologia chat memorizzata in metadata sessione
  - Configurazione per sessione invece che globale

### 📝 Note
