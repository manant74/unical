# 🚀 Quick Start - BDI Framework

Guida rapida per iniziare ad usare l'applicazione BDI Framework in pochi minuti.

## ⚡ Setup Veloce

### 1. Installa le dipendenze

```bash
pip install -r requirements.txt
```

### 2. Configura le API Keys

```bash
# Copia il file di esempio
cp .env.example .env

# Apri .env e inserisci almeno una API key:
# - GOOGLE_API_KEY=your_key_here
# - ANTHROPIC_API_KEY=your_key_here
# - OPENAI_API_KEY=your_key_here
```

### 3. (Opzionale) Testa l'installazione

```bash
python test_setup.py
```

### 4. Avvia l'applicazione

```bash
streamlit run app.py
```

L'app si aprirà automaticamente su `http://localhost:8501`

---

## 📋 Workflow Base

### Passo 1: Carica Documenti (Contextual)

1. Clicca sulla tile **Contextual** 📚
2. Carica i tuoi documenti:
   - **PDF**: Documenti tecnici, manuali
   - **Web**: URL di pagine web
   - **TXT/MD**: File di testo o Markdown
3. Aspetta che vengano processati
4. (Opzionale) Testa la ricerca nella knowledge base

### Passo 2: Definisci i Desire (Alì)

1. Clicca sulla tile **Alì** 🎯
2. Scegli il provider LLM dalla sidebar (Gemini/Claude/OpenAI)
3. Inizia la conversazione con l'agente
4. Alì ti aiuterà a identificare i tuoi **Desire** (obiettivi)
5. Puoi anche aggiungere Desire manualmente
6. Quando hai finito, clicca **"Completa Sessione"**

### Passo 3: Identifica i Belief (Believer)

1. Clicca sulla tile **Believer** 💡
2. L'agente caricherà automaticamente i tuoi Desire
3. Scegli il provider LLM dalla sidebar
4. Believer ti aiuterà a identificare i **Belief** (credenze/fatti)
5. I Belief saranno collegati ai Desire rilevanti
6. Clicca **"Completa Sessione"** per salvare tutto
7. Usa **"Esporta BDI"** per scaricare il JSON completo

---

## 🎯 Esempio Pratico

### Scenario: Sviluppo di una App Mobile

**1. Contextual - Carica Documenti:**

- Specifiche tecniche del progetto (PDF)
- Documentazione API (Web)
- Requisiti cliente (TXT)

**2. Alì - Definisci Desire:**

```
Utente: "Voglio creare un'app mobile per gestione task"

Alì: "Interessante! Puoi dirmi di più? Quali sono
le funzionalità principali che vuoi includere?"

Utente: "Login, lista task, notifiche push"

Alì: "Perfetto! Possiamo strutturare questo come:
- Desire #1: Implementare sistema di autenticazione sicuro
- Desire #2: Creare interfaccia per gestione task
- Desire #3: Integrare sistema di notifiche push
Confermi?"
```

**3. Believer - Identifica Belief:**

```
Believer: "Ho caricato i tuoi 3 Desire. Esploriamo
i belief che li supportano. Per il Desire #1
(autenticazione), quali tecnologie o vincoli hai?"

Utente: "Dobbiamo usare OAuth 2.0"

Believer: "Ottimo! Questo è un belief di tipo 'constraint':
- Belief #1: Il sistema deve usare OAuth 2.0
  Tipo: constraint
  Confidenza: high
  Correlato a: Desire #1
Dalla knowledge base vedo anche che..."
```

**4. Risultato Finale:**

```json
{
  "desires": [
    {
      "id": 1,
      "description": "Implementare sistema autenticazione sicuro",
      "priority": "high"
    }
  ],
  "beliefs": [
    {
      "id": 1,
      "description": "Il sistema deve usare OAuth 2.0",
      "type": "constraint",
      "confidence": "high",
      "related_desires": [1]
    }
  ]
}
```

---

## 💡 Tips & Tricks

### Migliori Pratiche

**Per Contextual:**

- ✅ Carica documenti rilevanti e aggiornati
- ✅ Usa nomi file descrittivi
- ✅ Testa la ricerca prima di procedere
- ❌ Non caricare documenti troppo grandi (>50MB)

**Per Alì (Desire):**

- ✅ Sii specifico nei tuoi obiettivi
- ✅ Usa il framework SMART (Specific, Measurable, Achievable, Relevant, Time-bound)
- ✅ Prioritizza i Desire (high/medium/low)
- ❌ Non creare troppi Desire alla volta (max 5-7)

**Per Believer (Belief):**

- ✅ Basa i Belief su evidenze dalla knowledge base
- ✅ Specifica il tipo corretto (fact/assumption/principle/constraint)
- ✅ Collega ogni Belief ai Desire rilevanti
- ✅ Indica il livello di confidenza onestamente

### Troubleshooting Comune

**Problema:** "L'agente non risponde"

- ✅ Verifica che l'API key sia configurata correttamente
- ✅ Controlla la connessione internet
- ✅ Prova a cambiare provider LLM

**Problema:** "La ricerca nella KB non trova nulla"

- ✅ Verifica che i documenti siano stati processati
- ✅ Prova query più semplici o generiche
- ✅ Ricarica i documenti se necessario

**Problema:** "Import errors"

- ✅ Esegui `pip install -r requirements.txt` di nuovo
- ✅ Verifica la versione di Python (3.9+)
- ✅ Esegui `python test_setup.py` per diagnosticare

---

## 🔧 Personalizzazione

### Modificare i System Prompts

I comportamenti degli agenti sono definiti in file Markdown:

```bash
prompts/
├── ali_system_prompt.md       # Modifica per cambiare Alì
├── believer_system_prompt.md  # Modifica per cambiare Believer
└── ...
```

Dopo aver modificato un prompt, riavvia l'app.

### Aggiungere Nuovi Provider LLM

Modifica `utils/llm_manager.py` per aggiungere nuovi modelli.

---

## 📚 Risorse Aggiuntive

- **README completo**: [README.md](README.md)
- **Nuove funzionalità**: [NewFeatures.md](NewFeatures.md)
- **Documentazione prompts**: [prompts/README.md](prompts/README.md)

---

## 🆘 Supporto

Se hai problemi:

1. Consulta la sezione Troubleshooting sopra
2. Esegui `python test_setup.py` per diagnosticare
3. Controlla i log di Streamlit nella console
4. Apri un issue su GitHub con dettagli e log

---

## 🎉 Prossimi Passi

Dopo aver completato il tuo primo framework BDI:

1. Esplora le visualizzazioni e analisi
2. Esporta i dati per altri usi
3. Consulta [NewFeatures.md](NewFeatures.md) per funzionalità avanzate
4. Personalizza i prompts per il tuo dominio specifico

**Buon lavoro con il BDI Framework! 🚀**
