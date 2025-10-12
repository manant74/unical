# 📋 Analisi System Prompts - LUMIA Studio

## Panoramica

Questo documento analizza i system prompts degli agenti **Alì** e **Believer** dopo il loro miglioramento, valutandone l'efficacia e proponendo eventuali ottimizzazioni.

---

## ✨ Alì - Agent for Desires

### 🎯 Punti di Forza

#### 1. **Ruolo Chiaro e Ben Definito**

✅ **Ottimo**: Alì è definito come "esperto di product strategy, user research e design thinking"

- Fornisce un framework mentale chiaro all'AI
- Stabilisce il tono professionale e collaborativo

#### 2. **Processo Strutturato in 7 Step**

✅ **Eccellente**: Il processo è ben articolato e progressivo

```markdown
1. Identificazione Dominio
2. Identificazione Personas
3. Selezione Persona
4. Esplorazione Desires
5. Sintesi per Persona
6. Iterazione
7. Generazione Report (solo su richiesta esplicita)
```

**Forza**: Lo Step 7 con "comando esplicito" previene output prematuri

#### 3. **Definizione Cristallina di "Desire"**

✅ **Molto Buono**:

- "Uno stato del mondo desiderato visto attraverso gli occhi dell'utente finale"
- Esempi concreti con prospettiva utente (Principiante vs Esperto)
- Evita ambiguità

#### 4. **Output JSON Strutturato**

✅ **Eccellente**: Schema JSON completo con:

- `domain_summary`
- `personas[]` con `persona_name`, `persona_description`, `desires[]`
- Ogni desire con: `desire_id`, `desire_statement`, `motivation`, `success_metrics`

**Forza**: Include `motivation` e `success_metrics` - va oltre il semplice desiderio

#### 5. **Guardrails e Principi Guida**

✅ **Ottimo**:

1. Rimani focalizzato sul contesto (no conoscenza esterna non pertinente)
2. Strategia, non implementazione (no soluzioni tecniche)
3. Linguaggio propositivo ("Si potrebbe considerare...")

### ⚠️ Aree di Miglioramento

#### 1. **Gestione Conversazione Lunga**

🟡 **Suggerimento**: Aggiungere checkpoint intermedi

```markdown
**Checkpoint Intermedi**: Ogni 3-4 domande, riassumi i punti emersi per:
- Validare comprensione
- Permettere all'utente di correggere/integrare
- Mantenere focus
```

#### 2. **Gestione Casi Edge**

🟡 **Suggerimento**: Aggiungere istruzioni per scenari comuni:

- Utente incerto sulle personas
- Utente con troppi desires per persona (>5)
- Utente che vuole tornare indietro e modificare

#### 3. **Validazione Qualità Desires**

🟡 **Suggerimento**: Criteri SMART impliciti

```markdown
**Validazione Interna**: Prima di confermare un desire, verifica mentalmente che sia:
- Specifico (non generico)
- Misurabile (ha success_metrics chiari)
- Orientato all'utente (prospettiva utente, non azienda)
- Rilevante al dominio
```

### 💡 Modifiche Proposte

**Aggiunta Sezione "Gestione Conversazione"**:

```markdown
## GESTIONE DELLA CONVERSAZIONE

### Checkpoint Intermedi
Ogni 3-4 domande, riassumi brevemente:
- "Finora abbiamo identificato X personas..."
- "Per [Persona Y] abbiamo esplorato questi desires..."

### Domande di Qualità
Se un desire sembra generico, usa domande come:
- "Puoi darmi un esempio concreto di quando questo desire emerge?"
- "Come saprebbe l'utente di aver soddisfatto questo desire?"
- "Cosa distingue questo desire tra diverse categorie di utenti?"

### Gestione Ambiguità
Se l'utente fornisce informazioni contrastanti:
- Evidenzia educatamente la contraddizione
- Chiedi chiarimenti senza giudicare
- Proponi alternative per risolvere l'ambiguità
```

---

## 💡 Believer - Agent for Beliefs

### 🎯 Punti di Forza

#### 1. **Ruolo Tecnico Chiaro**

✅ **Ottimo**: "Esperto analista in ingegneria della conoscenza"

- Stabilisce competenza tecnica
- Framework BDI esplicito

#### 2. **Principio di Rilevanza Centrale**

✅ **Eccellente**:
> "Se un fatto, per quanto vero, non ha alcuna attinenza con i desires elencati, DEVE ESSERE IGNORATO"

**Forza**: Previene information overload e mantiene focus

#### 3. **Struttura JSON Belief Ben Definita**

✅ **Molto Buono**:

```json
{
  "soggetto": "...",
  "relazione": "...",
  "oggetto": "...",
  "fonte": "...",
  "metadati": {...},
  "rilevanza": "..."
}
```

**Forza**: Include `fonte` (tracciabilità) e `rilevanza` (collegamento ai desires)

#### 4. **Regole Chiare**

✅ **Ottimo**:

1. Principio di Rilevanza
2. Fattualità Assoluta (no inferenze)
3. Atomicità (un fatto per belief)
4. Normalizzazione delle relazioni

#### 5. **Esempio Pratico (Few-Shot)**

✅ **Eccellente**: Esempio JWST con desires e output JSON concreto

- Mostra applicazione pratica
- Dimostra filtro di rilevanza

#### 6. **Approccio Interattivo**

✅ **Ottimo**:

- Chiede informazioni aggiuntive all'inizio
- Propone domande aperte
- Chiede feedback su belief individuati
- Report finale solo su comando esplicito

### ⚠️ Aree di Miglioramento

#### 1. **JSON Sintassi Incompleta**

🔴 **Errore**: Nelle righe 62, 95 mancano le virgolette di chiusura

```json
"tipo_oggetto": "Agenzia Spaziale"  // ← manca virgoletta
"tipo_oggetto": "Materiale"         // ← manca virgoletta
```

**Fix**:

```json
"tipo_oggetto": "Agenzia Spaziale"
"tipo_oggetto": "Materiale"
```

#### 2. **Gestione Conflitti tra Belief**

🟡 **Suggerimento**: Aggiungere istruzioni per gestire belief contraddittori

```markdown
**Gestione Contraddizioni**: Se identifichi belief che sembrano in conflitto:
1. Segnala il conflitto all'utente
2. Verifica le fonti
3. Se entrambi sono validi, includi entrambi con nota sulla contraddizione
4. Chiedi all'utente quale ha priorità o come interpretarli
```

#### 3. **Livelli di Rilevanza**

🟡 **Suggerimento**: Introdurre livelli di rilevanza espliciti

```json
"rilevanza": {
  "livello": "CRITICO|ALTO|MEDIO|BASSO",
  "desires_correlati": ["D1", "D2"],
  "spiegazione": "..."
}
```

#### 4. **Gestione Belief Impliciti**

🟡 **Suggerimento**: Chiarire approccio ai belief impliciti ma ragionevolmente derivabili

```markdown
**Belief Impliciti vs Espliciti**:
- EVITA inferenze speculative
- PERMETTI belief ragionevolmente derivabili se:
  - Strettamente logici dal testo
  - Rilevanti per i desires
  - Segnalati come "derivati" nei metadati
```

```markdown
## GESTIONE DELLA COMPLESSITÀ

### Per Domini Ricchi di Informazioni
Se il testo è molto lungo:
1. Inizia con una prima passata per identificare aree rilevanti
2. Chiedi all'utente se vuoi concentrarti su specifiche sezioni
3. Procedi in modo incrementale

### Per Belief Ambigui
Se un fatto è ambiguo o può essere interpretato in modi diversi:
1. Presenta le interpretazioni possibili all'utente
2. Chiedi quale sia corretta nel contesto dei desires
3. Annota l'interpretazione scelta nei metadati

### Livelli di Rilevanza
Classifica ogni belief:
- **CRITICO**: Impatto diretto e immediato sul raggiungimento di un desire
- **ALTO**: Supporta significativamente un desire
- **MEDIO**: Fornisce contesto utile per un desire
- **BASSO**: Marginalmente rilevante ma potenzialmente utile
```

**3. Sezione Output Finale Integrato**:

```markdown
## OUTPUT FINALE INTEGRATO (JSON)

Quando richiesto esplicitamente, genera un JSON che integra desires e beliefs:

\`\`\`json
{
  "metadata": {
    "domain": "Nome dominio",
    "timestamp": "ISO date",
    "version": "1.0"
  },
  "desires": [...],
  "beliefs": [...],
  "mappings": [
    {
      "desire_id": "D1",
      "related_beliefs": ["B1", "B3", "B7"],
      "coverage": "85%",
      "gaps": "Mancano informazioni su..."
    }
  ]
}
\`\`\`
```

---

## 🔄 Integrazione tra Alì e Believer

### Punti di Forza dell'Integrazione

✅ **Flusso Coerente**:

1. Alì → Identifica desires strutturati
2. Believer → Usa desires come filtro per beliefs
3. Output JSON compatibili

✅ **Comando Esplicito**:

- Entrambi richiedono conferma prima del report finale
- Previene output prematuri
- Mantiene controllo all'utente

### Aree da Migliorare nell'Integrazione

🟡 **IDs Consistenti**:

- Alì usa: `"desire_id": "P1-D1"` (Persona-Desire)
- Believer usa: `"desires_correlati": ["D1"]`
- **Suggerimento**: Allineare il formato degli ID

🟡 **Metadati Condivisi**:

```json
// Aggiungere in entrambi:
{
  "session_id": "UUID",
  "domain": "Nome dominio",
  "created_at": "timestamp"
}
```

---

## 📊 Valutazione Complessiva

### Alì - Agent for Desires

| Criterio | Valutazione | Note |
|----------|-------------|------|
| **Chiarezza Ruolo** | ⭐⭐⭐⭐⭐ | Eccellente |
| **Struttura Processo** | ⭐⭐⭐⭐⭐ | 7 step ben definiti |
| **Output Strutturato** | ⭐⭐⭐⭐⭐ | JSON completo e utile |
| **Guardrails** | ⭐⭐⭐⭐⭐ | Principi chiari |
| **Gestione Conversazione** | ⭐⭐⭐⭐☆ | Buono, può migliorare con checkpoint |
| **Gestione Edge Cases** | ⭐⭐⭐☆☆ | Da implementare |

**Punteggio Totale: 9.2/10** 🌟

### Believer - Agent for Beliefs

| Criterio | Valutazione | Note |
|----------|-------------|------|
| **Chiarezza Ruolo** | ⭐⭐⭐⭐⭐ | Eccellente |
| **Principio Rilevanza** | ⭐⭐⭐⭐⭐ | Fondamentale e chiaro |
| **Output Strutturato** | ⭐⭐⭐⭐⭐ | JSON ben progettato |
| **Regole Estrazione** | ⭐⭐⭐⭐⭐ | Chiare e complete |
| **Esempio Pratico** | ⭐⭐⭐⭐⭐ | Molto utile (con fix JSON) |
| **Interattività** | ⭐⭐⭐⭐⭐ | Approccio collaborativo |
| **Gestione Complessità** | ⭐⭐⭐☆☆ | Da migliorare |

**Punteggio Totale: 9.4/10** 🌟

---

## ✅ Raccomandazioni Finali

### Priorità Alta (Implementare Subito)

1. ✅ **Fix JSON syntax** in Believer esempio (righe 62, 95)
2. ✅ **Allineare ID format** tra Alì e Believer
3. ✅ **Aggiungere checkpoint intermedi** in Alì

### Priorità Media (Prossima Iterazione)

4. ⚠️ **Gestione casi edge** in entrambi
5. ⚠️ **Livelli di rilevanza** in Believer
6. ⚠️ **Metadati condivisi** per integrazione

### Priorità Bassa (Ottimizzazioni Future)

7. 💡 **Validazione SMART** automatica in Alì
8. 💡 **Gestione belief impliciti** in Believer
9. 💡 **Report di coverage** (mapping desires-beliefs)

---

## 🎯 Conclusione

**I prompt sono di ottima qualità** e rappresentano un notevole miglioramento rispetto alle versioni precedenti. Mostrano:

- Chiara comprensione del framework BDI
- Approccio metodologico strutturato
- Focus sull'interazione utente
- Output utili e processabili

Con le piccole modifiche proposte, i prompt saranno **eccellenti** e pronti per uso professionale.

---

**Ultimo aggiornamento**: 2025-01-15
**Versione Analisi**: 1.0
**Autore**: LUMIA Studio Development Team
