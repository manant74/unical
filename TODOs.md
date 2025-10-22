# LUMIA Studio - TODOs

**Legenda:**

- [ ] = Da fare
- [x] = Completato

## 🐛 Fix

### Belief non salvati nel JSON

- [X] **Verifica perché i nuovi belief generati non compaiono nel JSON**
  - **Problema**: Quando Believer genera nuovi belief durante la conversazione, questi non vengono salvati correttamente nel file `current_bdi.json`
  - **Impatto**: Perdita di dati tra sessioni, i belief generati non persistono
  - **Azioni**:
    - Investigare il flusso di salvataggio dei belief in `pages/3_Believer.py`
    - Verificare la logica di parsing della risposta LLM
    - Controllare se il metodo di salvataggio del JSON viene chiamato correttamente
  - **File coinvolti**: `pages/3_Believer.py`, `data/current_bdi.json`

### Pulsante Home - COMPLETATO

- [x] **Pulsante Home in Contextual (spostato nella sidebar)**
  - Spostato il pulsante "Torna alla Home" dalla colonna principale alla sidebar per coerenza con le altre pagine

## ✨ Features

### Traduzioni - COMPLETATO

- [x] **Traduzione homepage in inglese**
  - Tradotti tutti i testi della homepage `app.py` mantenendo i nomi tecnici (LUMIA, BDI, agenti)
  - Testi principali, workflow, descrizioni moduli, footer ora in inglese

### Visualizzazione Contesto - COMPLETATO

- [x] **Visualizzazione lista documenti nel contesto (da ChromaDB)**
  - Implementata lista persistente dei documenti caricati recuperata direttamente da ChromaDB
  - Mostra tipo di documento con icone, nome/URL, e source ID

### Sistema Multisessione

- [x] **Gestione multisessione - Base implementata** ✅
  - **Stato**: Sistema base funzionante tramite Compass
  - **Implementato**:
    - ✅ Generazione session_id univoco (UUID)
    - ✅ Directory `./data/sessions/{session_id}/` per ogni sessione
    - ✅ Gestione file JSON per sessione (metadata, config, beliefs, BDI)
    - ✅ Isolamento delle sessioni
    - ✅ Integrazione completa con DocumentProcessor (ChromaDB per sessione)
  - **File coinvolti**: `utils/session_manager.py`, `pages/0_Compass.py`

### Belief di Base

- [X] **Generazione Belief di base**
  - **Obiettivo**: Generare automaticamente un set di belief fondamentali dalla knowledge base
  - **Descrizione**: Prima di iniziare la conversazione con Believer, estrarre automaticamente i concetti chiave, fatti principali e principi dal contesto caricato
  - **Funzionalità**:
    - Analisi automatica dei documenti in ChromaDB
    - Estrazione di belief fondamentali (fatti, regole, principi)
    - Salvataggio in una struttura JSON base
    - Possibilità di revisione prima dell'uso
  - **File coinvolti**: `pages/3_Believer.py`, nuovo modulo `utils/belief_extractor.py` (da creare)

### Auditor

- [ ] **Prima implementazione dell'Auditor con funzioni di ascolto e monitoraggio degli LLM**
  - **Obiettivo**: Creare un sistema di monitoring e auditing delle interazioni con gli LLM
  - **Funzionalità principali**:
    - Log di tutte le chiamate LLM (prompt, risposta, timestamp, token usage)
    - Tracking delle conversazioni per agente (Alì, Believer)
    - Analisi della qualità delle risposte
  
### Integrazione Belief di Base

- [X] **Integrazione Belief di base all'inizio del Believer**
  - **Obiettivo**: Utilizzare i belief di base generati automaticamente come punto di partenza nella conversazione con Believer
  - **Dipendenze**: Richiede completamento task "Generazione Belief di base"
  - **Funzionalità**:
    - Caricamento automatico dei belief di base all'apertura di Believer
    - Possibilità di accettare, modificare o rigenerare i belief proposti
    - Integrazione nel prompt di sistema di Believer
    - Visualizzazione dei belief di base nella sidebar
  - **Benefici**: Riduce il tempo necessario per costruire il framework BDI, migliora la coerenza
  - **File coinvolti**: `pages/3_Believer.py`, `prompts/believer_prompt.md`

### Miglioramento Prompt Alì

- [ ] **Modifica prompt di Alì per migliorare la gestione della fluidità della conversazione**
  - **Obiettivo**: Rendere le conversazioni con Alì più naturali e fluide
  - **Problemi attuali da risolvere**:
    - Flusso Risposte a volte troppo rigido
    - Difficoltà nell'ascoltare l'utente
    - Difficoltà nel raggiungimento degli obbiettivi
    - Gestione delle domande di chiarimento
    - Gestione di opzioni chiuse per arrivare all'obiettivo più velocemente
    - Bottoni dinamici con risposte precompilate per aiutare l'utente a raggiungere obbiettivo velocemente 


## 🎨 UI/UX Improvements

### Sidebar Management - COMPLETATO

- [x] **Sidebar nascosta nella homepage**
  - Implementato CSS per nascondere completamente la sidebar su `app.py`
  - Migliora il focus sul contenuto principale e le card dei moduli

- [x] **Sidebar visibile ed espansa nelle altre pagine**
  - Aggiunto `initial_sidebar_state="expanded"` a tutte le pagine dei moduli
  - Mantiene le sidebar originali con configurazioni e navigazione
  - Esperienza utente coerente tra i vari moduli

---
