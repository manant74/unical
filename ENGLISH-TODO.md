# LUMIA Studio - English Translation TODO

This document tracks the complete transformation of LUMIA Studio from Italian to English.

## Translation Progress Overview

- **Total Components**: 35
- **Completed**: 9
- **In Progress**: 0
- **Not Started**: 26

---

## 1. SYSTEM PROMPTS (14 files) - CRITICAL PRIORITY

These are LLM agent instructions and must be translated carefully to preserve functionality.

### 1.1 Main Agent Prompts

- [ ] **prompts/ali_system_prompt.md** (86 lines, ~80% Italian)
  - Role definition and conversation guidelines
  - Desire extraction process
  - JSON schema documentation
  - Status: ⬜ Not Started

- [ ] **prompts/believer_system_prompt.md** (213 lines, ~85% Italian)
  - Knowledge engineering instructions
  - Belief extraction methodology
  - Relevance level definitions (CRITICO→CRITICAL, ALTO→HIGH, MEDIO→MEDIUM, BASSO→LOW)
  - Status: ⬜ Not Started

- [ ] **prompts/cuma_system_prompt.md** (135 lines, ~90% Italian)
  - Strategic mapping instructions
  - Intention generation guidelines
  - Domain mapping methodology
  - Status: ⬜ Not Started

### 1.2 Auditor Prompts

- [ ] **prompts/desires_auditor_system_prompt.md** (114 lines, ~95% Italian)
  - Quality evaluation rubric
  - Validation criteria
  - Output format specifications
  - Status: ⬜ Not Started

- [ ] **prompts/belief_auditor_system_prompt.md** (114 lines, ~95% Italian)
  - Belief validation criteria
  - Structure verification rules
  - Evidence requirements
  - Status: ⬜ Not Started

- [ ] **prompts/auditor_system_prompt.md** (~30% Italian)
  - General auditor guidelines
  - Status: ⬜ Not Started

### 1.3 Genius Agent Prompts

- [ ] **prompts/genius_discovery_prompt.md** (208 lines, ~40% Italian)
  - Discovery phase dialogue
  - Desire customization process
  - Context gathering questions
  - Status: ⬜ Not Started

- [ ] **prompts/genius_coach_template.md** (198 lines, ~20% Italian)
  - Coaching dialogue examples
  - Encouragement phrases
  - Status: ⬜ Not Started

- [ ] **prompts/genius_plan_generation_prompt.md** (~40% Italian)
  - Plan generation instructions
  - Status: ⬜ Not Started

- [ ] **prompts/genius_step_tips_prompt.md** (~45% Italian)
  - Step-by-step guidance
  - Status: ⬜ Not Started

- [ ] **prompts/genius_system_prompt.md** (Brief, mostly English)
  - Main system prompt
  - Status: ⬜ Not Started

### 1.4 Believer Support Prompts

- [ ] **prompts/belief_base_prompt.md** (~60% Italian)
  - Belief base extraction instructions
  - Status: ⬜ Not Started

- [ ] **prompts/believer_from_scratch_prompt.md** (~70% Italian)
  - From-scratch extraction process
  - Status: ⬜ Not Started

- [ ] **prompts/believer_mix_beliefs_prompt.md** (~65% Italian)
  - Mixed belief generation
  - Status: ⬜ Not Started

---

## 2. STREAMLIT PAGES (6 files) - HIGH PRIORITY

UI labels, buttons, messages, and user-facing text.

### 2.1 Core Pages

- [x] **pages/0_Compass.py** (2,279 lines, 1 Italian instance)
  - Sidebar button: "Torna alla Home" → "Back to Home" ✅
  - All other text was already in English
  - Status: ✅ Completed

- [x] **pages/1_Knol.py** (749 lines, ~40 Italian messages translated)
  - ✅ Dialog: "Editor Beliefs" → "Beliefs Editor"
  - ✅ Buttons: "Valida JSON" → "Validate JSON", "Salva" → "Save", "Crea Contesto" → "Create Context"
  - ✅ Labels: "Carica Fonti" → "Load Sources", "Fonti Caricate" → "Loaded Sources"
  - ✅ Error/Success messages: All translated to English
  - ✅ Tooltips and captions: All translated to English
  - Status: ✅ Completed

- [x] **pages/2_Ali.py** (871 lines, ~18 Italian instances)
  - ✅ Constants: ALI_MODULE_GOAL, ALI_EXPECTED_OUTCOME
  - ✅ UI messages: Session info, KB loaded, warnings
  - ✅ Buttons: "Nuova Conversazione" → "New Conversation", "Completa Sessione" → "Complete Session"
  - ✅ Success/error messages: All translated to English
  - ✅ Sidebar labels, tooltips, expander headers
  - ✅ Initial greeting message
  - ✅ Auditor feedback UI
  - ✅ RAG context display
  - Status: ✅ Completed

- [x] **pages/3_Believer.py** (1,332 lines, ~90+ Italian instances translated)
  - ✅ Constants: BELIEVER_MODULE_GOAL, BELIEVER_EXPECTED_OUTCOME
  - ✅ Quick reply UI labels ("Auditor Quick Suggestions", "Option X")
  - ✅ Session status messages ("Active Session", "No active session")
  - ✅ Configuration headers ("Believer Configuration", "Session Control")
  - ✅ Button labels ("New", "Complete", "Add Belief Manually")
  - ✅ Sidebar sections ("Available Desires", "Available Base Beliefs", "Identified Beliefs")
  - ✅ Main page title and welcome message
  - ✅ Prerequisite check messages (KB empty, no desires, no provider)
  - ✅ Greeting messages (with/without base beliefs options)
  - ✅ Four-option button pills ("Chat to Create...", "Review Base Beliefs", "Create Mix...", "Generate from Scratch")
  - ✅ Response messages for all 4 options
  - ✅ Mix generation progress messages ("Preparing context...", "Querying KB...", "Analyzing with LLM...")
  - ✅ From-scratch generation messages and progress updates
  - ✅ Success/error messages (mix completed, JSON parsing errors, generation errors)
  - ✅ Chat input placeholder
  - ✅ Auditor feedback labels ("Rubric scores", "Detected issues", "Suggestions for agent")
  - ✅ RAG context expander ("Context & Desires Details", "User Desires", "Priority")
  - ✅ Statistics labels ("Messages", "Identified Beliefs", "KB Contents")
  - ✅ All user-facing error/warning/info/success messages
  - Status: ✅ Completed

- [x] **pages/4_Cuma.py** (529 lines, ~50+ Italian instances translated)
  - ✅ Constants: CUMA_MODULE_GOAL, CUMA_EXPECTED_OUTCOME
  - ✅ Session status messages ("Active Session", "No active session")
  - ✅ Configuration headers ("CUMA Configuration", "Session Control")
  - ✅ Button labels ("New Conversation", "Complete Session", "Go to Compass", "Go to Alì")
  - ✅ Sidebar sections ("Loaded Data", "Statistics", "Defined Intentions")
  - ✅ Main page title and subtitle
  - ✅ Prerequisite check messages (no desires, no beliefs)
  - ✅ Greeting message (Domain Strategy Mapper introduction)
  - ✅ Two-option button pills ("Map multiple Intentions", "Deep dive into a specific aspect")
  - ✅ AI context headers ("AVAILABLE BELIEFS", "AVAILABLE DESIRES", "Intentions defined so far")
  - ✅ Success/error messages (session completed, JSON extracted, AI errors)
  - ✅ Chat input placeholder
  - ✅ All user-facing error/warning/info/success messages
  - Status: ✅ Completed

- [x] **pages/6_Genius.py** (778 lines, ~50+ Italian instances translated)
  - ✅ Tab labels: "Nuovo Piano" → "New Plan", "Carica Piano Esistente" → "Load Existing Plan"
  - ✅ Button text: "Carica" → "Load", "Salva Piano" → "Save Plan", "Torna alla Home" → "Back to Home"
  - ✅ Section headers: "Fase" → "Phase", "Configurazione LLM" → "LLM Configuration"
  - ✅ Error messages, success messages, greeting messages
  - ✅ All metrics, progress indicators, and summary views
  - Status: ✅ Completed

---

## 3. UTILITY MODULES (8 files) - MEDIUM PRIORITY

Error messages, logging, and helper functions.

- [x] **utils/ui_messages.py** (38 lines, 25 messages - ALL translated)
  - ✅ All 25 thinking/loading messages translated
  - ✅ Sci-fi themed messages translated creatively while preserving playful tone
  - ✅ Docstring translated
  - Status: ✅ Completed

- [x] **utils/auditor.py** (402 lines, ~40 Italian instances translated)
  - ✅ FINALIZATION_KEYWORDS: All 28 phrases translated
  - ✅ FINALIZATION_VERBS: All 21 verbs translated
  - ✅ FINALIZATION_OBJECTS: Cleaned up (removed Italian duplicates)
  - ✅ EXPECTED_FINALIZATION_KEYWORDS: All 9 phrases translated
  - ✅ MODULE_FINALIZATION_LABELS: All labels translated
  - ✅ MODULE_STRUCTURED_MARKERS: Cleaned up (removed Italian duplicates)
  - ✅ Class docstring translated
  - ✅ Method docstring translated
  - ✅ All error messages and user-facing strings translated
  - Status: ✅ Completed

- [ ] **utils/context_manager.py** (304 lines, ~7 Italian instances)
  - Error logging messages
  - Status: ⬜ Not Started

- [ ] **utils/document_processor.py** (263 lines, ~5 Italian instances)
  - Error handling messages
  - Status: ⬜ Not Started

- [ ] **utils/prompts.py** (121 lines, ~1 Italian instance)
  - Error message: "File prompt non trovato"
  - Status: ⬜ Not Started

- [ ] **utils/session_manager.py** (311 lines)
  - Review for any Italian content
  - Status: ⬜ Not Started

- [ ] **utils/llm_manager.py** (190 lines)
  - Review for any Italian content
  - Status: ⬜ Not Started

- [x] **utils/genius_engine.py** (570 lines)
  - ✅ All user-facing content already in English
  - ✅ Print statements are debugging-only (not user-facing)
  - ✅ No Italian UI messages found
  - Status: ✅ Completed (no changes needed)

---

## 4. HOMEPAGE & DOCUMENTATION (3 files) - LOW PRIORITY

- [x] **app.py** (18 Italian comments - all translated)
  - Translated all Python and CSS comments
  - All user-facing content was already in English
  - Status: ✅ Completed

---

## 5. TESTING & VALIDATION

After translation, these components need testing:

- [ ] **Agent Conversations**
  - Test Alì conversation flow in English
  - Test Believer extraction in English
  - Test Genius coaching in English
  - Status: ⬜ Not Started

- [ ] **UI Components**
  - Verify all buttons and labels display correctly
  - Check error messages appear properly
  - Validate thinking messages show appropriately
  - Status: ⬜ Not Started

- [ ] **Auditor Functionality**
  - Test keyword detection with English phrases
  - Verify finalization detection works
  - Validate rubric scoring
  - Status: ⬜ Not Started

- [ ] **End-to-End Workflow**
  - Complete workflow from Knol → Compass → Alì → Believer → Genius
  - Verify JSON generation
  - Check session management
  - Status: ⬜ Not Started

## 6 Altro

- [ ] **README.md**
  - Review and update if needed
  - Status: ⬜ Not Started

- [ ] **CLAUDE.md**
  - Update to reflect English-first application
  - Status: ⬜ Not Started

---

## Translation Guidelines

### Key Terms Mapping

| Italian | English | Notes |
|---------|---------|-------|
| Beneficiario | Stakeholder/Beneficiary | Context-dependent |
| Desiderio/Desire | Desire | Keep "Desire" |
| Belief | Belief | Already English |
| Intenzione | Intention | Keep "Intention" |
| CRITICO | CRITICAL | Relevance level |
| ALTO | HIGH | Relevance level |
| MEDIO | MEDIUM | Relevance level |
| BASSO | LOW | Relevance level |
| Responsabile di Dominio | Domain Owner | |
| Sessione Attiva | Active Session | |
| Knowledge Base | Knowledge Base | Already English |
| Torna alla Home | Back to Home | |

### Relevance Level Mapping

```python
# OLD (Italian)
"CRITICO", "ALTO", "MEDIO", "BASSO"

# NEW (English)
"CRITICAL", "HIGH", "MEDIUM", "LOW"
```

### Agent Module Goals

Update constants in agent files:

```python
# OLD
ALI_MODULE_GOAL = "Guidare il responsabile..."
ALI_EXPECTED_OUTCOME = "Progredire verso..."

# NEW
ALI_MODULE_GOAL = "Guide the domain owner..."
ALI_EXPECTED_OUTCOME = "Progress toward..."
```

---

## Status Legend

- ⬜ Not Started
- 🟦 In Progress
- ✅ Completed
- ⚠️ Blocked/Issues

---

## Completion Metrics

### By Category

- System Prompts: 0/14 (0%)
- Streamlit Pages: 6/6 (100%) ✅
- Utility Modules: 3/8 (38%)
- Homepage & Docs: 1/3 (33%)
- Testing: 0/4 (0%)

### Overall Progress

- Total Items: 35
- Completed: 9 (26%)
- Remaining: 26

---

## Notes

- Focus on CRITICAL priority items first (system prompts)
- Test agent functionality after each prompt translation
- Preserve JSON schema structures exactly
- Keep technical terms consistent across all files
- Maintain the same tone and style in English as the Italian original
- Special attention to ui_messages.py - preserve the playful sci-fi theme

---

*Last Updated: 2026-02-01*

---

## Recent Changes

### 2026-02-01 (Latest)

- ✅ **utils/auditor.py**: Completed translation
  - Translated ~40 Italian user-facing messages and keyword lists (402 lines total)
  - FINALIZATION_KEYWORDS (28 phrases): "procedi con il report" → "proceed with the report", "genera il json" → "generate the json", etc.
  - FINALIZATION_VERBS (21 verbs): "formalizza" → "formalize", "genera" → "generate", "produci" → "produce", etc.
  - FINALIZATION_OBJECTS: Removed Italian duplicates ("desiderio", "desideri"), kept English-only list
  - EXPECTED_FINALIZATION_KEYWORDS (9 phrases): "report json finale" → "final json report", etc.
  - MODULE_FINALIZATION_LABELS: "report JSON dei desire" → "JSON report of desires", "report JSON dei belief" → "JSON report of beliefs"
  - MODULE_STRUCTURED_MARKERS: Removed Italian markers ("desiderio:", "motivazione:", "successo:", "metriche di successo", "criteri di successo")
  - Class docstring: "Gestisce le chiamate all'agente Auditor..." → "Manages calls to the Auditor agent..."
  - Method docstring: "Invia la conversazione all'Auditor..." → "Sends the conversation to the Auditor..."
  - Error messages: "L'utente ha richiesto..." → "The user requested...", "Il flusso corrente richiede..." → "The current workflow requires...", etc.
  - All suggested replies and focus messages translated
  - Code comments NOT translated (per user request)

- ✅ **utils/ui_messages.py**: Completed translation
  - Translated all 25 thinking/loading messages while preserving playful sci-fi theme
  - Original messages: "Sto tessendo connessioni...", "Sto consultando la Biblioteca di Babele...", "Sto attivando i neuroni positronici..."
  - Translated: "Weaving connections...", "Consulting the Library of Babel...", "Activating positronic neurons..."
  - Preserved references to classic sci-fi: Asimov (positronic), Borges (Library of Babel), Blade Runner (tears in rain), Star Wars (Force, Jedi archives), Foundation, Matrix
  - Docstring translated: "Restituisce un messaggio casuale..." → "Returns a random message..."
  - Code comments NOT translated (per user request)
  - **Note**: User later enriched this file with 40+ additional sci-fi messages (Dune, Hitchhiker's Guide, Doctor Who, Neuromancer, 2001, etc.) with detailed legend

### 2026-02-01 (Earlier)

- ✅ **pages/6_Genius.py**: Completed translation (user-facing only)
  - Translated ~50+ Italian user-facing messages across entire file (778 lines)
  - Tab labels: "Nuovo Piano" → "New Plan", "Carica Piano Esistente" → "Load Existing Plan"
  - Buttons: "Torna alla Home" → "Back to Home", "Ricomincia da Capo" → "Start Over", "Carica" → "Load", "Salva Piano" → "Save Plan", "Esporta Markdown" → "Export Markdown", "Arricchisci con Tips e Tools" → "Enrich with Tips and Tools"
  - Configuration UI: "Configurazione LLM" → "LLM Configuration", "Modello" → "Model", "Impostazioni Avanzate" → "Advanced Settings"
  - Section headers: "Fase" → "Phase", "Selezione Corrente" → "Current Selection", "Beliefs Utilizzati nel Piano" → "Beliefs Used in the Plan"
  - Progress tracking: "completato" → "complete", "Fase Corrente" → "Current Phase", "Step Corrente" → "Current Step"
  - Metrics: "Fasi" → "Phases", "Steps Totali" → "Total Steps", "Durata Stimata" → "Estimated Duration", "settimane" → "weeks", "giorni" → "days"
  - Plan generation: "Generazione Piano in Corso" → "Plan Generation in Progress", "Piano Generato con Successo" → "Plan Generated Successfully"
  - Greeting messages: "Ciao! Ho caricato..." → "Hello! I've loaded...", "Su quale desire vuoi lavorare oggi?" → "Which desire would you like to work on today?"
  - Error messages: "Errore LLM" → "LLM Error", "Errore nella generazione del piano" → "Error generating plan", "Errore nel salvataggio" → "Error saving plan"
  - Success messages: "Tips generati con successo" → "Tips generated successfully", "Piano salvato con successo" → "Plan saved successfully"
  - Summary view: "Visualizza Riepilogo" → "View Summary", "Riepilogo Sessione Genius" → "Genius Session Summary", "Conversazione" → "Conversation", "Priorità" → "Priority"
  - Upcoming features: "Prossimi Sviluppi" → "Upcoming Features"
  - All tooltips and help text translated
  - Code comments NOT translated (per user request)

- ✅ **utils/genius_engine.py**: Completed review (no changes needed)
  - All user-facing content already in English
  - Print statements are debugging-only (not user-facing)
  - Error messages already in English
  - No Italian UI messages found

- **🎉 MILESTONE: All Streamlit Pages Complete (6/6 - 100%)**
  - Compass ✅
  - Knol ✅
  - Alì ✅
  - Believer ✅
  - Cuma ✅
  - Genius ✅

### 2026-02-01 (Earlier)

- ✅ **pages/4_Cuma.py**: Completed translation (user-facing only)
  - Translated ~50+ Italian user-facing messages across entire file (529 lines)
  - Module constants: CUMA_MODULE_GOAL ("Map multiple possible strategic Intentions..."), CUMA_EXPECTED_OUTCOME ("A complete mapping of multiple alternative strategic Intentions...")
  - Greeting message: Domain Strategy Mapper introduction with role explanation
  - Session management: "Active Session", "No active session", "Session completed! X Intentions saved"
  - Configuration UI: "CUMA Configuration", "LLM Provider", "Model", "Session Control"
  - Button labels: "New Conversation" / "Complete Session", "Map multiple Intentions for the domain", "Deep dive into a specific aspect"
  - Sidebar sections: "Loaded Data" (Desires, Beliefs, Defined Intentions), "Statistics" (Messages, Created Intentions)
  - Prerequisite checks: "No Desire found in session", "No Belief found in session", "Complete the Alì/Believer phase"
  - AI context preparation: "AVAILABLE BELIEFS", "AVAILABLE DESIRES", "Intentions defined so far", "No beliefs/desires available"
  - Error messages: "No response received from AI", "Error communicating with AI", "Error saving Intentions"
  - Success messages: "JSON report extracted successfully!", "Session completed!"
  - Navigation buttons: "Go to Compass", "Go to Alì", "Back to Home"
  - Chat placeholder: "Write your message for Cuma..."
  - Code comments NOT translated (per user request)

### 2026-02-01 (Earlier)

- ✅ **pages/3_Believer.py**: Completed translation (user-facing only)
  - Translated ~90+ Italian user-facing messages across entire file (1,332 lines)
  - Module constants: BELIEVER_MODULE_GOAL, BELIEVER_EXPECTED_OUTCOME
  - Greeting messages with 4-option workflow (specialized chat, review base beliefs, mix generation, from-scratch)
  - All button labels: "New" / "Complete", "Chat to Create Specialized Beliefs", "Review Base Beliefs", "Create Mix...", "Generate from Scratch"
  - Session management messages: "Active Session", "No active session", "Session completed"
  - Configuration UI: "Believer Configuration", "LLM Provider", "Model", "Session Control"
  - Manual belief form: "Add Belief Manually", "Description", "Type", "Confidence", "Related Desires", "Evidence"
  - Sidebar sections: "Available Desires", "Available Base Beliefs", "Identified Beliefs", "Statistics"
  - Progress messages for automated generation: "Preparing context", "Querying knowledge base", "Analyzing with LLM"
  - Success/error/warning messages: All translated to English
  - Auditor feedback labels: "Auditor Quick Suggestions", "Rubric scores", "Detected issues", "Suggestions for agent"
  - RAG context display: "Context & Desires Details", "User Desires", "Priority"
  - Statistics metrics: "Messages", "Identified Beliefs", "KB Contents"
  - Chat input placeholder: "Write your message..."
  - All prerequisite check messages (empty KB, no desires, no provider configured)
  - Code comments NOT translated (per user request)

### 2026-01-31

- ✅ **app.py**: Completed translation of all 18 Italian comments (Python and CSS)
  - All user-facing content was already in English
  - Translated internal code comments for consistency

- ✅ **pages/0_Compass.py**: Completed translation (user-facing only)
  - Translated 1 Italian tooltip: "Torna alla Home" → "Back to Home"
  - All other UI text was already in English
  - Code comments NOT translated (per user request)

- ✅ **pages/1_Knol.py**: Completed translation (user-facing only)
  - Translated ~40 Italian user-facing messages
  - Dialog title: "Editor Beliefs" → "Beliefs Editor"
  - Buttons: "Valida JSON" → "Validate JSON", "Salva" → "Save", etc.
  - Form labels: "Carica Fonti" → "Load Sources", "Crea Contesto" → "Create Context"
  - Success/Error messages: All translated to English
  - Tooltips and captions: All translated to English
  - Code comments NOT translated (per user request)
