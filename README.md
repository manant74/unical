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

### Input (Contextual)

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

### 📚 Contextual - Knowledge Base Builder

Il **primo passo** nel workflow LUMIA. Contextual trasforma documenti non strutturati in una base di conoscenza interrogabile.

**Funzionalità:**

- **Multi-format support**: Carica PDF, pagine web (URL), file di testo (.txt) e Markdown (.md)
- **Chunking intelligente**: Divide automaticamente i documenti in chunk semanticamente significativi (1000 caratteri con overlap di 200)
- **Embeddings multilingua**: Utilizza `paraphrase-multilingual-MiniLM-L12-v2` per supportare testi in italiano e altre lingue
- **Database vettoriale persistente**: ChromaDB memorizza gli embeddings per ricerche semantiche veloci
- **Test della KB**: Interfaccia per interrogare la base di conoscenza e verificare la qualità dell'indicizzazione
- **Gestione contesto**: Possibilità di reset completo del database per iniziare nuove sessioni

**Tecnologia RAG**: Implementa Retrieval Augmented Generation, permettendo agli agenti di accedere a informazioni rilevanti contestualizzate durante le conversazioni.

### 🎯 Alì - Agent for Desires

**Alì** è un agente conversazionale esperto in product strategy, user research e design thinking. Il suo scopo è guidare l'utente nell'identificazione dei **Desires** (obiettivi strategici) attraverso l'analisi delle personas.

**Approccio metodologico:**

1. **Identificazione del dominio**: Esplora e definisce il contesto di lavoro
2. **Mappatura personas**: Identifica le categorie di utenti finali
3. **Analisi per persona**: Analizza ogni categoria separatamente con focus empatico
4. **Esplorazione desires**: Usa domande strategiche per far emergere bisogni profondi
5. **Checkpoint intermedi**: Validazione progressiva per evitare deriva del contesto
6. **Report finale JSON**: Genera un documento strutturato con tutte le personas e i loro desires

**Caratteristiche tecniche:**

- Supporto multi-LLM (Gemini, Claude, OpenAI) con selezione modello
- Accesso RAG alla knowledge base per contestualizzare i desires nel dominio
- Parsing automatico del report JSON finale per estrarre desires strutturati
- Possibilità di aggiunta manuale di desires con metadati (priorità, contesto, criteri di successo)
- Salvataggio sessioni con timestamp e storico conversazioni

**Output**: File JSON con struttura `personas → desires → metrics` salvato in `data/current_desires.json`

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

- Estrazione guidata dal "Principio di Rilevanza": solo fatti pertinenti ai desires
- Metadati arricchiti (tipo entità, fonte testuale esatta)
- Correlazione esplicita belief-desire con spiegazione
- Gap analysis facilitata per identificare informazioni mancanti
- Possibilità di aggiunta manuale di beliefs
- Export completo del framework BDI

**Output**: File JSON completo con desires + beliefs + chat history salvato in `data/current_bdi.json`

### ✅ Validator - BDI Framework Validator

Modulo di validazione e editing manuale del framework BDI generato dagli agenti.

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

#### Passo 1: 📚 Costruzione della Knowledge Base (Contextual)

1. Accedi al modulo **Contextual**
2. Carica i tuoi documenti di dominio:
   - **PDF**: Documenti tecnici, report, white paper
   - **Pagine Web**: Inserisci URL di documentazione online, articoli, siti
   - **File di Testo**: File .txt con informazioni sul dominio
   - **Markdown**: Documentazione strutturata in formato .md
3. Verifica l'indicizzazione usando la funzione "Test della Base di Conoscenza"
4. Assicurati che il contatore "Contenuti nel Database" mostri almeno alcuni documenti

**Consiglio**: Carica documenti che descrivono il tuo dominio, gli utenti, i processi esistenti, le problematiche, etc.

#### Passo 2: 🎯 Identificazione dei Desires (Alì)

1. Accedi al modulo **Alì**
2. Nella sidebar, seleziona il provider LLM e il modello preferito (es. Gemini 2.5 Pro)
3. Inizia la conversazione rispondendo alle domande di Alì:
   - Descrivi il tuo dominio
   - Identifica le personas (categorie di utenti)
   - Per ogni persona, esplora i loro desires (obiettivi, bisogni, frustrazioni)
4. Valida i checkpoint intermedi che Alì ti propone
5. Quando hai completato tutte le personas, chiedi esplicitamente: **"Genera il report finale"**
6. Verifica che i desires siano stati estratti automaticamente (vedrai un messaggio di successo)
7. Clicca **"✅ Completa Sessione"** nella sidebar per salvare

**Output**: File `data/current_desires.json` con la struttura completa personas-desires

#### Passo 3: 💡 Estrazione dei Beliefs (Believer)

1. Accedi al modulo **Believer**
2. Verifica che i desires siano stati caricati correttamente (vedrai un messaggio verde nella sidebar)
3. Nella sidebar, seleziona il provider LLM e il modello
4. Inizia la conversazione con Believer:
   - Rispondi alle domande di contesto
   - Believer interrogherà la knowledge base per estrarre beliefs pertinenti
   - Valida, correggi e integra i beliefs proposti
5. Quando hai completato l'analisi, chiedi: **"Genera il report finale"**
6. Clicca **"✅ Completa Sessione"** per salvare il framework BDI completo

**Output**: File `data/current_bdi.json` con desires + beliefs + correlazioni + livelli di rilevanza

#### Passo 4: ✅ Validazione e Refinement (Validator)

1. Accedi al modulo **Validator**
2. Rivedi il JSON generato nella tab "📝 Editor"
3. Usa la tab "👁️ Preview" per visualizzare il JSON formattato con numeri di riga
4. Modifica manualmente se necessario:
   - Correggi errori di estrazione
   - Affina le correlazioni belief-desire
   - Aggiusta i livelli di rilevanza
5. Clicca **"✔️ Valida JSON"** per verificare la sintassi
6. Clicca **"💾 Salva Modifiche"** per aggiornare il file

**Pronto per l'uso**: Il framework BDI è ora strutturato, validato e pronto per essere utilizzato in applicazioni downstream o per analisi strategiche.

### Funzionalità Avanzate

#### Aggiunta Manuale di Desires (Alì)

Espandi "➕ Aggiungi Desire Manualmente" e compila:

- Descrizione del desire
- Priorità (high/medium/low)
- Contesto specifico
- Criteri di successo

#### Aggiunta Manuale di Beliefs (Believer)

Espandi "➕ Aggiungi Belief Manualmente" e compila:

- Descrizione del belief
- Tipo (fact/assumption/principle/constraint)
- Livello di confidenza
- Desires correlati (multi-select)
- Evidenze/fonte

#### Reset e Nuove Sessioni

- **Reset Knowledge Base**: Contextual → Pulsante "🗑️ Cancella Contesto"
- **Nuova conversazione**: Sidebar di Alì/Believer → "🔄 Nuova Conversazione"
- **Storico sessioni**: Tutte le sessioni completate sono salvate in `data/sessions/` con timestamp

## Struttura del Progetto

```text
unical/
├── app.py                  # Pagina principale con tiles
├── pages/
│   ├── 1_Contextual.py    # Gestione documenti e KB
│   ├── 2_Ali.py           # Agente per Desire
│   ├── 3_Believer.py      # Agente per Belief
│   ├── 4_Cuma.py          # Placeholder
│   └── 5_Genius.py        # Placeholder
├── prompts/
│   ├── ali_system_prompt.md       # System prompt per Alì
│   ├── believer_system_prompt.md  # System prompt per Believer
│   ├── cuma_system_prompt.md      # System prompt per Cuma
│   └── genius_system_prompt.md    # System prompt per Genius
├── utils/
│   ├── __init__.py
│   ├── document_processor.py  # Elaborazione documenti e RAG
│   ├── llm_manager.py         # Gestione provider LLM
│   └── prompts.py             # Caricamento system prompts
├── data/
│   ├── chroma_db/         # Database vettoriale
│   ├── sessions/          # Sessioni salvate
│   ├── current_desires.json
│   └── current_bdi.json
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
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

- **User Research**: Identificazione sistematica di personas e loro bisogni
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

## Licenza

[Specificare la licenza]

## Contatti

[Specificare i contatti]
