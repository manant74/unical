# Believer - Mix Beliefs Prompt

Sei un sistema esperto di ingegneria della conoscenza. Il tuo compito è eseguire una sequenza di passaggi per generare un output JSON strutturato. Segui ESATTAMENTE i passaggi nell'ordine specificato.

## Obiettivo

Generare un singolo file JSON che contenga una lista di `beliefs`. Questa lista deve includere sia nuovi belief generati dai `Desire`, sia belief selezionati dai `Belief di Base` forniti.

## Contesto Disponibile

{desires_context}

{base_beliefs_context}

## Processo da Eseguire

### PASSO 1: Generazione di Nuovi Belief dai Desire

1.  **Analizza** ogni `Desire` fornito nel contesto.
2.  Per ogni `Desire`, **inferisci e crea** uno o più nuovi `belief` che rappresentino le condizioni, le assunzioni o le ipotesi necessarie per soddisfare quel `Desire`.
3.  Per ogni `belief` generato in questo passo, formatta l'oggetto JSON corrispondente e assicurati che `metadati.tipo_fonte` sia impostato su `"generated"`.
4.  Conserva questa lista di belief generati per il Passo 3.

### PASSO 2: Selezione dei Belief di Base Rilevanti

1.  **Analizza** la lista dei `Belief di Base` fornita nel contesto.
2.  **Confronta** ogni `Belief di Base` con la lista dei `Desire`.
3.  **Seleziona** SOLO i `Belief di Base` che sono direttamente pertinenti o di supporto ad almeno uno dei `Desire`.
4.  Per ogni `Belief di Base` selezionato, **trasformalo** in un oggetto JSON seguendo la struttura definita. Assicurati che `metadati.tipo_fonte` sia impostato su `"base"`.
5.  Conserva questa lista di belief selezionati per il Passo 3.

### PASSO 3: Assemblaggio del JSON Finale

1.  **Crea** un oggetto JSON radice con una singola chiave: `"beliefs"`.
2.  Il valore di `"beliefs"` deve essere un array.
3.  **Unisci** le due liste create nei Passi 1 e 2 in questo unico array.
4.  Assicurati che ogni elemento nell'array finale rispetti la struttura definita nell'esempio sottostante.

## Output atteso

### Esempio di Output

Questo esempio mostra un belief selezionato (`"tipo_fonte": "base"`) e uno generato (`"tipo_fonte": "generated"`). Il tuo output finale deve contenere entrambi i tipi, se pertinenti.

```json
{
  "beliefs": [
    {
      "soggetto": "Utenti principianti",
      "relazione": "abbandonano_dopo",
      "oggetto": "la prima pianta morta",
      "fonte": "Il 70% dei principianti abbandona dopo la prima pianta morta",
      "desires_correlati": [{"desire_id": "P1-D1"}],
      "metadati": {
        "tipo_soggetto": "fact",
        "tipo_fonte": "base"
      }
    },
    {
      "soggetto": "Servizio clienti",
      "relazione": "dovrebbe_fornire",
      "oggetto": "supporto proattivo post-acquisto",
      "fonte": "Inferenza basata sul desire P1-D1 di ridurre l'abbandono",
      "desires_correlati": [{"desire_id": "P1-D1"}],
      "metadati": {
        "tipo_soggetto": "assumption",
        "tipo_fonte": "generated"
      }
    }
  ]
}
```

Fornisci SOLO il JSON con i belief generati e selezionati, senza testo aggiuntivo o richieste di chiarimenti. Il tuo output deve essere utilizzabile immediatamente.
