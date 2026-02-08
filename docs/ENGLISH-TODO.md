# LUMIA Studio - English Translation TODO

This document tracks the complete transformation of LUMIA Studio from Italian to English.

## Translation Progress Overview

- **Total Components**: 35
- **Completed**: 14
- **In Progress**: 0
- **Not Started**: 21

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

## 5. TESTING & VALIDATION

After translation, these components need testing:

- [ ] **Agent Conversations**
  - Test Alì conversation flow in English
  - Test Believer extraction in English
  - Test Genius coaching in English
  - Status: ⬜ Not Started

- [ ] **Auditor Functionality**
  - Test keyword detection with English phrases
  - Verify finalization detection works
  - Validate rubric scoring
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

## Notes

- Focus on CRITICAL priority items first (system prompts)
- Test agent functionality after each prompt translation
- Preserve JSON schema structures exactly
- Keep technical terms consistent across all files
- Maintain the same tone and style in English as the Italian original
- Special attention to ui_messages.py - preserve the playful sci-fi theme

---
