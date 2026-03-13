# LUMIA Studio: Una Piattaforma Multi-Agente per la Knowledge Engineering Strategica basata sul Modello Cognitivo BDI

*Documentazione Tecnico-Scientifica — Progetto di Ricerca Unical*

---

## Abstract

LUMIA Studio (*Learning Unified Model for Intelligent Agents*) è una piattaforma software per la knowledge engineering strategica che integra il modello cognitivo BDI (Belief-Desire-Intention) con tecniche di intelligenza artificiale generativa e retrieval aumentato (RAG). Il sistema è stato sviluppato nell'ambito di una collaborazione di ricerca con l'Università della Calabria (Unical) con l'obiettivo di affrontare un problema centrale nella gestione della conoscenza organizzativa: la trasformazione di documenti non strutturati in framework strategici strutturati e azionabili.

Il cuore del sistema è l'adozione del modello BDI — originariamente formalizzato nell'ambito dell'intelligenza artificiale per agenti autonomi — come struttura organizzativa della conoscenza. Attraverso una pipeline conversazionale multi-agente, LUMIA guida l'utente nell'elicitazione degli obiettivi strategici (*Desires*), nell'estrazione di conoscenza rilevante dalla base documentale (*Beliefs*) e nella pianificazione di azioni concrete (*Intentions*), producendo un framework BDI persistente e interrogabile.

L'architettura è composta da sei agenti specializzati, ciascuno dotato di un meta-agente di qualità (*Auditor*) che valuta le risposte su rubric multidimensionali, garantendo coerenza e rigore nella costruzione incrementale del framework. Il retrieval documentale è goal-oriented: i chunk recuperati dalla knowledge base sono sempre contestualizzati rispetto ai desires dell'utente, rendendo l'estrazione della conoscenza intrinsecamente finalistica anziché generica.

LUMIA Studio rappresenta un contributo originale nell'intersezione tra knowledge engineering, BDI cognitive modeling e LLM-based multi-agent systems, con potenziale applicativo in ambiti quali la consulenza strategica, la ricerca applicata e la formazione specialistica.

---

## 1. Team di Lavoro

Il progetto LUMIA Studio è stato sviluppato nell'ambito di una collaborazione di ricerca tra l'Università della Calabria (Unical) e partner tecnologici esterni. Di seguito i membri del team coinvolti nelle attività di ricerca, progettazione e sviluppo.

| Nome | Ruolo | Affiliazione |
|------|-------|--------------|
| **Prof. Francesco Scarcello** | Responsabile Scientifico  | Dipartimento DIMES, Unical |
| **Dott Davide xxxx** | Ricercatore | Dipartimento DIMES , Unical |
| **Ing. Antonio Mantuano** | AI Engineer | Partner Tecnologico |
| **Ing. Simone ** | AI Engineer | Partner Tecnologico |

---

## 2. Introduzione

### 2.1 Contesto e Motivazione

Nelle organizzazioni moderne, la conoscenza rilevante per il processo decisionale strategico è tipicamente dispersa in fonti eterogenee e non strutturate: documenti interni, report di ricerca, manuali tecnici, pagine web. Trasformare questa massa informativa in insight strutturati e azionabili richiede un effort cognitivo significativo, competenze specialistiche di knowledge management e strumenti adeguati. L'avvento dei Large Language Models (LLM) ha aperto nuove possibilità in questo dominio, rendendo accessibile l'elaborazione semantica di testi a scala, ma ha anche introdotto nuove sfide: la tendenza alla genericità delle risposte, la difficoltà nel mantenere coerenza su conversazioni lunghe e la necessità di ancorare le inferenze a fonti documentali verificabili.

LUMIA Studio nasce per affrontare queste sfide in modo sistematico, combinando la potenza generativa dei moderni LLM con un framework cognitivo formale — il modello BDI — che impone struttura, direzione e verificabilità al processo di estrazione della conoscenza.

### 2.2 Il Problema Affrontato

Il problema centrale che LUMIA si propone di risolvere è il seguente: dato un corpus documentale di dominio, come è possibile estrarre in modo sistematico e goal-oriented la conoscenza rilevante per gli obiettivi strategici di uno specifico beneficiario, e come organizzarla in un framework che ne faciliti la pianificazione e l'esecuzione?

Le soluzioni esistenti tendono a operare su uno solo degli aspetti del problema: i sistemi RAG classici recuperano informazioni ma non le organizzano strategicamente; i tool di mind-mapping strutturano la conoscenza ma non la estraggono automaticamente; i chatbot generativi conversano ma non producono output strutturati persistenti. LUMIA integra questi livelli in una pipeline coerente e guidata da un modello cognitivo.

### 2.3 Obiettivi del Sistema

Gli obiettivi primari di LUMIA Studio sono:

1. **Strutturare la conoscenza documentale** in una knowledge base interrogabile tramite retrieval semantico
2. **Elicitare obiettivi strategici** (*Desires*) attraverso conversazioni guidate e metodologicamente fondate
3. **Estrarre conoscenza rilevante** (*Beliefs*) in modo goal-oriented, correlando ogni fatto agli obiettivi identificati
4. **Pianificare azioni concrete** (*Intentions*) a partire dal framework BDI costruito
5. **Garantire la qualità** del processo attraverso un sistema di auditing automatico multidimensionale

### 2.4 Struttura del Documento

Il documento è organizzato come segue. La sezione 3 introduce i fondamenti teorici e posiziona LUMIA nel panorama della ricerca correlata. La sezione 4 descrive l'architettura del sistema. La sezione 5 illustra le pipeline e gli algoritmi chiave. La sezione 6 analizza gli aspetti di innovazione. La sezione 7 discute le tecnologie adottate e le motivazioni delle scelte. La sezione 8 presenta casi d'uso e validazione qualitativa. Le sezioni 9 e 10 trattano rispettivamente le limitazioni attuali e gli sviluppi futuri. La sezione 11 conclude il documento.

---

## 3. Fondamenti Teorici e Contesto di Ricerca

### 3.1 Il Modello BDI (Belief-Desire-Intention)

Il modello BDI è un framework computazionale per la modellazione di agenti razionali, originariamente proposto nell'ambito dell'intelligenza artificiale per sistemi multi-agente. Il modello scompone lo stato mentale di un agente in tre componenti distinte: le *Beliefs* (credenze), che rappresentano la conoscenza dell'agente sullo stato del mondo; i *Desires* (desideri), che rappresentano gli stati obiettivo che l'agente vuole raggiungere; le *Intentions* (intenzioni), che rappresentano i piani d'azione che l'agente si impegna a eseguire per raggiungere i propri obiettivi.

Originariamente concepito per la programmazione di agenti software autonomi in ambienti dinamici, il modello BDI ha dimostrato nel tempo una notevole versatilità come framework di modellazione cognitiva. La sua forza risiede nella separazione netta tra *cosa so* (Beliefs), *cosa voglio* (Desires) e *come agisco* (Intentions), una tripartizione che rispecchia fedelmente il processo decisionale umano in contesti strategici e organizzativi.

In LUMIA Studio, il modello BDI viene reinterpretato come struttura organizzativa per la knowledge engineering: non si tratta di programmare un agente autonomo, ma di guidare un esperto umano nell'articolazione della propria conoscenza di dominio secondo questa tripartizione. Il risultato è un *framework BDI* — un documento strutturato che cattura in modo formale e interrogabile la conoscenza strategica di un dominio rispetto a obiettivi specifici.

### 3.2 Retrieval Augmented Generation (RAG)

Il paradigma RAG combina la capacità generativa dei Large Language Models con il retrieval semantico su basi documentali esterne. Anziché affidarsi esclusivamente alla conoscenza parametrica del modello — soggetta ad allucinazioni e obsolescenza — il sistema recupera dinamicamente i chunk documentali più rilevanti per la query corrente e li fornisce come contesto al LLM al momento della generazione.

I componenti fondamentali di una pipeline RAG sono: un sistema di indicizzazione (chunking + embedding dei documenti), un meccanismo di retrieval (ricerca per similarità vettoriale) e un modello generativo che sintetizza la risposta a partire dal contesto recuperato. Nell'area della ricerca, RAG rappresenta oggi uno degli approcci più consolidati per costruire sistemi di question answering su corpora documentali specifici di dominio, superando i limiti dei modelli solo-generativi in termini di fedeltà alle fonti e aggiornabilità della conoscenza.

In LUMIA, la pipeline RAG viene estesa con un meccanismo di contestualizzazione goal-oriented: il retrieval non avviene in risposta a query generiche, ma è sempre guidato dagli obiettivi strategici (*Desires*) precedentemente elicitati, producendo un'estrazione della conoscenza intrinsecamente finalistica.

### 3.3 Sistemi Multi-Agente basati su LLM

La ricerca recente sui sistemi multi-agente basati su LLM esplora architetture in cui più modelli linguistici cooperano, ciascuno specializzato in un sottocompito, per risolvere problemi complessi che superano le capacità di un singolo agente generalista. Tra i pattern architetturali emergenti in questo campo, particolare rilevanza hanno assunto i sistemi con agenti di supervisione (*meta-agents* o *critic agents*), in cui un agente valuta e corregge l'output di un altro, incrementando la qualità e la coerenza del risultato finale.

LUMIA adotta e specializza questo pattern: ogni agente conversazionale del sistema è affiancato da un *Auditor* dedicato, un meta-agente che valuta la qualità delle risposte su dimensioni specifiche al dominio dell'agente supervisionato, introducendo un meccanismo di quality assurance automatico e multidimensionale integrato nel flusso conversazionale.

### 3.4 Posizionamento di LUMIA

LUMIA Studio si colloca all'intersezione di tre aree di ricerca attive — BDI cognitive modeling, RAG-based knowledge extraction e LLM multi-agent systems — con una caratteristica distintiva: l'uso del framework BDI non come meccanismo di controllo per agenti autonomi, ma come *schema organizzativo della conoscenza umana* mediato da agenti conversazionali. Questo posizionamento originale apre una direzione di ricerca che potremmo definire *BDI-guided knowledge engineering*, in cui la struttura cognitiva formale diventa il contratto tra il sistema AI e l'esperto umano.

---

## 4. Architettura del Sistema

### 4.1 Visione d'Insieme

LUMIA Studio adotta un'architettura a strati (*layered architecture*) che separa nettamente le responsabilità di presentazione, logica applicativa, gestione della conoscenza e persistenza. Il sistema è implementato come applicazione web multi-pagina basata su Streamlit, con ogni pagina corrispondente a un agente specializzato del sistema.

```
┌─────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                  │
│         pages/ — Agenti come pagine Streamlit        │
├─────────────────────────────────────────────────────┤
│                 BUSINESS LOGIC LAYER                 │
│        utils/ — Manager e pipeline applicative       │
├─────────────────────────────────────────────────────┤
│                  KNOWLEDGE LAYER                     │
│     ChromaDB (vettori) + JSON (BDI strutturato)      │
├─────────────────────────────────────────────────────┤
│                 PERSISTENCE LAYER                    │
│          data/ — Filesystem strutturato              │
└─────────────────────────────────────────────────────┘
```

Questa separazione garantisce che la logica applicativa nei moduli `utils/` sia completamente indipendente dal framework di presentazione, facilitando la manutenibilità del sistema e un potenziale porting verso interfacce diverse in futuro.

### 4.2 Componenti Principali

Il sistema è composto da sei agenti conversazionali, un layer di utility condivise e un sistema di persistenza strutturato.

**Agenti conversazionali:**

| Agente | Modulo | Responsabilità |
|--------|--------|----------------|
| **Compass** | `0_Compass.py` | Gestione sessioni, dashboard BDI, configurazione LLM |
| **Knol** | `1_Knol.py` | Costruzione knowledge base, indicizzazione documenti |
| **Alì** | `2_Ali.py` | Elicitazione Desires via conversazione Socratica |
| **Believer** | `3_Believer.py` | Estrazione Beliefs con correlazione ai Desires |
| **Cuma** | `4_Cuma.py` | Pianificazione Intentions *(Beta)* |
| **Genius** | `6_Genius.py` | Coach esecutivo su framework BDI esportato |

**Utility condivise:**

| Modulo | Responsabilità |
|--------|----------------|
| `llm_manager.py` | Interfaccia unificata multi-provider (Gemini, OpenAI) |
| `session_manager.py` | CRUD sessioni, gestione sessione attiva |
| `context_manager.py` | Lifecycle ChromaDB con inizializzazione lazy |
| `document_processor.py` | Pipeline RAG: ingestione, chunking, embedding |
| `auditor.py` | Meta-agente di quality assurance |
| `genius_engine.py` | Generazione e persistenza piani d'azione |
| `prompts.py` | Caricamento prompt con cache LRU |

### 4.3 Flusso Dati End-to-End

Il flusso operativo di una sessione LUMIA segue una sequenza pipeline in cui l'output di ogni fase alimenta la successiva:

```
[Documenti PDF/URL/testo]
         │
         ▼
    ┌─────────┐
    │  KNOL   │ — Chunking (1000 char, overlap 200)
    │         │ — Embedding (paraphrase-multilingual-MiniLM-L12-v2, 384 dim)
    │         │ — Indicizzazione ChromaDB
    └────┬────┘
         │ Knowledge Base
         ▼
    ┌─────────┐
    │   ALÌ   │ — Conversazione Socratica
    │         │ — Inferenza beneficiario
    │         │ — Elicitazione Desires strutturati
    └────┬────┘
         │ Desires → current_bdi.json
         ▼
    ┌──────────┐
    │ BELIEVER │ — RAG desire-correlated
    │          │ — Estrazione Beliefs con scoring
    │          │ — Correlazione Belief↔Desire
    └────┬─────┘
         │ Beliefs → current_bdi.json
         ▼
    ┌─────────┐
    │ COMPASS │ — Validazione e editing BDI
    │         │ — Export Framework BDI
    └────┬────┘
         │ BDI Framework
         ▼
    ┌─────────┐     ┌─────────┐
    │  CUMA   │     │ GENIUS  │
    │         │     │         │
    │Intentions     │Piano    │
    │planning │     │esecutivo│
    └─────────┘     └─────────┘
```

### 4.4 Modello dei Dati BDI

Il framework BDI prodotto da LUMIA è persistito come documento JSON con una struttura formalmente definita. Il documento cattura quattro componenti principali:

**Beneficiario** — Il soggetto per cui viene costruito il framework, inferito conversazionalmente dall'agente Alì senza elicitazione diretta, attraverso l'analisi dei segnali emergenti nel dialogo.

**Desires** — Obiettivi strategici strutturati, ciascuno con identificatore univoco (`D1`, `D2`, …), livello di priorità (`high/medium/low`), metriche di successo misurabili, contesto e motivazione profonda.

**Beliefs** — Fatti e principi estratti dalla knowledge base, ciascuno con definizione tripartita (COSA è, PERCHÉ conta, COME funziona), relazioni semantiche tipizzate verso altri concetti, fonte documentale citata, score di importanza e confidenza, e mappa di rilevanza verso ogni Desire (`CRITICO / ALTO / MEDIO / BASSO`).

**Intentions** — Piani d'azione strutturati, ciascuno collegato a Desires e Beliefs specifici, con passi operativi, stime di effort, dipendenze e coppie rischio/mitigazione.

Questa struttura costituisce il contratto formale tra gli agenti del sistema e rappresenta l'artefatto principale prodotto da una sessione LUMIA.

---

## 5. Pipeline e Algoritmi Chiave

### 5.1 RAG Pipeline Desire-Correlated

La pipeline di retrieval aumentato di LUMIA estende il paradigma RAG classico introducendo il concetto di *retrieval contestualizzato agli obiettivi*. Il processo si articola in due fasi distinte: indicizzazione e retrieval.

**Fase di indicizzazione (Knol):**

1. Il documento sorgente (PDF, URL, testo) viene acquisito e normalizzato in testo piano
2. Il testo viene segmentato tramite `RecursiveCharacterTextSplitter` con finestre di 1.000 caratteri e overlap di 200 caratteri. L'overlap garantisce che concetti a cavallo di due chunk non vadano perduti
3. Ogni chunk viene trasformato in un vettore denso a 384 dimensioni tramite il modello `paraphrase-multilingual-MiniLM-L12-v2` della libreria `sentence-transformers`. La scelta di un modello multilingue consente l'indicizzazione di documenti in lingue diverse senza preprocessing aggiuntivo
4. I vettori vengono persistiti in ChromaDB, con una collezione separata per ogni contesto di conoscenza

**Fase di retrieval (Believer):**

A differenza di un sistema RAG tradizionale in cui la query è formulata dall'utente, in LUMIA il retrieval è guidato dai Desires precedentemente elicitati. Per ogni ciclo di estrazione delle Beliefs, Believer formula query semantiche costruite a partire dagli obiettivi strategici attivi nella sessione. I chunk recuperati vengono forniti al LLM come contesto, insieme alla lista dei Desires, richiedendo esplicitamente che ogni Belief estratta venga correlata agli obiettivi rilevanti con un livello di rilevanza quantificato. Questo meccanismo trasforma il retrieval da operazione generica a operazione *finalistica*: la knowledge base non viene esplorata in modo neutro, ma attraverso la lente degli obiettivi del beneficiario.

### 5.2 Elicitazione Conversazionale dei Desires (Alì)

L'agente Alì implementa un approccio di elicitazione ispirato al metodo Socratico: anziché richiedere all'utente di compilare form strutturati o elencare esplicitamente obiettivi e beneficiari, Alì conduce una conversazione esplorativa in cui le informazioni rilevanti emergono naturalmente dal dialogo.

Il processo segue una sequenza in tre fasi:

1. **Esplorazione del dominio** — Alì avvia la conversazione con domande aperte sul contesto, sulle sfide percepite e sulle dinamiche del dominio, senza rivelare la struttura BDI sottostante. Questo approccio riduce il bias di ancoraggio che si produrrebbe se l'utente sapesse in anticipo quali categorie dovrà popolare

2. **Inferenza del beneficiario** — Attraverso l'analisi dei segnali emergenti nel dialogo (esempi portati, terminologia usata, prospettive adottate), Alì inferisce la categoria di beneficiario principale senza domande dirette. Questo meccanismo produce inferenze più naturali e meno artificiosamente costruite rispetto all'elicitazione esplicita

3. **Elicitazione strutturata dei Desires** — Una volta stabilito il contesto, Alì guida l'utente nell'articolazione degli obiettivi strategici, esplorando per ciascuno la motivazione profonda, le metriche di successo e il contesto operativo. Al termine, genera un report JSON strutturato con il framework parziale Desires + Beneficiario

### 5.3 Sistema di Quality Assurance Multi-Dimensionale (Auditor)

Il sistema di auditing rappresenta uno degli elementi architetturali più originali di LUMIA. Ogni agente conversazionale principale è affiancato da un meta-agente *Auditor* dedicato, implementato come chiamata LLM separata che valuta ogni risposta dell'agente supervisionato prima che questa venga mostrata all'utente.

Ogni Auditor applica una rubric di valutazione specifica per dominio, composta da 6 dimensioni scored su scala 0–5:

**Auditor per Alì (Desires):**

| Dimensione | Descrizione |
|------------|-------------|
| Coerenza della query | La risposta è coerente con la domanda posta? |
| Allineamento al modulo | La risposta è appropriata alla fase corrente del processo? |
| Preservazione del contesto | Il contesto conversazionale precedente è mantenuto? |
| Progressione del dialogo | La conversazione avanza verso l'obiettivo? |
| Focus sul beneficiario | L'attenzione è correttamente centrata sul beneficiario? |
| Gestione della finalizzazione | Il JSON viene prodotto correttamente quando richiesto? |

**Auditor per Believer (Beliefs):**

| Dimensione | Descrizione |
|------------|-------------|
| Coerenza della query | La risposta è coerente con la domanda? |
| Preservazione del contesto | Il contesto documentale è rispettato? |
| Specificità della Belief | La Belief è sufficientemente specifica e non generica? |
| Struttura della Belief | La struttura COSA/PERCHÉ/COME è rispettata? |
| Evidenza e fonte | La Belief è ancorata a una fonte documentale citata? |
| Gestione della finalizzazione | Il JSON viene prodotto correttamente? |

L'Auditor produce, per ogni risposta valutata, un insieme di *issues* identificati, *suggerimenti di miglioramento* e *quick replies* che l'utente può adottare per guidare la conversazione verso risposte di qualità superiore. Il sistema rileva inoltre il caso in cui un agente dichiari verbalmente di aver prodotto output strutturato senza averlo effettivamente generato in formato JSON — un pattern di errore comune nei sistemi LLM-based.

### 5.4 Generazione del Piano d'Azione (Genius Engine)

Il motore Genius implementa una pipeline di generazione del piano in quattro fasi sequenziali:

1. **Discovery** — Genius conduce una conversazione strutturata per raccogliere il contesto operativo dell'utente: ruolo, orizzonte temporale, situazione attuale, vincoli e risorse disponibili

2. **Belief filtering** — A partire dal framework BDI esportato, il motore filtra le Beliefs per rilevanza rispetto al Desire target, privilegiando quelle con livello `CRITICO` e `ALTO`. Questo filtro garantisce che il piano generato sia ancorato alla conoscenza di dominio più pertinente

3. **Plan generation** — Il LLM riceve il Desire target, il profilo dell'utente raccolto nella fase Discovery e le Beliefs filtrate, e genera un piano d'azione strutturato in fasi con passi operativi, stime di effort e dipendenze

4. **Step enrichment** — Opzionalmente, ogni passo del piano può essere arricchito con suggerimenti pratici, strumenti consigliati e riferimenti specifici, tramite una chiamata LLM dedicata per passo

Il piano generato viene persistito su filesystem e può essere esportato in formato Markdown. Il tracciamento del completamento dei passi avviene tramite flag persistiti che sopravvivono al riavvio dell'applicazione.

---

## 6. Aspetti di Innovazione

### 6.1 BDI come Framework Cognitivo per la Knowledge Engineering

Il contributo innovativo principale di LUMIA Studio risiede nella reinterpretazione del modello BDI come struttura organizzativa per la knowledge engineering strategica mediata da agenti conversazionali.

Il modello BDI è stato storicamente applicato alla progettazione di agenti software autonomi: il framework definisce come un agente *delibera* sulle proprie azioni in ambienti dinamici. LUMIA opera una trasposizione concettuale significativa: il modello non viene usato per programmare il comportamento di un agente autonomo, ma come *schema epistemico* che guida un esperto umano nell'articolazione della propria conoscenza di dominio. In questa prospettiva, il framework BDI diventa un contratto formale tra il sistema AI e l'utente, che definisce *quali* tipi di conoscenza estrarre, *come* organizzarla e *come* collegarla agli obiettivi strategici.

Questa trasposizione produce vantaggi concreti rispetto agli approcci tradizionali di knowledge management:

- **Direzione finalistica** — la conoscenza non viene estratta in modo enciclopedico, ma sempre in relazione a obiettivi espliciti, eliminando il rumore informativo non pertinente
- **Struttura verificabile** — il framework BDI prodotto è un artefatto formale interrogabile, modificabile e riutilizzabile, non una sintesi narrativa opaca
- **Separazione delle preoccupazioni** — la distinzione netta tra Beliefs (fatti del dominio), Desires (obiettivi) e Intentions (piani) rispecchia fasi cognitive distinte del processo decisionale, riducendo la contaminazione tra livelli

L'originalità di questo approccio sta nel fatto che, a differenza dei sistemi di knowledge graph o ontology engineering tradizionali — che richiedono competenze specialistiche per la modellazione formale — LUMIA rende accessibile la costruzione di un framework strutturato attraverso la conversazione in linguaggio naturale, abbassando significativamente la barriera di accesso alla knowledge engineering formale.

### 6.2 Architettura Multi-Agente con Meta-Auditor Dedicato

Il secondo contributo innovativo di LUMIA è l'architettura di quality assurance integrata nel flusso conversazionale tramite meta-agenti Auditor specializzati per dominio.

Nei sistemi LLM-based, la qualità delle risposte è intrinsecamente variabile: lo stesso modello può produrre output eccellenti e output incoerenti a seconda del contesto, della formulazione della query e dello stato della conversazione. Le soluzioni tradizionali a questo problema — prompt engineering più sofisticato, temperature più bassa, post-processing degli output — agiscono in modo statico e non adattivo.

LUMIA introduce un meccanismo di quality assurance *dinamico e contestuale*: ogni risposta di un agente conversazionale viene valutata in tempo reale da un meta-agente Auditor che applica una rubric multidimensionale specifica per il tipo di conoscenza che l'agente sta producendo. L'Auditor non si limita a rilevare errori sintattici o strutturali, ma valuta dimensioni semantiche di alto livello — la progressione del dialogo verso l'obiettivo, la specificità e l'ancoraggio documentale delle Beliefs, la correttezza della gestione degli output strutturati — producendo feedback azionabile che l'utente può utilizzare per guidare la conversazione.

Questo pattern — che potremmo denominare *conversational quality loop* — introduce una forma di meta-cognizione nel sistema: il sistema è in grado di valutare la qualità del proprio output e di segnalare proattivamente le aree di miglioramento, avvicinandosi al comportamento di un sistema auto-riflessivo.

### 6.3 Retrieval Goal-Oriented (Desire-Correlated RAG)

Il terzo contributo innovativo riguarda l'estensione della pipeline RAG con un meccanismo di contestualizzazione goal-oriented.

Nei sistemi RAG tradizionali, il retrieval è guidato dalla query dell'utente nel momento della richiesta: il sistema recupera i chunk più simili alla domanda posta e li fornisce come contesto al LLM. Questo approccio è efficace per il question answering generico, ma subottimale per la knowledge engineering strategica, dove l'obiettivo non è rispondere a una domanda specifica ma estrarre sistematicamente la conoscenza rilevante per un insieme di obiettivi predefiniti.

LUMIA estende il paradigma RAG introducendo i Desires come *filtro semantico persistente* sull'intera operazione di retrieval. Ogni query verso la knowledge base viene costruita tenendo conto degli obiettivi strategici attivi nella sessione, e ogni Belief estratta viene esplicitamente correlata ai Desires rilevanti con un livello di rilevanza quantificato. Il risultato è un sistema di retrieval che non esplora la knowledge base in modo neutro, ma la attraversa con una *intenzionalità* definita dagli obiettivi del beneficiario.

Questo approccio produce due vantaggi misurabili: riduce il volume di conoscenza estratta eliminando i fatti non pertinenti agli obiettivi, e aumenta l'utilizzabilità del framework BDI prodotto perché ogni Belief è già pre-correlata agli obiettivi a cui contribuisce, eliminando la fase manuale di mappatura che caratterizza i processi di knowledge management tradizionali.

---

## 7. Tecnologie e Motivazione delle Scelte

### 7.1 Stack Tecnologico

| Layer | Tecnologia | Versione |
|-------|------------|----------|
| Framework applicativo | Streamlit | 1.x |
| LLM — Provider 1 | Google Gemini (2.5 Pro/Flash/Flash-Lite) | API |
| LLM — Provider 2 | OpenAI GPT-5 series | API |
| Embeddings | `sentence-transformers` — `paraphrase-multilingual-MiniLM-L12-v2` | 384-dim |
| Vector database | ChromaDB | persistent client |
| Document processing | PyPDF2, BeautifulSoup4 | — |
| Text splitting | LangChain `RecursiveCharacterTextSplitter` | — |
| Visualizzazione grafi | PyVis, Plotly | — |
| Persistenza | JSON su filesystem | — |
| Configurazione | python-dotenv | — |

### 7.2 Motivazione delle Scelte

**Streamlit** è stato scelto come framework applicativo per la sua capacità di costruire applicazioni web interattive in Python puro, senza richiedere competenze frontend separate. In un contesto di ricerca universitaria, questa scelta abbassa significativamente il costo di sviluppo e manutenzione, permettendo al team di concentrarsi sulla logica applicativa e sugli algoritmi piuttosto che sull'infrastruttura web. Il trade-off principale è la scalabilità limitata a singolo utente e l'assenza di controllo granulare sull'interfaccia — limitazioni accettabili per un prototipo di ricerca.

**ChromaDB** è stato scelto come vector store per la sua semplicità di deployment (nessun server esterno, client persistente embedded), la compatibilità nativa con `sentence-transformers` e la maturità per use case di ricerca. Rispetto ad alternative come Pinecone (SaaS, dipendenza esterna) o Weaviate (overhead operativo elevato), ChromaDB offre il miglior rapporto tra funzionalità e semplicità per un sistema single-user. Il limite principale è la scalabilità: ChromaDB non è adatto a corpus di milioni di documenti o a deployment multi-utente concorrente.

**`paraphrase-multilingual-MiniLM-L12-v2`** è stato scelto come modello di embedding per tre ragioni: supporto multilingue nativo (critico per documenti italiani e inglesi), dimensionalità contenuta (384 dim, bilanciamento tra qualità e performance), e disponibilità locale senza dipendenze API esterne. Il modello viene scaricato una volta sola durante il setup e opera interamente on-device, eliminando latenza di rete e costi API per la fase di indicizzazione.

**Dual LLM provider (Gemini + OpenAI)** — La scelta di supportare due provider LLM anziché uno solo risponde a una esigenza di flessibilità e resilienza della ricerca: diversi modelli mostrano capacità differenti su task specifici (elicitazione conversazionale vs. estrazione strutturata), e la possibilità di confrontare i risultati su provider diversi ha valore scientifico per la valutazione del sistema. L'interfaccia unificata `LLMManager.chat()` isola il resto del sistema dalle differenze API tra provider, rendendo l'aggiunta di nuovi provider un intervento localizzato.

**JSON su filesystem** per la persistenza è una scelta deliberatamente semplice, motivata dalla natura single-user del sistema attuale e dalla priorità data alla leggibilità e ispezionabilità dei dati durante la fase di ricerca. Un file `current_bdi.json` può essere aperto, letto e modificato manualmente da un ricercatore senza strumenti specializzati — caratteristica preziosa in fase di sviluppo e validazione. Il passaggio a un database relazionale o document store è identificato come sviluppo futuro prioritario.

**LangChain `RecursiveCharacterTextSplitter`** è stato preferito a strategie di chunking più semplici (split per paragrafo, split per frase) per la sua capacità di rispettare gerarchie strutturali del testo (paragrafi → frasi → parole) durante la segmentazione, producendo chunk semanticamente più coerenti rispetto a un semplice split per lunghezza.

---

## 8. Casi d'Uso e Validazione Qualitativa

### 8.1 Scenari Applicativi

LUMIA Studio è stato progettato con vocazione generalista rispetto al dominio di conoscenza, ma con una particolare adeguatezza per scenari caratterizzati da: corpus documentale di dominio disponibile, necessità di estrarre conoscenza strategica orientata a obiettivi specifici, e presenza di un esperto umano come interlocutore del sistema.

I principali scenari applicativi identificati sono:

**Consulenza strategica e organizzativa** — Un consulente o manager carica i documenti di contesto di un'organizzazione (report, strategie, analisi di mercato) e utilizza LUMIA per costruire un framework BDI che struttura la conoscenza rilevante rispetto agli obiettivi strategici del cliente. Il piano d'azione generato da Genius costituisce il punto di partenza per la pianificazione operativa.

**Ricerca applicata e knowledge management accademico** — Un ricercatore carica un corpus di paper, report tecnici e documenti di progetto e utilizza LUMIA per estrarre sistematicamente le conoscenze rilevanti per gli obiettivi della propria ricerca, costruendo una mappa strutturata dello stato dell'arte rispetto alle proprie domande di ricerca.

**Formazione specialistica** — Un formatore carica il materiale didattico di un corso e utilizza LUMIA per costruire un framework BDI che mappa le conoscenze chiave rispetto agli obiettivi di apprendimento degli studenti, producendo un piano di studio personalizzato tramite Genius.

**Analisi di dominio per sviluppo software** — Un team di sviluppo carica la documentazione di dominio di un cliente e utilizza LUMIA per estrarre i requisiti impliciti (Desires), i vincoli e i presupposti del dominio (Beliefs) e le priorità di implementazione (Intentions), prima di avviare la fase di progettazione.

### 8.2 Walkthrough di una Sessione Completa

Di seguito viene descritta una sessione LUMIA rappresentativa, relativa a uno scenario di consulenza strategica nel dominio della trasformazione digitale di una PMI.

**Step 1 — Configurazione (Compass)**
L'utente crea una nuova sessione denominata "Trasformazione Digitale PMI", seleziona il provider LLM (Gemini 2.5 Flash), configura i parametri del modello e collega il contesto di conoscenza precedentemente creato.

**Step 2 — Costruzione della Knowledge Base (Knol)**
L'utente carica 12 documenti: 3 report di settore in PDF, 5 articoli accademici e 4 URL di risorse web. Knol processa i documenti, produce 847 chunk indicizzati in ChromaDB e genera automaticamente la belief base di contesto tramite LLM. L'utente verifica la qualità dell'indicizzazione tramite la funzione "Test KB" con alcune query campione.

**Step 3 — Elicitazione dei Desires (Alì)**
Alì avvia la conversazione con un benvenuto contestualizzato alla descrizione del contesto caricato. Nel corso di 8 scambi conversazionali, emergono 4 Desires strutturati: digitalizzazione dei processi interni, formazione del personale sugli strumenti digitali, integrazione con sistemi ERP esistenti, e misurazione del ROI della trasformazione. Per ciascuno vengono identificate motivazione profonda e metriche di successo. L'Auditor segnala in un caso una risposta con bassa progressione del dialogo, suggerendo una domanda di approfondimento più specifica.

**Step 4 — Estrazione delle Beliefs (Believer)**
In modalità interattiva, Believer conduce 6 cicli di retrieval desire-correlated, estraendo 23 Beliefs strutturate dalla knowledge base. Ogni Belief include definizione tripartita, fonte documentale e mappa di rilevanza verso i 4 Desires. 7 Beliefs ricevono classificazione CRITICO su almeno un Desire.

**Step 5 — Validazione e Export (Compass)**
L'utente rivede il framework BDI nel dashboard di Compass, corregge manualmente 2 Beliefs tramite l'editor JSON, verifica il grafo interattivo Belief↔Desire e procede all'export del framework in `data/bdi_frameworks/`.

**Step 6 — Generazione del Piano (Genius)**
Genius carica il framework esportato. L'utente seleziona il Desire "digitalizzazione dei processi interni" come obiettivo target. Dopo la fase Discovery (4 domande sul contesto operativo dell'utente), Genius genera un piano in 3 fasi per 11 settimane con 18 passi operativi, ancorati alle 9 Beliefs con rilevanza CRITICO e ALTO sul Desire selezionato. L'utente esporta il piano in Markdown.

---

## 9. Limitazioni Attuali

Una documentazione tecnico-scientifica rigorosa richiede una valutazione onesta dei limiti del sistema nella sua versione attuale. Le limitazioni di LUMIA Studio sono di natura architetturale, metodologica e valutativa.

**Single-user, nessuna concorrenza** — L'architettura attuale è progettata per un singolo utente per istanza applicativa. Non esiste un sistema di autenticazione, e la gestione della sessione attiva tramite file `.active_session` non supporta accessi concorrenti. Questo vincolo è accettabile per un prototipo di ricerca ma preclude l'uso in contesti multi-utente senza un refactoring architetturale significativo.

**Chiamate LLM sincrone e bloccanti** — Tutte le chiamate ai provider LLM sono sincrone e bloccano l'interfaccia utente per la durata della generazione. L'esperienza utente è mitigata da messaggi di spinner dinamici, ma l'assenza di async processing limita la responsività dell'applicazione su task di generazione lunghi.

**Persistenza su filesystem** — L'uso di file JSON e ChromaDB locale come unico meccanismo di persistenza non è scalabile oltre il singolo utente e non supporta backup automatici, versioning dei dati o deployment in ambienti cloud con storage effimero.

**Assenza di evaluation formale** — Il sistema non dispone di una test suite automatizzata né di benchmark di valutazione quantitativa. La qualità degli output — Desires elicitati, Beliefs estratte, piani generati — è stata valutata esclusivamente in modo qualitativo attraverso sessioni di uso reale. L'assenza di metriche formali costituisce il principale gap scientifico rispetto agli standard della ricerca in NLP e AI.

**Dipendenza da API esterne** — Il sistema dipende interamente da provider LLM esterni (Google, OpenAI) per le capacità generative. Interruzioni di servizio, variazioni nei prezzi API o cambiamenti nei modelli disponibili impattano direttamente sulla funzionalità del sistema. L'assenza di un layer di fallback o di modelli locali (es. via Ollama) rappresenta un rischio operativo.

**Agente Cuma in stato Beta** — L'agente per la pianificazione delle Intentions è funzionale ma privo dell'integrazione con il sistema Auditor, rendendo la qualità dei suoi output meno garantita rispetto agli agenti Alì e Believer.

---

## 10. Sviluppi Futuri

### 10.1 Valutazione Formale del Sistema

La priorità di ricerca più urgente è la definizione di un framework di valutazione quantitativa per LUMIA. Gli assi di valutazione identificati includono:

- **Qualità dei Desires elicitati** — coerenza con le effettive esigenze del dominio, completezza rispetto agli obiettivi strategici reali, misurabili tramite valutazione umana su scala Likert con esperti di dominio
- **Qualità delle Beliefs estratte** — precisione (le Beliefs sono fattuali e ancorate alle fonti?), richiamo (la knowledge base rilevante è stata esplorata sufficientemente?), correttezza della correlazione Belief↔Desire
- **Qualità dei piani generati da Genius** — fattibilità operativa, completezza, rilevanza rispetto al profilo utente
- **Efficacia dell'Auditor** — correlazione tra i punteggi assegnati dall'Auditor e la valutazione umana della qualità delle risposte

### 10.2 Architettura Multi-Utente

Il passaggio da architettura single-user a multi-utente richiede: introduzione di un sistema di autenticazione (anche semplice, es. OAuth via provider esterno), migrazione della persistenza da filesystem a database (PostgreSQL per dati strutturati, servizio cloud per ChromaDB), e gestione della concorrenza nelle sessioni attive.

### 10.3 Modelli LLM Locali

L'integrazione con runtime per modelli locali (Ollama, LM Studio) consentirebbe l'uso di LUMIA in ambienti air-gapped o con vincoli di privacy sui dati, eliminando la dipendenza da API esterne. Modelli open-weight di dimensione medio-grande (es. Llama 3, Mistral, Qwen) hanno dimostrato capacità sufficienti per task di estrazione strutturata comparabili a quelli di LUMIA.

### 10.4 Fine-Tuning su Dominio BDI

Un'area di ricerca ad alto potenziale è il fine-tuning di modelli di embedding e/o generativi su dataset di framework BDI prodotti da LUMIA. Un modello specializzato sulla struttura BDI potrebbe produrre output più coerenti e ridurre la necessità di prompt engineering elaborato, aumentando la robustezza del sistema su domini eterogenei.

### 10.5 Interoperabilità con Standard Ontologici

L'export del framework BDI verso standard ontologici formali (OWL, RDF, JSON-LD) consentirebbe l'integrazione di LUMIA con strumenti di knowledge management esistenti (Protégé, graph database come Neo4j) e la pubblicazione della conoscenza estratta come Linked Data. Questa direzione aprirebbe scenari di ricerca nell'intersezione tra knowledge engineering conversazionale e web semantico.

### 10.6 Agenti Specializzati Aggiuntivi

L'architettura modulare di LUMIA facilita l'aggiunta di nuovi agenti specializzati. Tra i candidati più promettenti:

- **Agente di sintesi comparativa** — confronta framework BDI di sessioni diverse, identificando pattern comuni e divergenze tra domini o beneficiari distinti
- **Agente di monitoraggio** — traccia nel tempo l'evoluzione dei Desires e delle Beliefs di un dominio, identificando cambiamenti strategici emergenti
- **Agente di interview** — conduce interviste strutturate a stakeholder multipli, consolidando i risultati in un framework BDI condiviso

### 10.7 Completamento dell'Agente Cuma

Il completamento dell'integrazione dell'Auditor in Cuma e il raffinamento del processo di generazione delle Intentions rappresentano uno sviluppo a breve termine che porterebbe a completamento la pipeline BDI di LUMIA, rendendo il sistema pienamente operativo su tutti e tre i livelli cognitivi del framework.

---

## 11. Conclusioni

LUMIA Studio rappresenta un'esperienza di ricerca applicata nell'intersezione tra intelligenza artificiale generativa, knowledge engineering e modellazione cognitiva formale. Il sistema dimostra la fattibilità di un approccio in cui il modello BDI — storicamente confinato alla programmazione di agenti autonomi — viene reinterpretato come struttura organizzativa per la conoscenza strategica umana, resa accessibile attraverso conversazioni in linguaggio naturale con agenti LLM specializzati.

I contributi principali del progetto possono essere sintetizzati in tre punti. Primo, la definizione e implementazione del paradigma *BDI-guided knowledge engineering*, in cui la tripartizione Belief-Desire-Intention funge da contratto formale tra sistema AI ed esperto umano per l'elicitazione e l'organizzazione della conoscenza di dominio. Secondo, l'architettura *conversational quality loop*, in cui meta-agenti Auditor specializzati valutano in tempo reale la qualità degli output conversazionali su rubric multidimensionali, introducendo una forma di meta-cognizione nel sistema. Terzo, l'estensione del paradigma RAG con retrieval goal-oriented, in cui i Desires dell'utente fungono da filtro semantico persistente sull'intera operazione di retrieval, producendo un'estrazione della conoscenza intrinsecamente finalistica.

Il sistema è operativo e ha dimostrato la propria applicabilità su scenari reali di consulenza strategica, ricerca applicata e formazione specialistica. Le limitazioni attuali — assenza di evaluation formale, architettura single-user, dipendenza da API esterne — sono ben identificate e costituiscono la roadmap per le successive fasi di sviluppo.

Il lavoro futuro si orienta verso due direzioni complementari: sul piano scientifico, la definizione di un framework di valutazione quantitativa che permetta di misurare e confrontare la qualità degli output di LUMIA; sul piano ingegneristico, l'evoluzione dell'architettura verso un sistema multi-utente, cloud-native e interoperabile con gli standard del web semantico.

LUMIA Studio costituisce, in questa fase, una piattaforma prototipale con solide fondamenta teoriche e un'architettura estensibile, pronta per essere validata su casi d'uso reali in ambito accademico e industriale.

---

## Appendice A — Struttura Completa del BDI JSON

```json
{
  "domain_summary": "Descrizione sintetica del dominio di conoscenza",
  "beneficiario": {
    "beneficiario_name": "Nome o categoria del beneficiario",
    "beneficiario_description": "Descrizione del profilo del beneficiario",
    "beneficiario_inference_notes": ["Note sull'inferenza condotta da Alì"]
  },
  "desires": [
    {
      "desire_id": "D1",
      "desire_statement": "Enunciato dell'obiettivo strategico",
      "priority": "high | medium | low",
      "motivation": "Motivazione profonda dell'obiettivo",
      "success_metrics": ["Metrica 1", "Metrica 2"],
      "context": "Contesto operativo dell'obiettivo"
    }
  ],
  "beliefs": [
    {
      "subject": "Soggetto della Belief",
      "definition": "COSA è. PERCHÉ conta. COME funziona.",
      "semantic_relations": [
        {
          "relation": "tipo di relazione",
          "object": "concetto correlato",
          "description": "descrizione della relazione"
        }
      ],
      "source": "Citazione della fonte documentale",
      "importance": 0.9,
      "confidence": 0.9,
      "related_desires": [
        {
          "desire_id": "D1",
          "relevance_level": "CRITICO | ALTO | MEDIO | BASSO",
          "definition": "Spiegazione della rilevanza"
        }
      ]
    }
  ],
  "intentions": [
    {
      "intention_id": "I1",
      "linked_desire": "D1",
      "linked_beliefs": ["B1", "B2"],
      "action_steps": [
        {
          "step": "Descrizione del passo",
          "effort": "stima effort",
          "dependencies": []
        }
      ],
      "expected_outcomes": ["Outcome atteso"],
      "risks": [
        {
          "risk": "Descrizione del rischio",
          "mitigation": "Strategia di mitigazione"
        }
      ]
    }
  ]
}
```

---

## Appendice B — Agenti e Prompt di Sistema

| Agente | File Prompt | Descrizione |
|--------|-------------|-------------|
| Alì | `ali_system_prompt.md` | Conversazione Socratica per elicitazione Desires |
| Believer | `believer_system_prompt.md` | Estrazione Beliefs in modalità interattiva |
| Believer | `believer_from_scratch_prompt.md` | Estrazione Beliefs senza belief base |
| Believer | `believer_mix_beliefs_prompt.md` | Estrazione Beliefs in modalità mista |
| Cuma | `cuma_system_prompt.md` | Pianificazione Intentions |
| Genius | `genius_discovery_prompt.md` | Fase Discovery del coach esecutivo |
| Genius | `genius_plan_generation_prompt.md` | Generazione piano d'azione |
| Genius | `genius_step_tips_prompt.md` | Arricchimento passi del piano |
| Auditor Desires | `desires_auditor_system_prompt.md` | Rubric valutazione Alì |
| Auditor Beliefs | `belief_auditor_system_prompt.md` | Rubric valutazione Believer |
| Auditor Intentions | `intention_auditor_system_prompt.md` | Rubric valutazione Cuma |

---

## Appendice C — Istruzioni di Installazione

```bash
# 1. Clonare il repository
git clone <repository-url>
cd unical

# 2. Creare e attivare un ambiente virtuale
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Installare le dipendenze
pip install -r requirements.txt

# 4. Scaricare il modello di embedding (una tantum, ~120 MB)
python setup_models.py

# 5. Configurare le API key
cp .env.example .env
# Editare .env e inserire almeno una tra:
# GOOGLE_API_KEY=...
# OPENAI_API_KEY=...

# 6. Avviare l'applicazione
streamlit run app.py
```

L'applicazione sarà disponibile su `http://localhost:8501`.
