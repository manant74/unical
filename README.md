# ✨ LUMIA Studio

**LUMIA Studio** è una piattaforma innovativa basata su intelligenza artificiale per la progettazione strategica centrata sull'utente. Attraverso agenti conversazionali specializzati, LUMIA Studio trasforma la conoscenza in azione strutturata seguendo il framework BDI (Belief-Desire-Intention).

> **LUMIA** = **L**earning **U**nified **M**odel for **I**ntelligent **A**gents

## 🎯 Cos'è LUMIA Studio?

LUMIA Studio è uno strumento di **knowledge engineering** e **strategic planning** che aiuta i responsabili di dominio a:

1. **Strutturare la conoscenza**: Trasforma documenti non strutturati (PDF, web, testo) in una base di conoscenza interrogabile tramite RAG (Retrieval Augmented Generation)
2. **Identificare obiettivi strategici (Desires)**: Attraverso conversazioni guidate con agenti AI, identifica e formalizza i bisogni e gli obiettivi degli utenti finali del tuo dominio
3. **Estrarre conoscenza rilevante (Beliefs)**: Analizza automaticamente la base di conoscenza per estrarre solo i fatti pertinenti agli obiettivi identificati, con classificazione prioritaria
4. **Validare e strutturare**: Permette la revisione e validazione del framework BDI generato in formato JSON strutturato

### Il Framework BDI

Il framework **Belief-Desire-Intention** è un modello per agenti intelligenti che separa:

- **Beliefs (Credenze)**: Fatti, principi e assunzioni sul dominio - "cosa so del mondo"
- **Desires (Desideri)**: Obiettivi e stati desiderati - "cosa voglio ottenere"
- **Intentions (Intenzioni)**: Piani d'azione per raggiungere i desires - "come lo ottengo"

LUMIA Studio si concentra sulle prime due fasi, costruendo una rappresentazione strutturata e semanticamente ricca del dominio attraverso l'interazione con agenti conversazionali.

## 🔍 Esempio Pratico

**Scenario**: Stai progettando un servizio di e-commerce per piante

### Input (Knol)

Carichi documentazione sul mercato delle piante, guide di giardinaggio, report di ricerca utenti, competitor analysis.

### Desires (Alì)

Attraverso conversazione guidata, emergono obiettivi come:

- **Persona "Principiante"**: "Sentirsi sicuro e guidato, sapendo di poter mantenere in vita la pianta acquistata"
- **Persona "Esperto"**: "Trovare e acquistare rapidamente varietà di piante rare con informazioni tecniche dettagliate"

### Beliefs (Believer)

L'AI estrae automaticamente dalla KB solo i fatti pertinenti:

- "Le piante d'appartamento richiedono cure specifiche basate su luce e umidità" → 🔴 CRITICO per desire "Principiante"
- "Il 70% dei principianti abbandona dopo la prima pianta morta" → 🔴 CRITICO per strategia prodotto
- "Gli esperti cercano informazioni su pH del terreno e cicli di crescita" → 🟡 ALTO per desire "Esperto"

### Output

Un file JSON strutturato che mappa desires degli utenti con fatti rilevanti della knowledge base, pronto per guidare decisioni di product design, feature prioritization e content strategy.

## 🎨 Moduli e Funzionalità

LUMIA Studio è organizzato in moduli specializzati, ciascuno con un agente AI dedicato o funzionalità specifiche:

### 🧭 Compass - Session Configuration & BDI Management

**Compass** è il modulo centrale per la gestione delle sessioni di lavoro e del framework BDI. Rappresenta il **punto di partenza** di ogni progetto LUMIA.

**Funzionalità principali:**

- **Gestione Sessioni**:
  - Creazione sessioni con nome, descrizione e tag
  - Selezione del contesto (knowledge base) da utilizzare
  - Configurazione provider LLM (Gemini, Claude, OpenAI) e modello
  - **Parametri LLM avanzati**: temperature, max_tokens, top_p
  - Test connessione LLM con sessione attiva
  - Gestione sessioni recenti (carica, elimina, switch)

- **Gestione BDI Data**:
  - **Tab Desires**: Visualizzazione e gestione desires della sessione
  - **Tab Beliefs**: Visualizzazione e gestione beliefs della sessione
  - Editor JSON con syntax highlighting per belief base
  - Import/export belief base dal contesto
  - Validazione JSON in tempo reale
  - Salvataggio persistente in sessione

- **Context & Beliefs Base**:
  - Opzione "Nessuno" per progetti senza contesto specifico
  - Import automatico beliefs da contesto selezionato
  - Editor espandibile/collassabile per grandi JSON
  - Gestione belief_base e beliefs (compatibilità retroattiva)

**Architettura**:

- Persistenza in `./data/sessions/{session_id}/`
- SessionManager utility per CRUD completo
- Isolamento completo tra sessioni diverse
- Auto-recovery sessione attiva in Alì e Believer

**Output**: Sessione configurata e attiva per l'intero workflow LUMIA

### 📚 Knol - Knowledge Base Builder

**Knol** è il modulo di gestione della knowledge base. Trasforma documenti non strutturati in contesti interrogabili e genera belief base.

**Funzionalità:**

- **Gestione Contesti**:
  - Creazione e selezione contesti multipli
  - Context Manager per isolamento knowledge base
  - Statistiche per contesto (documenti, beliefs, data)
  - Switch rapido tra contesti diversi

- **Upload Documenti**:
  - **Multi-format support**: PDF, URL (web scraping), file di testo (.txt), Markdown (.md)
  - **Chunking intelligente**: RecursiveCharacterTextSplitter (1000 caratteri, overlap 200)
  - **Embeddings multilingua**: `paraphrase-multilingual-MiniLM-L12-v2`
  - **Database vettoriale**: ChromaDB persistente per contesto

- **Estrazione Belief Base**:
  - Pulsante "🧠 Estrai Belief" per generazione automatica belief base
  - **Generazione descrizione contesto**: Se mancante, genera automaticamente descrizione (20 parole) analizzando i documenti
  - Salvataggio in `belief_base.json` nel contesto
  - Update automatico metadata contesto

- **Test KB**: Interfaccia query per verificare qualità indicizzazione
- **Gestione**: Reset KB, eliminazione contesto, export/import

**Tecnologia RAG**: Implementa Retrieval Augmented Generation per accesso contestuale agli agenti.

### 🎯 Alì - Agent for Desires

**Alì** è un agente conversazionale esperto in product strategy, user research e design thinking. Il suo scopo è guidare l'utente nell'identificazione dei **Desires** (obiettivi strategici) dell'unica persona primaria dedotta automaticamente durante la conversazione, senza chiedere di elencare personas.

**Approccio metodologico:**

1. **Identificazione del dominio**: Esplora e definisce il contesto di lavoro
2. **Segnali sull'utente reale**: Raccoglie esempi, comportamenti e motivazioni per poter inferire la categoria corretta senza domande esplicite
3. **Formalizzazione della persona primaria**: Formula un'etichetta descrittiva dedotta dal dialogo e la mantiene allineata lungo tutta la sessione
4. **Esplorazione desires**: Usa domande strategiche per far emergere bisogni profondi della persona dedotta
5. **Checkpoint intermedi**: Validazione progressiva del dominio, della persona e dei desire per evitare deriva del contesto
6. **Report finale JSON**: Genera un documento strutturato con la sola persona dedotta e tutti i suoi desires

**Caratteristiche tecniche:**

- **Sessione obbligatoria**: Richiede sessione attiva configurata in Compass
- **Auto-recovery**: Carica automaticamente ultima sessione attiva se session state vuoto
- Supporto multi-LLM con **parametri configurabili dalla sessione** (temperature, max_tokens, top_p)
- Accesso RAG alla knowledge base del contesto selezionato
- **Saluto contestualizzato**: Legge descrizione del contesto dal metadata (generata da Knol)
- Parsing automatico report JSON per estrazione desires strutturati
- **Salvataggio automatico**: Desires salvati in BDI data della sessione in tempo reale
- **Aggiunta manuale desires**: Form sidebar con metadati completi
- **UI ottimizzata**: Chat pulita, session badge, link rapido a Compass

**Output**: Desires salvati automaticamente in `session BDI data` + visualizzabili in Compass

### 💡 Believer - Agent for Beliefs

**Believer** è un sistema di knowledge engineering specializzato nell'estrazione di conoscenza strutturata. Analizza la knowledge base per identificare solo i **Beliefs** (fatti) pertinenti ai Desires precedentemente definiti.

**Processo di estrazione:**

1. **Caricamento desires**: Legge automaticamente i desires da Alì (supporta entrambi i formati JSON)
2. **Esplorazione interattiva**: Chiede all'utente informazioni aggiuntive per contestualizzare l'estrazione
3. **Query RAG contestuale**: Interroga la KB con contesto che include sia documenti che desires
4. **Estrazione strutturata**: Identifica fatti atomici in formato soggetto-relazione-oggetto
5. **Classificazione prioritaria**: Assegna livelli di rilevanza (CRITICO/ALTO/MEDIO/BASSO) per ogni belief rispetto ai desires correlati
6. **Validazione utente**: Interagisce per feedback e raffinamento
7. **Report finale**: Genera JSON completo con beliefs correlati ai desires

**Livelli di rilevanza (v2.2):**

- 🔴 **CRITICO**: Risponde direttamente al desire, dati quantitativi o vincoli assoluti
- 🟡 **ALTO**: Supporta significativamente il desire, informazioni essenziali
- 🟢 **MEDIO**: Fornisce contesto utile, background information
- 🔵 **BASSO**: Marginalmente rilevante, connessione indiretta

**Caratteristiche tecniche:**

- **Sessione obbligatoria**: Richiede sessione attiva con desires disponibili
- **Auto-recovery**: Carica automaticamente ultima sessione attiva
- **Caricamento automatico desires**: Legge desires dalla sessione BDI data
- Supporto multi-LLM con **parametri configurabili dalla sessione**
- Estrazione guidata dal "Principio di Rilevanza": solo fatti pertinenti
- Metadati arricchiti (tipo entità, fonte, correlazione desire)
- **Salvataggio automatico**: Beliefs salvati in BDI data in tempo reale
- **Aggiunta manuale beliefs**: Form sidebar con multi-select desires correlati
- **UI ottimizzata**: Session badge, desires disponibili visualizzati, link Compass

**Output**: Beliefs salvati automaticamente in `session BDI data` + visualizzabili in Compass

**Funzionalità:**

- **Editor JSON**: Text area con font monospazio per modifiche dirette
- **Preview con line numbers**: Visualizzazione formattata del JSON per navigazione facile
- **Validazione**: Controllo sintattico JSON prima del salvataggio
- **Salvataggio sicuro**: Aggiornamento del file `current_bdi.json` solo dopo validazione

**Uso**: Permette correzioni manuali, aggiustamenti e pulizia del JSON prima di procedere con moduli downstream (Cuma, Genius).

### 🔮 Cuma - Scenario Planning Agent (In Sviluppo)

**Futuro modulo** per analisi predittiva e scenario planning basato sul framework BDI costruito.

**Obiettivi pianificati:**

- Simulazione di scenari futuri basati su beliefs e desires
- Identificazione di rischi e opportunità
- Supporto decisionale strategico

### ⚡ Genius - BDI Optimization Agent (In Sviluppo)

**Futuro modulo** per ottimizzazione intelligente del framework BDI.

**Obiettivi pianificati:**

- Analisi di completezza e coerenza del framework
- Suggerimenti per colmare gap informativi
- Raccomandazioni strategiche basate sull'analisi BDI

## Installazione

### Prerequisiti

- Python 3.9 o superiore
- pip

### Setup

#### Clona il repository

```bash
git clone <repository-url>
cd unical
```

#### Crea un ambiente virtuale

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### Installa le dipendenze

```bash
pip install -r requirements.txt
```

#### Configura le API keys

```bash
# Copia il file di esempio
cp .env.example .env

# Modifica .env con le tue API keys
# Configura almeno una delle seguenti:
# - GOOGLE_API_KEY (per Gemini)
# - ANTHROPIC_API_KEY (per Claude)
# - OPENAI_API_KEY (per OpenAI)
```

## 🚀 Guida Rapida all'Utilizzo

### Avvio dell'Applicazione

#### Avvia l'applicazione

```bash
streamlit run app.py
```

#### L'applicazione si aprirà nel browser all'indirizzo `http://localhost:8501`

### Workflow Completo

LUMIA Studio segue un workflow sequenziale ben definito:

#### Passo 0: 🧭 Configurazione Sessione (Compass)

> **NUOVO** - Punto di partenza obbligatorio

1. Accedi al modulo **Compass**
2. **Crea una nuova sessione**:
   - Nome descrittivo (es: "Analisi E-commerce Piante")
   - Descrizione opzionale
   - Tag per organizzazione
3. **Configura la sessione**:
   - Seleziona il **contesto** (knowledge base) da utilizzare (o "Nessuno" se nuovo progetto)
   - Scegli **Provider LLM** (Gemini, Claude, OpenAI)
   - Scegli **Modello** (es: gemini-2.5-pro, claude-4-sonnet, gpt-4o)
   - **Configura parametri LLM** (opzionale):
     - Temperature (0.0-1.0, default 0.7) - Controllo creatività
     - Max Tokens (100-8000, default 2000) - Lunghezza risposte
     - Top P (0.0-1.0, default 0.9) - Nucleus sampling
     - Stop Sequences (max 4, opzionale) - Sequenze di interruzione
4. **Test connessione** LLM (opzionale ma consigliato)
5. **Attiva sessione** - Rende la sessione disponibile per Alì e Believer

**Output**: Sessione attiva pronta per l'intero workflow

#### Passo 1: 📚 Costruzione della Knowledge Base (Knol)

1. Accedi al modulo **Knol**
2. **Seleziona o crea un contesto** (se non l'hai già fatto in Compass)
3. **Carica documenti** nel contesto:
   - **PDF**: Documenti tecnici, report, white paper
   - **Pagine Web**: URL di documentazione online, articoli, siti
   - **File di Testo**: File .txt con informazioni sul dominio
   - **Markdown**: Documentazione strutturata in formato .md
4. **Estrai Belief Base** (pulsante "🧠 Estrai Belief"):
   - Genera automaticamente belief base dal contesto
   - Se la descrizione contesto è vuota, la genera automaticamente (20 parole)
   - Salva in `belief_base.json` nel contesto
5. **Test della KB**: Verifica qualità indicizzazione con query test

**Output**: Contesto con documenti indicizzati, belief base generata, descrizione disponibile

#### Passo 2: 🎯 Identificazione dei Desires (Alì)

1. Accedi al modulo **Alì**
2. **Verifica sessione attiva** (badge in sidebar mostra la sessione corrente)
   - Se non c'è sessione, viene caricata automaticamente l'ultima attiva
   - Altrimenti vai in Compass ad attivarla
3. **Nota**: Provider/modello LLM sono quelli configurati nella sessione (ma puoi cambiarli temporaneamente)
4. **Conversazione con Alì**:
   - Alì ti saluta con descrizione del contesto (letta dal metadata)
   - Rispondi alle domande guidate
   - Fai emergere la persona primaria (Alì la deduce) e i suoi desires
5. Valida checkpoint intermedi
6. Chiedi: **"Genera il report finale"**
7. I desires vengono **salvati automaticamente** nella sessione BDI data
8. (Opzionale) Clicca **"✅ Completa Sessione"** per finalizzare

**Output**: Desires salvati automaticamente in `session BDI data`, visualizzabili in Compass

#### Passo 3: 💡 Estrazione dei Beliefs (Believer)

1. Accedi al modulo **Believer**
2. **Verifica sessione attiva** e **desires caricati** (mostrati in sidebar)
   - I desires vengono caricati automaticamente dalla sessione BDI data
   - Se non ci sono desires, vai prima su Alì
3. **Nota**: Provider/modello LLM dalla sessione (override temporaneo possibile)
4. **Conversazione con Believer**:
   - Believer mostra i desires disponibili
   - Interroga la KB per estrarre beliefs pertinenti ai desires
   - Valida, correggi e integra i beliefs proposti
5. Chiedi: **"Genera il report finale"**
6. I beliefs vengono **salvati automaticamente** nella sessione BDI data
7. (Opzionale) Clicca **"✅ Completa Sessione"** per finalizzare

**Output**: Beliefs salvati automaticamente in `session BDI data`, visualizzabili in Compass

#### Passo 4: 🧭 Gestione BDI nella Sessione (Compass)

1. Accedi al modulo **Compass**
2. Seleziona la tua sessione attiva
3. Usa le tab "💭 Desires" e "🧠 Beliefs" per gestire i dati BDI
4. Modifica, valida e salva i dati direttamente nella sessione:
   - Correggi errori di estrazione
   - Affina le correlazioni belief-desire
   - Aggiusta i livelli di rilevanza
5. Clicca **"✔️ Valida JSON"** per verificare la sintassi
6. Clicca **"💾 Salva Modifiche"** per aggiornare il file

**Pronto per l'uso**: Il framework BDI è ora strutturato, validato e pronto per essere utilizzato in applicazioni downstream o per analisi strategiche.

### Funzionalità Avanzate

#### Saluto Contestualizzato (Alì)

Al primo accesso ad Alì, l'agente:

- Legge automaticamente il file `current_context.json` generato da Knol
- Personalizza il messaggio di benvenuto includendo la descrizione del contesto
- Se il file non esiste, lo genera analizzando i titoli dei documenti nella KB usando l'LLM

Questo permette ad Alì di avere immediatamente il contesto del dominio su cui lavorare.

#### Aggiunta Manuale di Desires (Alì)

Nella sidebar di Alì, espandi "➕ Aggiungi Desire Manualmente" e compila:

- Descrizione del desire
- Priorità (high/medium/low)
- Contesto specifico
- Criteri di successo

#### Aggiunta Manuale di Beliefs (Believer)

Nella sidebar di Believer, espandi "➕ Aggiungi Belief Manualmente" e compila:

- Descrizione del belief
- Tipo (fact/assumption/principle/constraint)
- Livello di confidenza
- Desires correlati (multi-select)
- Evidenze/fonte

#### Reset e Nuove Sessioni

- **Reset Knowledge Base**: Knol → Pulsante "🗑️ Cancella Contesto"
- **Nuova conversazione**: Sidebar di Alì/Believer → "🔄 Nuova Conversazione"
- **Storico sessioni**: Tutte le sessioni completate sono salvate in `data/sessions/` con timestamp

## Struttura del Progetto

```text
unical/
├── app.py                     # Pagina principale con tiles
├── pages/
│   ├── 0_Compass.py          # ✨ NUOVO: Gestione sessioni e BDI
│   ├── 1_Knol.py             # Gestione contesti e KB
│   ├── 2_Ali.py              # Agente per Desires
│   ├── 3_Believer.py         # Agente per Beliefs
│   ├── 4_Cuma.py             # Placeholder
│   └── 5_Genius.py           # Placeholder
├── prompts/
│   ├── ali.md                # System prompt per Alì
│   ├── believer.md           # System prompt per Believer
│   ├── belief_base_prompt.md # Prompt per generazione belief base
│   ├── cuma.md               # System prompt per Cuma
│   └── genius.md             # System prompt per Genius
├── utils/
│   ├── __init__.py
│   ├── document_processor.py    # Elaborazione documenti e RAG
│   ├── llm_manager.py           # ✨ AGGIORNATO: Gestione LLM con parametri
│   ├── session_manager.py       # ✨ NUOVO: Gestione sessioni
│   ├── context_manager.py       # ✨ NUOVO: Gestione contesti multipli
│   └── prompts.py               # Caricamento system prompts
├── data/
│   ├── contexts/                # ✨ NUOVO: Contesti multipli
│   │   └── {context_name}/
│   │       ├── chroma_db/       # DB vettoriale per contesto
│   │       ├── context_metadata.json  # Metadata contesto
│   │       └── belief_base.json       # Belief base contesto
│   ├── sessions/                # ✨ AGGIORNATO: Sessioni complete
│   │   └── {session_id}/
│   │       ├── metadata.json    # Nome, descrizione, timestamp
│   │       ├── config.json      # Context, LLM provider/model/settings
│   │       ├── bdi_data.json    # Desires e beliefs della sessione
│   │       └── belief_base.json # Belief base (opzionale)
│   ├── current_context.json     # ⚠️ DEPRECATO: Sostituito da context metadata
│   └── current_bdi.json         # ⚠️ DEPRECATO: Sostituito da session BDI data
├── docs/                        # ✨ NUOVO: Documentazione tecnica
│   ├── COMPASS_GUIDE.md
│   ├── LLM_PARAMETERS_ANALYSIS.md
│   ├── SESSION_INTEGRATION_TODO.md
│   └── ...
├── test_*.py                    # ✨ NUOVO: Suite di test
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### Struttura del Framework BDI

Il sistema utilizza un framework BDI (Beliefs, Desires, Intentions) in formato single-persona: ogni sessione è legata a un'unica categoria utente dedotta da Alì.

```json
{
  "domain_summary": "Sintesi del dominio o progetto (1-2 frasi)",
  "persona": {
    "persona_name": "Nome della persona primaria",
    "persona_description": "Breve descrizione del ruolo/contesto",
    "persona_inference_notes": ["Segnale 1", "Segnale 2"]
  },
  "desires": [
    {
      "desire_id": "D1",
      "desire_statement": "Descrizione del desire",
      "priority": "medium",
      "success_metrics": ["Metrica 1", "Metrica 2"]
    }
  ],
  "beliefs": [
    {
      "soggetto": "Entità soggetto",
      "relazione": "Tipo di relazione",
      "oggetto": "Entità oggetto",
      "fonte": "Fonte testuale",
      "metadati": {"tipo_soggetto": "Tipo di entità", "tipo_oggetto": "Tipo di entità"},
      "desires_correlati": [{"desire_id": "D1", "livello_rilevanza": "CRITICO", "spiegazione": "Spiegazione della correlazione"}]
    }
  ],
  "intentions": []
}
```
### Personalizzazione dei System Prompts

I system prompts degli agenti sono memorizzati in file Markdown separati nella directory [prompts/](prompts/). Questo permette di:

- Modificare facilmente il comportamento degli agenti
- Versionare i prompts separatamente dal codice
- Testare diverse versioni dei prompts senza modificare il codice

Per modificare un prompt:

1. Apri il file corrispondente in `prompts/` (es. [prompts/ali_system_prompt.md](prompts/ali_system_prompt.md))
2. Modifica il contenuto
3. Riavvia l'applicazione (o usa `clear_cache()` da `utils.prompts` per ricaricare)

## 🆕 Nuove Funzionalità (v2.5 - Ottobre 2025)

### Sistema di Gestione Sessioni Enterprise

- **Compass Module**: Punto di controllo centrale per configurazione e gestione
- **Sessioni Multiple**: Crea e gestisci progetti diversi in parallelo
- **Isolamento Completo**: Ogni sessione ha propri desires, beliefs e configurazioni
- **Auto-Recovery**: Caricamento automatico ultima sessione attiva in Alì/Believer
- **BDI Management**: Visualizzazione e editing desires/beliefs direttamente in Compass

### Parametri LLM Avanzati

- **Temperature Control** (0.0-2.0): Regola creatività vs determinismo delle risposte
- **Max Tokens** (100-8000): Controlla lunghezza risposte
- **Top P Sampling** (0.0-1.0): Nucleus sampling per varietà output
- **Stop Sequences** (max 4): Sequenze custom per interrompere generazione
- **Configurazione Centralizzata**: Parametri configurati una volta in Compass, usati automaticamente da Alì/Believer
- **Cross-Provider**: Funziona con Gemini, Claude e OpenAI

### Gestione Contesti Multipli

- **Context Manager**: Organizza knowledge base in contesti separati
- **Generazione Automatica Descrizione**: Knol genera descrizione contesto (20 parole) se mancante
- **Belief Base per Contesto**: Ogni contesto ha propria belief base
- **Metadata Completi**: Tracking documenti, beliefs, timestamp per contesto

### Miglioramenti UX

- **Session Badge**: Visibilità sessione attiva in ogni pagina
- **Link Rapidi**: Navigazione veloce tra moduli correlati
- **Salvataggio Automatico**: Desires e beliefs salvati in tempo reale nella sessione
- **Fallback Intelligenti**: Gestione robusta campi mancanti (desires senza 'id')

Per dettagli completi sulle implementazioni, vedi [docs/SESSION_SUMMARY_2025-10-20.md](docs/SESSION_SUMMARY_2025-10-20.md)

## Provider LLM Supportati

### Google Gemini

- gemini-1.5-pro
- gemini-1.5-flash
- gemini-pro

### Anthropic Claude

- claude-3-5-sonnet-20241022
- claude-3-opus-20240229
- claude-3-haiku-20240307

### OpenAI

- gpt-4-turbo-preview
- gpt-4
- gpt-3.5-turbo

## Formati di Output

### Desire JSON Structure

```json
{
  "id": 1,
  "description": "Descrizione del desire",
  "priority": "high|medium|low",
  "context": "Contesto specifico",
  "success_criteria": "Criteri di successo",
  "timestamp": "2025-01-01T12:00:00"
}
```

### Belief JSON Structure (v2.2 - Con Livelli di Rilevanza)

```json
{
  "soggetto": "Entità principale del fatto",
  "relazione": "Verbo o proprietà che lega soggetto e oggetto",
  "oggetto": "Entità o valore collegato",
  "fonte": "Testo esatto da cui è estratta l'informazione",
  "metadati": {
    "tipo_soggetto": "Tipo dell'entità soggetto",
    "tipo_oggetto": "Tipo dell'entità oggetto"
  },
  "desires_correlati": [
    {
      "desire_id": "P1-D1",
      "livello_rilevanza": "CRITICO|ALTO|MEDIO|BASSO",
      "spiegazione": "Perché questo belief è rilevante per il desire"
    }
  ]
}
```

**Livelli di Rilevanza**:

- 🔴 **CRITICO**: Risponde direttamente al desire, dati quantitativi o vincoli assoluti
- 🟡 **ALTO**: Supporta significativamente il desire, informazioni essenziali
- 🟢 **MEDIO**: Fornisce contesto utile, background information
- 🔵 **BASSO**: Marginalmente rilevante, connessione indiretta

> Per dettagli completi sul sistema di priorità, vedi [docs/UPDATES_v2.2.md](docs/UPDATES_v2.2.md)

### BDI Complete JSON

```json
{
  "timestamp": "2025-01-01T12:00:00",
  "desires": [...],
  "beliefs": [...],
  "chat_history": [...]
}
```

## 💼 Casi d'Uso e Applicazioni

LUMIA Studio è versatile e applicabile a diversi scenari:

### Product Management e Design

- **User Research**: Identificazione sistematica della persona primaria e dei suoi bisogni dedotti dal dialogo
- **Product Strategy**: Definizione di obiettivi allineati agli utenti
- **Gap Analysis**: Identificazione di informazioni mancanti critiche per decisioni strategiche

### Knowledge Management

- **Documentation Mining**: Estrazione di conoscenza strutturata da documentazione non strutturata
- **Domain Modeling**: Creazione di modelli di dominio basati su fatti e relazioni
- **Ontology Building**: Costruzione di basi di conoscenza semantiche per sistemi esperti

### Business Analysis

- **Requirements Engineering**: Elicitazione e strutturazione di requisiti attraverso analisi dei desires
- **Stakeholder Analysis**: Mappatura di bisogni e obiettivi di diversi stakeholder
- **Decision Support**: Correlazione tra fatti e obiettivi per supporto decisionale informato

### Strategic Planning

- **Goal Setting**: Definizione di obiettivi strategici evidence-based
- **Priority Management**: Classificazione prioritaria di informazioni e iniziative
- **Scenario Analysis**: Base strutturata per analisi predittiva (con moduli futuri)

## 🎓 Vantaggi dell'Approccio BDI con AI

### Separazione delle Concerns

- **Modularità**: Beliefs, Desires e Intentions sono gestiti separatamente
- **Traceability**: Ogni belief è esplicitamente correlato ai desires rilevanti
- **Manutenibilità**: Facile aggiornamento di singole componenti senza impatto sul resto

### AI-Augmented Knowledge Engineering

- **Scalabilità**: Elaborazione rapida di grandi volumi di documentazione
- **Qualità**: Estrazione guidata da principi (rilevanza, atomicità, fattualità)
- **Human-in-the-Loop**: L'AI propone, l'umano valida e raffina

### Output Strutturato e Riusabile

- **JSON Standard**: Format interoperabile per integrazione con altri sistemi
- **Semantic Richness**: Metadati, correlazioni e livelli di rilevanza espliciti
- **API-Ready**: Pronto per essere consumato da applicazioni downstream

## 🛠️ Tecnologie Utilizzate

### Core Framework

- **Frontend/Backend**: Streamlit 1.x
- **Python**: 3.9+

### AI e Machine Learning

- **LLM Integration**: Google Gemini (2.5 Pro/Flash), Anthropic Claude (3.7/4.x Sonnet, 4 Opus), OpenAI (GPT-4o, GPT-5, o1)
- **Embeddings**: sentence-transformers (`paraphrase-multilingual-MiniLM-L12-v2`)
- **RAG Framework**: Custom implementation con ChromaDB

### Data Storage e Processing

- **Vector Database**: ChromaDB (persistent client)
- **Document Processing**: PyPDF2 (PDF), BeautifulSoup4 (web scraping), requests
- **Text Chunking**: LangChain RecursiveCharacterTextSplitter

### Configuration

- **Environment Management**: python-dotenv per gestione API keys
- **Data Format**: JSON per persistenza e interoperabilità

## Documentazione Aggiuntiva

### Guide Tecniche

- **[docs/AGENTS_GUIDE.md](docs/AGENTS_GUIDE.md)** - Guida agli agenti
- **[docs/PROMPT_ANALYSIS.md](docs/PROMPT_ANALYSIS.md)** - Analisi dei system prompts
- **[NewFeatures.md](NewFeatures.md)** - Proposte di nuove funzionalità

## Roadmap

### Funzionalità Future

- [ ] Implementazione funzionalità Cuma (scenario planning)
- [ ] Implementazione funzionalità Genius (ottimizzazione BDI)
- [ ] Sistema di gestione Intentions completo
- [ ] Export in formati multipli (CSV, XML, PDF)
- [ ] Dashboard analitica con grafici interattivi
- [ ] Sistema di versioning per sessioni multiple
- [ ] Integrazione con altri provider LLM

## Contribuire

Contributi, issue e feature request sono benvenuti!

