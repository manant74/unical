# Genius Agent - Requirements Document

**Version**: 1.0
**Date**: 2026-01-10
**Status**: Design Phase
**Author**: Brainstorming Session

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [User Flow](#user-flow)
4. [Data Model](#data-model)
5. [UI Specifications](#ui-specifications)
6. [LLM Strategy](#llm-strategy)
7. [Implementation Plan](#implementation-plan)
8. [Technical Decisions](#technical-decisions)

---

## Overview

### Purpose

**Genius** is a BDI-based execution coach that helps users achieve their desires by creating personalized action plans and providing interactive step-by-step guidance.

### Key Characteristics

- **Domain-Agnostic**: Works with ANY BDI framework across different domains
- **Multi-BDI Support**: Users can select which BDI framework to work with
- **Personal Coach**: Provides 1-on-1 guidance for executing specific desires
- **Adaptive**: Adjusts plans based on user context (role, timeline, constraints)
- **Interactive**: Conversational Q&A support during execution

### Positioning vs Other Agents

| Agent | Focus | Output | User Type |
|-------|-------|--------|-----------|
| **Alì** | Desires extraction | Desires list | Strategist |
| **Believer** | Beliefs extraction | Beliefs with correlations | Analyst |
| **Cuma** | Strategic scenarios | Multiple alternative intentions | Decision Maker |
| **Genius** | Personal execution | Single actionable plan for 1 desire | Executor/Individual Contributor |

**Key Difference from Cuma:**

- **Cuma**: Explores multiple strategic scenarios (what-if analysis)
- **Genius**: Creates ONE personalized execution plan (how-to-do-it)

---

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    GENIUS ARCHITECTURE                      │
│                  (Domain-Agnostic Coach)                    │
└─────────────────────────────────────────────────────────────┘

INPUT: Multiple BDI Frameworks (JSON files)
       ├── data/bdi_frameworks/ecommerce_retention.json
       ├── data/bdi_frameworks/healthcare_optimization.json
       └── data/bdi_frameworks/{domain}.json

GENIUS PHASES:
  ┌─────────────────────────────────────────────────────────┐
  │ PHASE 1: Discovery (Generic Agent)                     │
  ├─────────────────────────────────────────────────────────┤
  │ 1. BDI Selection (from bdi_frameworks/)                │
  │ 2. Desire Customization (conversational)                   │
  │ 3. User Context Gathering (chat)                       │
  │    - Role                                              │
  │    - Timeline                                          │
  │    - Current situation                                 │
  │    - Constraints                                       │
  │ 4. Generate User Profile                              │
  └─────────────────────────────────────────────────────────┘
                         ↓
  ┌─────────────────────────────────────────────────────────┐
  │ PHASE 2: Specialized Mode (Dynamic Prompt Generation)  │
  ├─────────────────────────────────────────────────────────┤
  │ 1. Filter relevant beliefs (CRITICO + ALTO)           │
  │ 2. Generate specialized system prompt:                │
  │    - Domain terminology from BDI                      │
  │    - Concrete examples from beliefs                   │
  │    - User constraints from profile                    │
  │ 3. Generate action plan structure                     │
  │ 4. Refine plan phase-by-phase (iterative)            │
  └─────────────────────────────────────────────────────────┘
                         ↓
  ┌─────────────────────────────────────────────────────────┐
  │ PHASE 3: Execution Support (Interactive Coaching)      │
  ├─────────────────────────────────────────────────────────┤
  │ 1. Step-by-step guidance                              │
  │ 2. Q&A on specific steps                              │
  │ 3. Progress tracking                                  │
  │ 4. Adaptive refinement based on feedback             │
  └─────────────────────────────────────────────────────────┘

OUTPUT: Personalized Action Plan (saved to session)
        └── data/sessions/{session_id}/genius_plans/plan_{id}.json
```

### File System Structure

```
data/
├── bdi_frameworks/                  # ← NEW: BDI source files
│   ├── ecommerce_retention.json    # User populates these
│   ├── healthcare_optimization.json
│   ├── education_platform.json
│   └── {domain_name}.json
│
└── sessions/{session_id}/
    ├── metadata.json
    ├── config.json
    ├── current_bdi.json             # Original session BDI
    ├── belief_base.json
    ├── chat_history/
    └── genius_plans/                # ← NEW: Genius outputs
        ├── plan_{plan_id}.json      # Generated plans
        └── .active_plan             # Current active plan ID
```

**Note on BDI Source:**

- User manually populates `data/bdi_frameworks/` with BDI JSON files
- Format: Standard `current_bdi.json` schema
- Genius lists available BDI files for selection

---

## User Flow

### Complete Journey

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 0: PAGE LOAD                                           │
└─────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: BDI SELECTION                                       │
├─────────────────────────────────────────────────────────────┤
│ UI: Card-based selection                                    │
│                                                             │
│  📂 Select BDI Framework to work with:                      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🎯 E-commerce Retention Strategy                    │   │
│  │    5 desires, 23 beliefs                            │   │
│  │    Tags: retention, e-commerce                      │   │
│  │    [Select This BDI]                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🏥 Healthcare Optimization Project                  │   │
│  │    3 desires, 18 beliefs                            │   │
│  │    Tags: healthcare, optimization                   │   │
│  │    [Select This BDI]                                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
              ↓ User selects BDI
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: DESIRE CUSTOMIZATION (Conversational)               │
├─────────────────────────────────────────────────────────────┤
│ Genius: "Ho caricato il BDI 'E-commerce Retention'.        │
│         Vedo 5 desires definiti:                            │
│                                                             │
│         🎯 D1: Aumentare retention da 65% a 80% (HIGH)     │
│         🎯 D2: Implementare onboarding in-app (MEDIUM)     │
│         🎯 D3: Ridurre churn post-trial (HIGH)             │
│         🎯 D4: Migliorare NPS score (LOW)                  │
│         🎯 D5: Ottimizzare pricing strategy (MEDIUM)       │
│                                                             │
│         Su quale desire vuoi lavorare oggi?"                │
│                                                             │
│ User: "Voglio lavorare su D2"                              │
└─────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: USER CONTEXT GATHERING (Conversational)            │
├─────────────────────────────────────────────────────────────┤
│ Genius asks sequentially:                                  │
│                                                             │
│ 1️⃣ "Qual è il tuo ruolo nel progetto?"                     │
│    User: "Sono un Product Manager"                         │
│                                                             │
│ 2️⃣ "Quanto tempo hai a disposizione? (settimane/mesi)"     │
│    User: "3 mesi"                                           │
│                                                             │
│ 3️⃣ "Qual è la situazione attuale?"                         │
│    User: "Abbiamo onboarding basilare da migliorare"       │
│                                                             │
│ 4️⃣ "Ci sono vincoli particolari?"                          │
│    User: "Team piccolo, solo io e uno sviluppatore"        │
│                                                             │
│ Genius: "Perfetto! Ho tutte le info. Genero il piano..."   │
└─────────────────────────────────────────────────────────────┘
              ↓ [LLM generates plan structure]
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: PLAN GENERATION & PRESENTATION                     │
├─────────────────────────────────────────────────────────────┤
│ Genius: "✅ Piano generato!                                │
│                                                             │
│  📊 PIANO PERSONALIZZATO PER D2                            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  🎯 Obiettivo: Implementare onboarding in-app              │
│  ⏱️ Timeline: 12 settimane                                  │
│  👥 Team: 2 persone                                         │
│  📈 Progress: 0% (0/12 steps)                              │
│                                                             │
│  FASE 1: Research & Analysis (Settimane 1-2) ⬜             │
│   Step 1.1: Analizza dati attivazione ⬜                    │
│   Step 1.2: User research su pain points ⬜                 │
│                                                             │
│  FASE 2: Design (Settimane 3-5) ⬜                          │
│   Step 2.1: Progetta tutorial interattivi ⬜                │
│   Step 2.2: Prototipi clickable ⬜                          │
│   Step 2.3: User testing prototipi ⬜                       │
│                                                             │
│  FASE 3: Implementation (Settimane 6-9) ⬜                  │
│   [... 4 steps ...]                                         │
│                                                             │
│  FASE 4: Testing & Launch (Settimane 10-12) ⬜              │
│   [... 3 steps ...]                                         │
│                                                             │
│  [View Full Plan] [Export Markdown]                        │
│                                                             │
│  Vuoi esplorare uno step o iniziare con il primo?"         │
└─────────────────────────────────────────────────────────────┘
              ↓ User: "Dimmi di più sullo Step 1.1"
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: INTERACTIVE EXECUTION COACHING                     │
├─────────────────────────────────────────────────────────────┤
│ Genius: "📌 STEP 1.1: Analizza dati attivazione            │
│                                                             │
│  🎯 Obiettivo:                                              │
│  Identificare 3 core features e misurare baseline.         │
│                                                             │
│  📋 Tasks:                                                  │
│  1. Identifica le 3 core features (da belief B15)          │
│  2. Misura tempo medio attivazione per feature             │
│  3. Calcola % utenti che attivano ≥1 feature               │
│  4. Stabilisci baseline conversion (attuale: 40% da B12)   │
│                                                             │
│  🔗 Beliefs rilevanti:                                      │
│  • B12 (CRITICO): Trial conversion 40%, 60% churn          │
│  • B15 (ALTO): 3 core features entro 48h per retention     │
│                                                             │
│  ✅ Criteri completamento:                                 │
│  • Report metriche attuali completato                      │
│  • 3 core features identificate e documentate              │
│  • Baseline attivazione misurato per ogni feature          │
│                                                             │
│  ⏱️ Effort: 3 giorni | 👤 Chi: Product Manager (tu)        │
│                                                             │
│  💡 Suggerimenti:                                           │
│  - Usa Google Analytics/Mixpanel                           │
│  - 'Activation' = uso effettivo, non solo view             │
│                                                             │
│  Domande? Posso aiutarti con:                              │
│  • Come identificare core features?                        │
│  • Come impostare tracking?                                │
│  • Template per report?                                    │
│  • Altro..."                                                │
│                                                             │
│ User: "Come identifico le core features?"                  │
│                                                             │
│ Genius: [Provides detailed guidance...]                    │
│                                                             │
│ [Mark as In Progress] [Mark as Completed] [Skip]           │
└─────────────────────────────────────────────────────────────┘
              ↓ User marks step completed
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: PROGRESS TRACKING & CONTINUATION                   │
├─────────────────────────────────────────────────────────────┤
│ Genius: "🎉 Step 1.1 completato!                           │
│                                                             │
│  Vuoi aggiungere note su cosa hai scoperto?                │
│  (Aiuta ad adattare i prossimi step)"                      │
│                                                             │
│ User: "Ho identificato: Dashboard, Reports, Integrations"  │
│                                                             │
│ Genius: "Perfetto! Salvato. 📝                             │
│                                                             │
│  📊 PROGRESS UPDATE:                                        │
│  • Fase 1: Research & Analysis                             │
│    └─ Step 1.1 ✅ COMPLETATO                               │
│    └─ Step 1.2 ⬜ PROSSIMO                                  │
│  • Overall: 8% (1/12 steps)                                │
│                                                             │
│  Procediamo con Step 1.2 (User research)?"                 │
│                                                             │
│ [Continue to Next Step] [Review Plan] [Export] [Pause]     │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Model

### BDI Framework File Format

**Location**: `data/bdi_frameworks/{domain}.json`

**Format**: Standard `current_bdi.json` schema

```json
{
  "domain_summary": "Brief description of the domain",
  "beneficiario": {
    "beneficiario_name": "Primary stakeholder",
    "beneficiario_description": "Role/context",
    "beneficiario_inference_notes": ["Signal 1", "Signal 2"]
  },
  "desires": [
    {
      "desire_id": "D1",
      "desire_statement": "Clear, actionable goal",
      "priority": "high|medium|low",
      "success_metrics": ["Metric 1", "Metric 2"],
      "context": "Additional context",
      "motivation": "Why this matters"
    }
  ],
  "beliefs": [
    {
      "subject": "Main entity/concept",
      "definition": "Complete description (WHAT, WHY, HOW)",
      "semantic_relations": [
        {
          "relation": "relationship_type",
          "object": "Related entity",
          "description": "Explanation"
        }
      ],
      "source": "Citation",
      "importance": 0.85,
      "confidence": 0.9,
      "prerequisites": ["Prereq 1"],
      "related_concepts": ["Concept 1"],
      "enables": ["What this enables"],
      "tags": ["tag1", "tag2"],
      "related_desires": [
        {
          "desire_id": "D1",
          "relevance_level": "CRITICO|ALTO|MEDIO|BASSO",
          "definition": "Why relevant"
        }
      ]
    }
  ],
  "intentions": []
}
```

### User Profile

**Generated in Phase 1 (Context Gathering)**

```json
{
  "profile_id": "uuid",
  "bdi_source": "ecommerce_retention.json",
  "target_desire": "D2",
  "user_context": {
    "role": "Product Manager",
    "timeline_weeks": 12,
    "current_situation": "basic_onboarding_exists",
    "constraints": ["small_team", "limited_budget"],
    "skill_level": "intermediate",
    "additional_notes": "Team: PM + 1 developer"
  },
  "created_at": "2026-01-10T15:00:00Z"
}
```

### Action Plan

**Location**: `data/sessions/{session_id}/genius_plans/plan_{plan_id}.json`

```json
{
  "plan_id": "uuid-plan-1",
  "session_id": "uuid-session-a",
  "bdi_source": "ecommerce_retention.json",
  "created_at": "2026-01-10T15:00:00Z",
  "last_updated": "2026-01-10T16:30:00Z",

  "target_desire": {
    "desire_id": "D2",
    "desire_statement": "Implementare onboarding in-app interattivo",
    "priority": "medium",
    "success_metrics": [
      "Attivazione 3 core features entro 48h",
      "Conversion rate ≥60%"
    ]
  },

  "user_profile": {
    "role": "Product Manager",
    "timeline_weeks": 12,
    "current_situation": "basic_onboarding_exists",
    "constraints": ["small_team", "limited_budget"],
    "skill_level": "intermediate"
  },

  "plan_structure": {
    "total_phases": 4,
    "total_steps": 12,
    "estimated_duration_weeks": 12,

    "phases": [
      {
        "phase_id": "P1",
        "phase_name": "Research & Analysis",
        "phase_order": 1,
        "duration_weeks": 2,
        "status": "in_progress",
        "started_at": "2026-01-10T15:00:00Z",
        "completed_at": null,

        "steps": [
          {
            "step_id": "S1.1",
            "step_order": 1,
            "description": "Analyze current activation data",

            "tasks": [
              "Identify 3 core features (from B15)",
              "Measure average activation time per feature",
              "Calculate % users activating ≥1 feature",
              "Establish baseline conversion (current: 40% from B12)"
            ],

            "supporting_beliefs": [
              {
                "belief_id": "B12",
                "subject": "Trial Conversion Rate",
                "relevance_level": "CRITICO",
                "why_relevant": "Provides baseline metric to improve"
              },
              {
                "belief_id": "B15",
                "subject": "Core Feature Activation",
                "relevance_level": "ALTO",
                "why_relevant": "Defines what to measure (3 core features)"
              }
            ],

            "verification_criteria": [
              "Metrics report completed",
              "3 core features identified and documented",
              "Baseline activation measured for each feature"
            ],

            "estimated_effort_days": 3,
            "assigned_to": "Product Manager",

            "status": "completed",
            "started_at": "2026-01-10T15:00:00Z",
            "completed_at": "2026-01-11T10:00:00Z",

            "user_notes": "Identified features: Dashboard, Reports, Integrations. Current activation: Dashboard 60%, Reports 30%, Integrations 15%",

            "practical_tips": [
              "Use Google Analytics or Mixpanel for tracking",
              "Consider 'activation' = actual usage, not just page view",
              "If no tracking exists, implement it now for baseline"
            ]
          },

          {
            "step_id": "S1.2",
            "step_order": 2,
            "description": "Conduct user research on pain points",

            "tasks": [
              "Interview 10-15 trial users who didn't convert",
              "Identify blockers preventing feature activation",
              "Map pain points to the 3 core features"
            ],

            "supporting_beliefs": [
              {
                "belief_id": "B12",
                "subject": "Trial Conversion Rate",
                "relevance_level": "CRITICO",
                "why_relevant": "60% churn → need to understand why"
              }
            ],

            "verification_criteria": [
              "10+ interviews completed",
              "Pain points documented and categorized",
              "Insights mapped to core features from S1.1"
            ],

            "estimated_effort_days": 5,
            "assigned_to": "Product Manager",

            "status": "in_progress",
            "started_at": "2026-01-11T11:00:00Z",
            "completed_at": null,

            "user_notes": "Completed 7/10 interviews. Common theme: confusion on how to start with Integrations.",

            "practical_tips": [
              "Recruit users who churned post-trial (60% from B12)",
              "Offer incentive (e.g., 20% discount) for participation",
              "Ask: 'What prevented you from activating [feature]?'",
              "Template for interviews available on request"
            ]
          }
        ]
      },

      {
        "phase_id": "P2",
        "phase_name": "Design",
        "phase_order": 2,
        "duration_weeks": 3,
        "status": "pending",
        "started_at": null,
        "completed_at": null,

        "steps": [
          {
            "step_id": "S2.1",
            "step_order": 3,
            "description": "Design interactive tutorials for core features",
            "tasks": [...],
            "supporting_beliefs": [...],
            "verification_criteria": [...],
            "estimated_effort_days": 7,
            "status": "pending",
            "user_notes": "",
            "practical_tips": [...]
          }
          // ... more steps
        ]
      }

      // ... more phases
    ]
  },

  "relevant_beliefs_summary": [
    {
      "belief_id": "B12",
      "subject": "Trial Conversion Rate",
      "definition": "Current trial-to-paid conversion is 40%, with 60% churn post-trial",
      "relevance_level": "CRITICO",
      "used_in_steps": ["S1.1", "S1.2", "S3.1"],
      "source": "analytics_dashboard.pdf, page 3"
    },
    {
      "belief_id": "B15",
      "subject": "Core Feature Activation",
      "definition": "Users need to activate 3 core features within 48h for optimal retention",
      "relevance_level": "ALTO",
      "used_in_steps": ["S1.1", "S2.1", "S3.1"],
      "source": "user_research_report.pdf, page 12"
    }
    // ... more beliefs
  ],

  "overall_progress": {
    "total_steps": 12,
    "completed_steps": 1,
    "in_progress_steps": 1,
    "pending_steps": 10,
    "percentage_complete": 8.33,
    "current_phase": "P1",
    "current_step": "S1.2"
  },

  "metadata": {
    "llm_provider": "Gemini",
    "llm_model": "gemini-2.5-flash",
    "generation_method": "hybrid",
    "refinement_iterations": 2
  }
}
```

### Active Plan Tracking

**File**: `data/sessions/{session_id}/genius_plans/.active_plan`

```json
{
  "active_plan_id": "uuid-plan-1",
  "set_at": "2026-01-10T15:00:00Z"
}
```

**Note**: Only ONE plan can be active at a time per session.

---

## UI Specifications

### Layout: Hybrid Approach

```
┌────────────────────────────────────────────────────────────────┐
│ SIDEBAR (270px width)                                          │
├────────────────────────────────────────────────────────────────┤
│ ✨ LumIA Studio                                    [🏠]        │
│ ──────────────────────────────────────────────────────────────┘
│                                                                 │
│ 📍 Sessione Attiva: Product Retention 2026                    │
│ 🗂️ Context: ecommerce_knowledge                               │
│ [🧭 Vai a Compass]                                             │
│                                                                 │
│ ─────────────────────────                                      │
│ ⚙️ CONFIGURAZIONE GENIUS                                       │
│ ──────────────────                                             │
│ Provider LLM:  [Gemini ▼]  Modello: [2.5 Flash ▼]             │
│                                                                 │
│ 🔧 Impostazioni Avanzate:                                      │
│   Temperature:     [████████░░] 0.7                            │
│   Max Tokens:      2000                                        │
│   Top P:           [████████░░] 0.9                            │
│                                                                 │
│ ─────────────────────────                                      │
│ 📊 CURRENT PLAN                                                │
│ ──────────────────                                             │
│ BDI: E-commerce Retention                                      │
│ Desire: D2 - Onboarding                                        │
│ Progress: 8% (1/12 steps)                                      │
│                                                                 │
│ ✅ Phase 1: Research (1/2)                                     │
│    ✅ Step 1.1 - Analyze data                                  │
│    🔵 Step 1.2 - User research ← Current                       │
│                                                                 │
│ ⬜ Phase 2: Design (0/3)                                       │
│    ⬜ Step 2.1 - Design tutorials                              │
│    ⬜ Step 2.2 - Prototypes                                    │
│    ⬜ Step 2.3 - User testing                                  │
│                                                                 │
│ ⬜ Phase 3: Implementation (0/4)                               │
│    [Collapsed - click to expand]                               │
│                                                                 │
│ ⬜ Phase 4: Testing & Launch (0/3)                             │
│    [Collapsed - click to expand]                               │
│                                                                 │
│ ─────────────────────────                                      │
│ [📄 View Full Plan Details]                                    │
│ [💾 Export Markdown]                                           │
│ [🔄 New Plan]                                                  │
│                                                                 │
│ ─────────────────────────                                      │
│ RELEVANT BELIEFS (5)                                           │
│ 🔴 B12: Trial conversion                                       │
│ 🟡 B15: Core features                                          │
│ 🟡 B23: Interactive tutorials                                  │
│ 🟢 B7: Onboarding best practices                               │
│ 🟢 B31: User activation metrics                                │
│ [Show All]                                                     │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ MAIN AREA (rest of screen width)                              │
├────────────────────────────────────────────────────────────────┤
│ ⚡ GENIUS - Your BDI Execution Coach                          │
│ ──────────────────────────────────────────────────────────────┘
│                                                                 │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ CHAT AREA (scrollable)                                    │  │
│ │                                                           │  │
│ │ [Genius avatar] Genius:                                   │  │
│ │ "Ho caricato il BDI 'E-commerce Retention'. Vedo 5        │  │
│ │  desires definiti..."                                     │  │
│ │                                                           │  │
│ │ [User avatar] You:                                        │  │
│ │ "Voglio lavorare su D2"                                   │  │
│ │                                                           │  │
│ │ [Genius avatar] Genius:                                   │  │
│ │ "Perfetto! Lavoreremo su: D2 - Implementare onboarding   │  │
│ │  in-app interattivo..."                                   │  │
│ │                                                           │  │
│ │ [Interactive cards, buttons, forms as needed]            │  │
│ │                                                           │  │
│ └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│ [💬 Chat Input Box - full width]                              │
│ [Send Button]                                                  │
│                                                                 │
│ Quick Actions:                                                 │
│ [⏭️ Next Step] [📋 Review Current] [❓ Ask Question]          │
│ [📊 View Plan] [✅ Mark Complete]                             │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### Visual Design Specifications

**Color Scheme:**

- ✅ Completed: Green (#28a745)
- 🔵 In Progress: Blue (#007bff)
- ⬜ Pending: Gray (#6c757d)
- 🔴 CRITICO belief: Red dot
- 🟡 ALTO belief: Yellow dot
- 🟢 MEDIO belief: Green dot
- 🔵 BASSO belief: Blue dot

**Progress Bar:**

- Linear progress bar at top of sidebar
- Shows percentage complete (0-100%)
- Color gradient: Red (0%) → Yellow (50%) → Green (100%)

**Step Status Icons:**

- ✅ Completed
- 🔵 In Progress (pulsing animation)
- ⬜ Pending (grayed out)

**Interactive Elements:**

- Click on step in sidebar → Jump to that step in chat
- Click on belief → Show full belief details in modal
- Click on phase → Expand/collapse steps

### Component Details

#### BDI Selection Cards

```
┌─────────────────────────────────────────────────────────┐
│ 🎯 E-commerce Retention Strategy                        │
├─────────────────────────────────────────────────────────┤
│ Domain: E-commerce                                      │
│ Desires: 5 | Beliefs: 23                                │
│ Tags: retention, e-commerce, 2026-Q1                    │
│                                                         │
│ Created: 2026-01-05                                     │
│ Last modified: 2026-01-08                               │
│                                                         │
│ [Select This BDI →]                                     │
└─────────────────────────────────────────────────────────┘
```

#### Step Detail Card (in chat)

```
┌──────────────────────────────────────────────────────────┐
│ 📌 STEP 1.1: Analyze current activation data            │
├──────────────────────────────────────────────────────────┤
│ 🎯 Obiettivo:                                            │
│ Identificare le 3 core features e stabilire baseline    │
│ di attivazione.                                          │
│                                                          │
│ 📋 Tasks (4):                                            │
│  1. Identify 3 core features (from B15)                 │
│  2. Measure avg activation time per feature             │
│  3. Calculate % users activating ≥1 feature             │
│  4. Establish baseline conversion (current: 40%, B12)   │
│                                                          │
│ 🔗 Beliefs (2):                                          │
│  🔴 B12 (CRITICO): Trial conversion 40%, 60% churn      │
│  🟡 B15 (ALTO): 3 core features within 48h              │
│  [View Full Beliefs]                                    │
│                                                          │
│ ✅ Criteri di completamento:                            │
│  • Metrics report completed                             │
│  • 3 core features identified and documented            │
│  • Baseline measured for each feature                   │
│                                                          │
│ ⏱️ Effort: 3 giorni | 👤 Chi: Product Manager           │
│                                                          │
│ 💡 Suggerimenti pratici (3):                            │
│  • Use Google Analytics/Mixpanel                        │
│  • 'Activation' = actual usage, not views               │
│  • Implement tracking if doesn't exist                  │
│  [Show More]                                            │
│                                                          │
│ Status: ⬜ Pending                                       │
│ [▶️ Start Step] [❓ Ask Question] [⏭️ Skip]              │
└──────────────────────────────────────────────────────────┘
```

#### Progress Update Card

```
┌──────────────────────────────────────────────────────────┐
│ 🎉 Step 1.1 Completato!                                 │
├──────────────────────────────────────────────────────────┤
│ Vuoi aggiungere note su cosa hai scoperto?              │
│ (Aiuta Genius ad adattare i prossimi step)              │
│                                                          │
│ [Text area for user notes]                              │
│                                                          │
│ [💾 Save Notes] [⏭️ Next Step] [Skip]                   │
│                                                          │
│ ─────────────────────────────────────────                │
│ 📊 PROGRESS UPDATE                                       │
│ Phase 1: Research & Analysis                            │
│  ├─ Step 1.1 ✅ COMPLETATO                              │
│  └─ Step 1.2 ⬜ PROSSIMO                                 │
│                                                          │
│ Overall: 8% completato (1/12 steps)                     │
│ [████░░░░░░░░░░░░░░░░░░░░░░░░░░] 8%                     │
└──────────────────────────────────────────────────────────┘
```

---

## LLM Strategy

### LLM Configuration

**Architecture**: Uses `LLMManager` class (consistent with other agents)

**Configuration Location**: Sidebar (independent from session)

**Default Behavior**:

```python
# Load defaults from active session
session_config = active_session_data['config']
default_provider = session_config.get('llm_provider', 'Gemini')
default_model = session_config.get('llm_model', 'gemini-2.5-flash')
default_settings = session_config.get('llm_settings', {
    'temperature': 0.7,
    'max_tokens': 2000,
    'top_p': 0.9
})
```

**User Override**: Sidebar selectboxes allow user to change provider/model for Genius independently

**LLM Manager Usage**:

```python
from utils.llm_manager import LLMManager

llm_manager = LLMManager()

# Make LLM call
response = llm_manager.chat(
    provider=selected_provider,  # From sidebar
    model=selected_model,        # From sidebar
    messages=[
        {"role": "system", "content": genius_system_prompt},
        {"role": "user", "content": user_message}
    ],
    settings={
        "temperature": temperature,    # From sidebar slider
        "max_tokens": max_tokens,      # From sidebar
        "top_p": top_p                # From sidebar slider
    }
)
```

**Recommended Settings per Phase**:

| Phase | Temperature | Max Tokens | Rationale |
|-------|-------------|------------|-----------|
| **Structure Generation** | 0.7 | 4000 | Balanced creativity for plan |
| **Detail Enrichment** | 0.6 | 1500 | More factual for tips |
| **Adaptive Coaching** | 0.5 | 1000 | Consistent, helpful answers |

### Hybrid Generation Approach

#### Phase 1: Structure Generation (Single-Shot)

**Purpose**: Generate complete plan structure in one LLM call

**Input:**

- Target desire (from BDI)
- User profile (role, timeline, constraints)
- Relevant beliefs (CRITICO + ALTO only)

**Prompt Template:**

```
You are Genius, an execution coach specializing in BDI frameworks.

USER PROFILE:
- Role: {role}
- Timeline: {timeline_weeks} weeks
- Current Situation: {current_situation}
- Constraints: {constraints}
- Skill Level: {skill_level}

TARGET DESIRE:
{desire_id}: {desire_statement}
Priority: {priority}
Success Metrics: {success_metrics}

RELEVANT BELIEFS (CRITICO + ALTO):
{filtered_beliefs}

TASK:
Generate a complete action plan structure to achieve this desire.

OUTPUT FORMAT (JSON):
{
  "phases": [
    {
      "phase_id": "P1",
      "phase_name": "Phase name",
      "duration_weeks": 2,
      "steps": [
        {
          "step_id": "S1.1",
          "description": "Step description",
          "tasks": ["Task 1", "Task 2"],
          "supporting_beliefs": ["B12", "B15"],
          "verification_criteria": ["Criterion 1"],
          "estimated_effort_days": 3,
          "assigned_to": "Role"
        }
      ]
    }
  ]
}

GUIDELINES:
- Total timeline must fit within {timeline_weeks} weeks
- Account for constraints: {constraints}
- Each step must reference supporting beliefs
- Tasks should be actionable for {role}
- Include verification criteria for each step
```

**LLM Settings:**

```python
{
    "temperature": 0.7,  # Balanced creativity
    "max_tokens": 4000,  # Long output for full plan
    "top_p": 0.9
}
```

#### Phase 2: Detail Enrichment (Iterative)

**Purpose**: Add practical tips, examples, and refinements phase-by-phase

**Trigger**: User asks for details on a specific step OR plan generation complete

**Input:**

- Generated step structure
- Relevant beliefs for that step
- User profile

**Prompt Template:**

```
Enrich the following step with practical tips and detailed guidance.

STEP:
{step_json}

SUPPORTING BELIEFS:
{beliefs_for_step}

USER CONTEXT:
Role: {role}
Constraints: {constraints}

ADD:
1. Practical tips (3-5 actionable suggestions)
2. Common pitfalls to avoid
3. Tools/resources recommendations
4. Estimated time breakdown for tasks

Keep language practical and domain-specific.
```

**LLM Settings:**

```python
{
    "temperature": 0.6,  # Slightly lower for factual tips
    "max_tokens": 1500,
    "top_p": 0.9
}
```

#### Phase 3: Adaptive Coaching (Conversational)

**Purpose**: Answer user questions during execution

**Trigger**: User asks a question in chat

**Input:**

- User question
- Current step context
- Relevant beliefs
- User notes from previous steps

**Prompt Template:**

```
You are coaching the user on executing this step.

CURRENT STEP:
{current_step_json}

USER PROGRESS SO FAR:
{user_notes_from_previous_steps}

RELEVANT BELIEFS:
{beliefs}

USER QUESTION:
{user_question}

Provide a helpful, practical answer. Reference beliefs when relevant.
Use domain-specific terminology from the beliefs.
Keep answers concise (2-3 paragraphs).
```

**LLM Settings:**

```python
{
    "temperature": 0.5,  # Lower for consistent coaching
    "max_tokens": 1000,
    "top_p": 0.9
}
```

### Specialized Prompt Generation

**Key Innovation**: Generate domain-specific system prompt from BDI

**Process:**

1. Extract domain terminology from belief subjects
2. Identify common patterns in belief relations
3. Extract stakeholder language from beneficiario
4. Create custom system instruction

**Example:**

**Input BDI** (E-commerce domain):

```json
{
  "domain_summary": "E-commerce retention strategy",
  "beneficiario": {
    "beneficiario_name": "Product Manager",
    "beneficiario_description": "SaaS platform owner"
  },
  "beliefs": [
    {"subject": "Trial Conversion Rate", ...},
    {"subject": "Core Feature Activation", ...},
    {"subject": "Customer Lifetime Value", ...}
  ]
}
```

**Generated Specialized Prompt:**

```
You are Genius, a Product Management Coach specializing in SaaS retention and onboarding.

DOMAIN EXPERTISE:
You are an expert in:
- Trial conversion optimization
- Feature activation strategies
- Customer retention metrics
- SaaS onboarding best practices

TERMINOLOGY:
When communicating with the user, use these domain-specific terms:
- Trial Conversion Rate: Percentage of trial users converting to paid
- Core Feature Activation: Users activating key features within 48h
- Customer Lifetime Value: Total revenue per customer relationship
- Churn Rate: Percentage of customers who stop using the product

YOUR COACHING STYLE:
- Speak the language of Product Managers (metrics, KPIs, user research)
- Reference concrete data points (e.g., "current 40% conversion" from beliefs)
- Provide actionable steps suitable for PM skill set
- Focus on measurable outcomes and success criteria

[Continue with standard coaching instructions...]
```

---

## Implementation Plan

### Phase 1: Foundation (Week 1)

**Tasks:**

1. Create file structure
   - `data/bdi_frameworks/` directory
   - Example BDI files for testing

2. Build `GeniusEngine` class (`utils/genius_engine.py`)
   - `load_bdi_frameworks()` - List available BDI files
   - `load_bdi(filename)` - Load specific BDI
   - `filter_beliefs(desire_id, min_level="ALTO")` - Get relevant beliefs
   - `create_user_profile(inputs)` - Generate profile from chat
   - `generate_plan_structure(profile, desire, beliefs)` - LLM call for plan
   - `save_plan(plan)` - Persist to session
   - `load_active_plan(session_id)` - Resume plan

3. System prompts
   - `prompts/genius_discovery_prompt.md` - Phase 1 (BDI/Desire customization)
   - `prompts/genius_coach_template.md` - Phase 2 (Specialized coaching)

**Deliverables:**

- Working `GeniusEngine` with core methods
- System prompts tested with LLM
- Example BDI framework in `bdi_frameworks/`

### Phase 2: UI Implementation (Week 2)

**Tasks:**

1. Update `pages/6_Genius.py`
   - BDI selection UI (cards)
   - Desire customization (conversational)
   - User context gathering (chat)
   - Plan display (hybrid layout)

2. Sidebar component
   - Progress overview
   - Phase/step tree view
   - Relevant beliefs list
   - Quick action buttons

3. Chat components
   - Step detail cards
   - Progress update cards
   - Belief detail modals

**Deliverables:**

- Functional Genius page
- Complete user flow from BDI selection to plan generation
- Interactive step navigation

### Phase 3: Execution Support (Week 3)

**Tasks:**

1. Interactive coaching
   - Q&A on steps
   - Step detail expansion
   - Mark step as complete
   - User notes capture

2. Progress tracking
   - Update step status
   - Calculate overall progress
   - Persist changes to plan file

3. Export functionality
   - Generate Markdown from plan
   - Download file
   - Include progress indicators

**Deliverables:**

- Complete execution coaching flow
- Working progress tracking
- Markdown export

### Phase 4: Testing & Refinement (Week 4)

**Tasks:**

1. Create test BDI frameworks (3 different domains)
2. End-to-end testing
3. Prompt optimization
4. UI/UX refinements
5. Documentation updates

**Deliverables:**

- Tested system with multiple domains
- Updated README.md
- This requirements doc finalized

---

## Technical Decisions

### Decision 1: BDI Source Location

**Decision**: Separate `data/bdi_frameworks/` directory (not in sessions)

**Rationale:**

- BDI frameworks are reusable across multiple users
- Separation of concerns: BDI = knowledge, Session = workspace
- User manually curates BDI files (admin-level control)
- Can be version-controlled independently

**Implications:**

- Genius doesn't modify BDI files (read-only)
- Plans reference BDI by filename (not by session)
- BDI updates don't affect existing plans

### Decision 2: Single Active Plan

**Decision**: Only ONE active plan per session at a time

**Rationale:**

- Simplifies UX (less cognitive load)
- Easier to track progress (single focus)
- Prevents plan fragmentation
- Most users work on one goal at a time

**Implications:**

- `.active_plan` file contains single plan ID
- Starting new plan deactivates previous one
- Historical plans still saved (can resume later)
- UI shows clear "current plan" indicator

### Decision 3: Hybrid LLM Strategy

**Decision**: Generate structure (single-shot) + Refine phase-by-phase (iterative)

**Rationale:**

- Balance between quality and latency
- Structure generation needs full context (one call)
- Details can be added lazily (on-demand)
- Reduces initial wait time for user

**Implications:**

- Initial plan shows structure (phases, steps, beliefs)
- Practical tips generated when user explores step
- Allows adaptive refinement based on user progress
- Two-tier prompt system

### Decision 4: Markdown Export Only (MVP)

**Decision**: Export to Markdown only (not PDF, not JSON raw)

**Rationale:**

- Markdown is human-readable
- Easy to edit in any text editor
- Can be converted to PDF/HTML later (Pandoc)
- Smaller implementation scope for MVP
- JSON is too technical for end-users

**Implications:**

- Export button generates `.md` file
- Includes progress indicators (✅, ⬜)
- Formatted for readability
- Can add PDF export post-MVP

### Decision 5: Chat-Based Desire Customization

**Decision**: Conversational desire customization (not dropdown/form)

**Rationale:**

- Aligns with "coach" persona (not a form-filling tool)
- Allows Genius to explain each desire
- User can ask questions about desires
- More engaging UX

**Implications:**

- Genius lists desires in chat message
- User responds in natural language ("I want D2" or "onboarding")
- LLM interprets user selection
- Fallback: If ambiguous, Genius asks for clarification

### Decision 8: LLM Configuration per Agent (Not Session)

**Decision**: Genius has its own LLM configuration in sidebar (independent from session)

**Rationale:**

- Consistent with other agents (Alì, Believer, Cuma)
- User may want different models for different tasks (e.g., faster model for coaching, smarter for planning)
- Session config provides default, but sidebar allows override
- Flexibility without changing session configuration

**Implications:**

- Sidebar has provider + model selectbox
- Default values loaded from active session config
- User can override for current Genius usage
- Uses `LLMManager` class for all LLM interactions
- LLM settings (temperature, max_tokens) also configurable in sidebar

### Decision 6: Belief Filtering Strategy

**Decision**: Only include CRITICO + ALTO beliefs in plan generation

**Rationale:**

- Reduces token usage (shorter prompts)
- Focuses on high-impact beliefs
- MEDIO/BASSO beliefs are supplementary (not essential)
- Avoids overwhelming user with too many references

**Implications:**

- Plan generation prompt includes filtered beliefs
- MEDIO/BASSO beliefs still accessible (in sidebar, on request)
- User can explore full belief base separately
- Clear labeling (🔴 CRITICO, 🟡 ALTO)

### Decision 7: Progress Tracking Granularity

**Decision**: Step-level tracking (pending | in_progress | completed)

**Rationale:**

- Sufficient granularity for most use cases
- Simple to implement and visualize
- Clear semantics (user understands state)
- Avoids over-engineering (no sub-task tracking for MVP)

**Implications:**

- No task-level checkboxes (tasks are guidance, not trackable)
- User marks entire step complete (not individual tasks)
- Progress calculated as: completed_steps / total_steps
- Can add finer tracking post-MVP if needed

---

## MVP Scope Summary

### In Scope

✅ **Core Features:**

- BDI selection from `data/bdi_frameworks/`
- Conversational desire customization
- User profile creation (role, timeline, constraints)
- Specialized prompt generation from BDI
- Action plan generation (hybrid: structure + refinement)
- Interactive Q&A on steps
- Progress tracking (step-level status)
- Plan persistence & resume
- Markdown export

✅ **UI Components:**

- Hybrid layout (sidebar + main chat)
- BDI selection cards
- Step detail cards
- Progress indicators
- Belief reference display
- Quick action buttons

✅ **LLM Integration:**

- Multi-phase prompt strategy
- Domain-specific terminology extraction
- Adaptive coaching responses

### Out of Scope (Post-MVP)

❌ **Features to add later:**

- PDF export
- Gantt chart visualization
- Task-level tracking (sub-tasks)
- Multi-plan support (work on multiple desires simultaneously)
- Integration with Cuma (load intentions as plan starters)
- Collaborative features (share plans with team)
- Version history for plans
- Automated reminders/notifications
- Mobile app
- API for external integrations

---

## Implementation Decisions

### Resolved Questions

#### 1. BDI File Naming Convention

**Decision**: `{domain_name}_bdi.json`

**Examples**:

- `ecommerce_retention_bdi.json`
- `healthcare_optimization_bdi.json`
- `education_platform_bdi.json`

**Versioning**: User manages manually (e.g., `ecommerce_retention_v2_bdi.json` if needed)

**Rationale**:

- Clear suffix `_bdi` identifies file purpose
- Simple and predictable naming
- User controls versioning strategy

---

#### 2. Plan ID Generation

**Decision**: `plan_{desire_id}_{uuid_short}.json`

**Examples**:

- `plan_D2_550e8400.json`
- `plan_D1_a3f12bc4.json`

**Format**: UUID shortened to first 8 characters

**Rationale**:

- Human-readable (shows which desire)
- Still unique (UUID prevents collisions)
- Easy to identify in file explorer

---

#### 3. Error Handling

**Scenario 1: Malformed BDI file**

- **Action**: Show error message, skip file
- **UI**: "⚠️ File `{filename}` has invalid JSON format. Skipping."
- **Logging**: Log error details for debugging

**Scenario 2: No CRITICO/ALTO beliefs for desire**

- **Action**: Fallback to MEDIO beliefs
- **UI**: Warning message: "⚠️ No high-priority beliefs found for this desire. Using medium-priority beliefs."
- **Behavior**: Include MEDIO beliefs in plan generation

**Scenario 3: LLM API failure**

- **Action**: Manual retry with clear error message
- **UI**: "❌ LLM Error: {error_message}. [Retry] button available"
- **No automatic retry** (avoid costs)
- **No fallback model** (user chooses model explicitly)

**Rationale**:

- Graceful degradation
- Clear user feedback
- User maintains control

---

#### 4. Belief Display in Sidebar

**Decision**: Top 5 beliefs (collapsed by default) + "Show All" button

**Behavior**:

- Show 5 most relevant beliefs (sorted by relevance_level: CRITICO > ALTO > MEDIO)
- "Show All (15)" expandable button if more exist
- Click on belief → **Modal popup** with full details

**Modal Content**:

```
┌──────────────────────────────────────────┐
│ 🔴 B12: Trial Conversion Rate      [✕]  │
├──────────────────────────────────────────┤
│ Definition:                              │
│ The percentage of users who convert...   │
│                                          │
│ Relevance to D2: CRITICO                 │
│ "This is the exact metric D2 aims..."   │
│                                          │
│ Source: customer_analytics.pdf, page 5  │
│                                          │
│ Related Concepts:                        │
│ • Churn rate                             │
│ • Activation rate                        │
│                                          │
│ Used in Steps: S1.1, S1.2, S3.1          │
│                                          │
│ [Close]                                  │
└──────────────────────────────────────────┘
```

**Rationale**:

- Avoids sidebar clutter
- Modal provides full context without leaving page
- Sorted by priority ensures most important visible

---

#### 5. Step Navigation

**A. Can user skip steps?**

- **Decision**: No skip status
- **Available states**: `pending`, `in_progress`, `completed` only
- **Rationale**: Simplicity for MVP. User can mark completed if they choose to skip.

**B. Can user reopen completed steps?**

- **Decision**: Yes, can change back to `in_progress`
- **Use case**: User wants to revise or add notes
- **UI**: Click on completed step → "Reopen this step?" confirmation

**C. What happens when user clicks previous step?**

- **Decision**: Chat scrolls to that step + allows Q&A
- **Behavior**:
  - Sidebar highlights selected step
  - Chat shows step detail card
  - User can ask questions about that step
  - Status doesn't change automatically (user must explicitly update)

**Rationale**:

- Flexibility to review and revise
- Non-destructive navigation
- User maintains control of progress

---

#### 6. User Notes

**A. Max length**

- **Decision**: 2000 characters
- **UI**: Character counter: "1523 / 2000"
- **Rationale**: Allows detailed notes without unlimited growth

**B. Format**

- **Decision**: Plain text (textarea)
- **Rationale**: Simplicity for MVP. Markdown support can be added post-MVP.

**C. Influence on next steps**

- **Decision**: Yes, LLM reads previous notes
- **Implementation**: When generating tips for step N, include notes from steps 1 to N-1 in context
- **Example prompt addition**:

  ```
  USER PROGRESS NOTES FROM PREVIOUS STEPS:
  - Step 1.1: "Identified core features: Dashboard, Reports, Integrations"
  - Step 1.2: "User interviews revealed confusion on Integrations setup"

  Use these insights to tailor your guidance for the current step.
  ```

**Rationale**:

- Adaptive coaching based on actual user experience
- Notes become valuable context for personalization
- Encourages users to document learnings

---

#### 7. Other Decisions

**LLM Model Choice**: ✅ User selects via sidebar (Decision 8)

**Token Budget**: ✅ 4000 for structure generation (specified in LLM Strategy)

**Validation**: ✅ Yes, validate plan JSON schema before saving (best practice)

**Caching**:

- **Decision**: No caching for MVP
- **Behavior**: Always generate fresh plans
- **Rationale**:
  - User inputs vary (profile, constraints)
  - LLM responses improve over time (model updates)
  - Cache invalidation complexity not worth it for MVP
- **Post-MVP**: Can add caching with TTL (time-to-live)

---

## Success Criteria

### MVP Success Metrics

**Functional:**

- [ ] User can load a BDI from `bdi_frameworks/`
- [ ] User can select a desire conversationally
- [ ] System generates complete plan in <30 seconds
- [ ] Plan includes all required fields (phases, steps, beliefs)
- [ ] User can navigate steps via sidebar
- [ ] User can mark steps as completed
- [ ] Progress is tracked and displayed correctly
- [ ] Plan persists across sessions (can resume)
- [ ] Markdown export generates valid, readable output

**Quality:**

- [ ] Generated plans are actionable (tasks are specific, not vague)
- [ ] Beliefs are correctly referenced in steps
- [ ] Timeline estimations are reasonable for user constraints
- [ ] Coaching Q&A provides helpful, relevant answers
- [ ] UI is responsive and intuitive

**Performance:**

- [ ] Page load time <3 seconds
- [ ] Plan generation time <30 seconds
- [ ] Chat response time <5 seconds
- [ ] Export generation time <2 seconds

---

## Appendix

### Example BDI for Testing

**File**: `data/bdi_frameworks/ecommerce_retention.json`

```json
{
  "domain_summary": "E-commerce SaaS platform focused on improving trial conversion and customer retention",
  "beneficiario": {
    "beneficiario_name": "Product Manager",
    "beneficiario_description": "Responsible for user onboarding and retention metrics in a SaaS e-commerce platform",
    "beneficiario_inference_notes": [
      "Mentioned specific retention KPIs (65% to 80%)",
      "Discussed product roadmap decisions",
      "Focused on post-trial conversion challenges"
    ]
  },
  "desires": [
    {
      "desire_id": "D1",
      "desire_statement": "Increase customer retention rate from 65% to 80% within 6 months",
      "priority": "high",
      "success_metrics": [
        "Retention rate ≥80%",
        "Churn rate <20%",
        "Repeat purchase rate >50%"
      ],
      "context": "Focus on post-purchase experience and customer success",
      "motivation": "High churn is impacting revenue growth and customer lifetime value"
    },
    {
      "desire_id": "D2",
      "desire_statement": "Implement in-app interactive onboarding to reduce time-to-value for trial users",
      "priority": "medium",
      "success_metrics": [
        "User activation within 48 hours of signup",
        "Feature adoption rate >60%",
        "Trial-to-paid conversion ≥60%"
      ],
      "context": "Current onboarding is email-based and passive, leading to low activation",
      "motivation": "Reduce 60% trial churn by helping users realize value faster"
    },
    {
      "desire_id": "D3",
      "desire_statement": "Reduce churn post-trial from 60% to below 30%",
      "priority": "high",
      "success_metrics": [
        "Post-trial churn <30%",
        "Conversion rate from trial to paid ≥70%"
      ],
      "context": "Most churn happens immediately after trial ends",
      "motivation": "Losing 60% of trial users is unsustainable for growth"
    }
  ],
  "beliefs": [
    {
      "subject": "Trial Conversion Rate",
      "definition": "The percentage of users who convert from free trial to paid subscription. Currently at 40%, meaning 60% of trial users churn without converting. This is a critical metric for SaaS growth.",
      "semantic_relations": [
        {
          "relation": "influenced_by",
          "object": "Onboarding quality",
          "description": "Better onboarding directly improves conversion"
        },
        {
          "relation": "measured_by",
          "object": "Analytics dashboard",
          "description": "Tracked via Mixpanel conversion funnel"
        }
      ],
      "source": "customer_analytics_2025.pdf, page 5",
      "importance": 0.95,
      "confidence": 0.98,
      "prerequisites": ["User signup", "Trial activation"],
      "related_concepts": ["Churn rate", "Activation rate"],
      "enables": ["Revenue forecasting", "Growth planning"],
      "tags": ["metrics", "conversion", "trial"],
      "related_desires": [
        {
          "desire_id": "D2",
          "relevance_level": "CRITICO",
          "definition": "This is the exact metric D2 aims to improve from 40% to ≥60%"
        },
        {
          "desire_id": "D3",
          "relevance_level": "CRITICO",
          "definition": "60% churn is the inverse of 40% conversion - directly targeted by D3"
        }
      ]
    },
    {
      "subject": "Core Feature Activation",
      "definition": "The process of users successfully activating and using the 3 core features of the platform within 48 hours of signup. Research shows users who activate these features have 3x higher retention. The 3 core features are: Dashboard, Reports, and Integrations.",
      "semantic_relations": [
        {
          "relation": "consists_of",
          "object": "Dashboard usage",
          "description": "First core feature users must activate"
        },
        {
          "relation": "consists_of",
          "object": "Reports generation",
          "description": "Second core feature"
        },
        {
          "relation": "consists_of",
          "object": "Integration setup",
          "description": "Third core feature, most complex"
        },
        {
          "relation": "leads_to",
          "object": "Higher retention",
          "description": "Activation correlates with 3x retention rate"
        }
      ],
      "source": "user_research_report.pdf, page 12",
      "importance": 0.9,
      "confidence": 0.92,
      "prerequisites": ["Account creation", "Email verification"],
      "related_concepts": ["Time-to-value", "Aha moment"],
      "enables": ["User retention", "Feature adoption"],
      "tags": ["activation", "onboarding", "features"],
      "related_desires": [
        {
          "desire_id": "D2",
          "relevance_level": "ALTO",
          "definition": "In-app onboarding should guide users to activate these 3 core features within 48h"
        },
        {
          "desire_id": "D1",
          "relevance_level": "ALTO",
          "definition": "Activating core features increases retention (relevant to D1's 80% target)"
        }
      ]
    },
    {
      "subject": "Interactive Tutorial Effectiveness",
      "definition": "Interactive tutorials (step-by-step guided walkthroughs with user interaction) increase feature adoption by 35% compared to passive documentation. They reduce time-to-first-value by 40%.",
      "semantic_relations": [
        {
          "relation": "increases",
          "object": "Feature adoption",
          "description": "+35% adoption rate vs passive docs"
        },
        {
          "relation": "reduces",
          "object": "Time-to-value",
          "description": "-40% time to first successful use"
        }
      ],
      "source": "onboarding_best_practices.pdf, page 8",
      "importance": 0.85,
      "confidence": 0.88,
      "prerequisites": ["In-app messaging capability"],
      "related_concepts": ["Product tours", "Contextual help"],
      "enables": ["Faster activation", "Better UX"],
      "tags": ["onboarding", "tutorials", "UX"],
      "related_desires": [
        {
          "desire_id": "D2",
          "relevance_level": "ALTO",
          "definition": "Interactive tutorials are the recommended implementation method for in-app onboarding"
        }
      ]
    }
  ],
  "intentions": []
}
```

---

**End of Document**
