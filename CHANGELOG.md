# Changelog

Tutte le modifiche significative a questo progetto saranno documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## Release - 2026-02-05

### ✨ Nuove Features

#### **Agente Genius**

- Implementata la pagina completa di **Genius** (`pages/6_Genius.py`): agente di coaching esecutivo basato su BDI che trasforma i Desire in piani d'azione personalizzati
- Creati prompt dedicati:
  - `genius_discovery_prompt.md` — fase di discovery e raccolta profilo utente
  - `genius_plan_generation_prompt.md` — generazione della struttura del piano tramite LLM
  - `genius_step_tips_prompt.md` — generazione di Tips e Integrane Tools per ogni step
  - `genius_coach_template.md` — template di coaching durante l'esecuzione
- Creato `utils/genius_engine.py`: che orchestra le seguenti fasi:
  - Selezione Framework BDI
  - Customizzazione Desire per il singolo utente, con individuazione belief correlati
  - Raccolta informaiziono e fatti sull'utente
  - Generaizone Piano
  - Individuazione Tools a supporto del piano
  - Execution Coarching
- Persistenza dei piani generati in `data/genius_plans/` con supporto per piano attivo

#### **Believer: Generazione Belief da zero**

- Aggiunta modalità di generazione dei Belief direttamente dai documenti e dai Desire, senza passare dal Belief Base (riduce il rumore)
- Creato prompt dedicato `believer_from_scratch_prompt.md` per questa modalità

### 🎨 Interventi UX

- **Grafo BDI**: il grafo delle relazioni è ora una tab dedicata in Compass con dimensionamento dinamico dei nodi in base al numero di connessioni (peso nel grafo)
- Traduzione completa dell'interfaccia in inglese:
  - Compass e Knol (primo batch)
  - Ali, Believer, Cuma, Auditor e tutti i moduli utils (secondo batch)
  - Aggiornamento dei messaggi di loading in `ui_messages.py`

### 🔧 Bug Fix e Miglioramenti

- **Dismissione GPT-4o**: rimosso il modello GPT-4o e la relativa configurazione da `llm_manager.py` e `llm_manager_config.py`; aggiornata la documentazione in `Architecture.md` e `README.md`
