# ✨ LUMIA Studio

**LUMIA Studio** è un'applicazione web basata su Streamlit per creare e gestire Belief, Desire e Intention secondo l'approccio BDI (Belief-Desire-Intention) applicato a un dominio di conoscenza specifico.

> **LUMIA** = **L**earning **U**nified **M**odel for **I**ntelligent **A**gents

## 🆕 Versione Corrente: v2.2.0

**Novità della v2.2** (2025-01-15):
- 🎯 **Sistema di Livelli di Rilevanza** per Believer con classificazione prioritaria (CRITICO/ALTO/MEDIO/BASSO)
- 📊 **Struttura JSON migliorata** per belief con prioritizzazione automatica
- 🔍 **Gap analysis** facilitata per identificare informazioni critiche mancanti
- 📚 **Documentazione completa** del nuovo sistema di priorità

> Vedi [CHANGELOG.md](CHANGELOG.md) per lo storico completo delle versioni e [docs/UPDATES_v2.2.md](docs/UPDATES_v2.2.md) per dettagli sulla v2.2

## Caratteristiche

### Funzionalità Implementate

#### 📚 Contextual

- Upload di documenti in formato PDF, pagine web, file di testo e Markdown
- Elaborazione e indicizzazione dei documenti con tecniche RAG (Retrieval Augmented Generation)
- Database vettoriale persistente con ChromaDB
- Gestione del contesto con possibilità di reset completo

#### 🎯 Alì - Agent for Desires

- Agente conversazionale specializzato nell'identificazione dei Desire
- Accesso alla base di conoscenza costruita in Contextual
- Supporto per multipli provider LLM: Gemini, Claude, OpenAI
- Sistema di completamento sessione con salvataggio JSON dei Desire
- Aggiunta manuale di Desire con metadati strutturati

#### 💡 Believer - Agent for Beliefs

- Agente per identificare e strutturare i Belief
- Integrazione RAG con contesto che include sia la KB che i Desire
- Supporto per multipli provider LLM
- Classificazione dei Belief per tipo (fact, assumption, principle, constraint)
- Correlazione tra Belief e Desire
- Esportazione completa del framework BDI in JSON

#### 🔮 Cuma e ⚡ Genius

- Pagine placeholder per funzionalità future
- Sistema di raccolta feedback utente

## Installazione

### Prerequisiti

- Python 3.9 o superiore
- pip

### Setup

1. Clona il repository:

```bash
git clone <repository-url>
cd unical
```

2. Crea un ambiente virtuale:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Installa le dipendenze:

```bash
pip install -r requirements.txt
```

4. Configura le API keys:

```bash
# Copia il file di esempio
cp .env.example .env

# Modifica .env con le tue API keys
# Configura almeno una delle seguenti:
# - GOOGLE_API_KEY (per Gemini)
# - ANTHROPIC_API_KEY (per Claude)
# - OPENAI_API_KEY (per OpenAI)
```

## Utilizzo

1. Avvia l'applicazione:

```bash
streamlit run app.py
```

2. L'applicazione si aprirà nel browser all'indirizzo `http://localhost:8501`

3. Workflow suggerito:
   - **Passo 1**: Vai a Contextual e carica i documenti per creare la base di conoscenza
   - **Passo 2**: Vai ad Alì per definire i Desire attraverso la conversazione con l'agente
   - **Passo 3**: Completa la sessione in Alì per salvare i Desire
   - **Passo 4**: Vai a Believer per identificare i Belief correlati ai Desire
   - **Passo 5**: Completa la sessione in Believer ed esporta il framework BDI completo

## Struttura del Progetto

```
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

## Tecnologie Utilizzate

- **Frontend/Backend**: Streamlit
- **Vector Database**: ChromaDB
- **Embeddings**: sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
- **LLM Integration**: Google Gemini, Anthropic Claude, OpenAI GPT
- **Document Processing**: PyPDF2, BeautifulSoup4
- **Text Splitting**: LangChain RecursiveCharacterTextSplitter

## Documentazione Aggiuntiva

### Release e Aggiornamenti
- **[CHANGELOG.md](CHANGELOG.md)** - Storico completo delle versioni
- **[RELEASE_NOTES_v2.2.md](RELEASE_NOTES_v2.2.md)** - Note di rilascio v2.2.0
- **[docs/UPDATES_v2.2.md](docs/UPDATES_v2.2.md)** - Documentazione dettagliata sistema livelli di rilevanza

### Guide Tecniche
- **[docs/AGENTS_GUIDE.md](docs/AGENTS_GUIDE.md)** - Guida agli agenti
- **[docs/PROMPT_ANALYSIS.md](docs/PROMPT_ANALYSIS.md)** - Analisi dei system prompts
- **[NewFeatures.md](NewFeatures.md)** - Proposte di nuove funzionalità

## Roadmap

### v2.3+ (In Pianificazione)
- [ ] Dashboard di Coverage per visualizzazione livelli di rilevanza
- [ ] Auto-recommendation per colmare gap critici
- [ ] Quality Score per completezza desires

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
