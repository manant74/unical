# LUMIA Studio - English Translation TODO

This document tracks the complete transformation of LUMIA Studio from Italian to English.

## Translation Progress Overview

- **Total Components**: 35
- **Completed**: 3
- **In Progress**: 0
- **Not Started**: 32

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

- [ ] **pages/2_Ali.py** (871 lines, ~18 Italian instances)
  - Constants: ALI_MODULE_GOAL, ALI_EXPECTED_OUTCOME
  - UI messages: Session info, KB loaded, warnings
  - Buttons: "Nuova Conversazione", "Completa Sessione"
  - Success/error messages
  - Status: ⬜ Not Started

- [ ] **pages/3_Believer.py** (1,332 lines, ~25 Italian instances)
  - Constants: BELIEVER_MODULE_GOAL, BELIEVER_EXPECTED_OUTCOME
  - Quick reply UI labels
  - Session status messages
  - Configuration headers
  - Error handling messages
  - Status: ⬜ Not Started

- [ ] **pages/4_Cuma.py** (529 lines, ~10 Italian instances)
  - Constants: CUMA_MODULE_GOAL, CUMA_EXPECTED_OUTCOME
  - CSS comments
  - UI labels and metrics
  - Status: ⬜ Not Started

- [ ] **pages/6_Genius.py** (778 lines, ~8 Italian instances)
  - Tab labels: "Nuovo Piano", "Carica Piano Esistente"
  - Button text: "Carica", "Salva Piano"
  - Section headers
  - Error messages
  - Status: ⬜ Not Started

---

## 3. UTILITY MODULES (8 files) - MEDIUM PRIORITY

Error messages, logging, and helper functions.

- [ ] **utils/ui_messages.py** (38 lines, 25 messages - ALL Italian)
  - All 25 thinking/loading messages
  - Sci-fi themed messages to translate creatively
  - Status: ⬜ Not Started

- [ ] **utils/auditor.py** (402 lines, ~40 Italian instances)
  - Finalization keywords list
  - Verb keywords
  - Object keywords
  - Error messages with Italian references
  - Status: ⬜ Not Started

- [ ] **utils/context_manager.py** (304 lines, ~7 Italian instances)
  - Error logging messages
  - Status: ⬜ Not Started

- [ ] **utils/document_processor.py** (263 lines, ~5 Italian instances)
  - Error handling messages
  - Code comments
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

- [ ] **utils/genius_engine.py** (570 lines)
  - Review for any Italian content
  - Status: ⬜ Not Started

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
- Streamlit Pages: 2/6 (33%)
- Utility Modules: 0/8 (0%)
- Homepage & Docs: 1/3 (33%)
- Testing: 0/4 (0%)

### Overall Progress
- Total Items: 35
- Completed: 3 (9%)
- Remaining: 32

---

## Notes

- Focus on CRITICAL priority items first (system prompts)
- Test agent functionality after each prompt translation
- Preserve JSON schema structures exactly
- Keep technical terms consistent across all files
- Maintain the same tone and style in English as the Italian original
- Special attention to ui_messages.py - preserve the playful sci-fi theme

---

*Last Updated: 2026-01-31*

---

## Recent Changes

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
