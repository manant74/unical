# LUMIA Studio — User Manual

**Version 1.0 | March 2026**

---

## Table of Contents

1. [What is LUMIA Studio?](#1-what-is-lumia-studio)
2. [The BDI Framework: Core Concepts](#2-the-bdi-framework-core-concepts)
3. [Getting Started](#3-getting-started)
4. [The Complete Workflow](#4-the-complete-workflow)
5. [Module Reference](#5-module-reference)
   - [Knol — Knowledge Base](#knol--knowledge-base)
   - [Compass — Session Manager](#compass--session-manager)
   - [Alì — Desires Agent](#alì--desires-agent)
   - [Believer — Beliefs Agent](#believer--beliefs-agent)
   - [Cuma — Intentions Mapper](#cuma--intentions-mapper)
   - [Genius — Execution Coach](#genius--execution-coach)
6. [Managing Your Work](#6-managing-your-work)
7. [Tips for Best Results](#7-tips-for-best-results)
8. [Glossary](#8-glossary)

---

## 1. What is LUMIA Studio?

LUMIA Studio is an **AI-powered knowledge engineering platform** that helps domain experts transform documents and ideas into structured, actionable strategic plans.

Think of LUMIA as a team of specialized AI assistants, each with a distinct role, working together to help you:

- **Understand your domain** by learning from your documents
- **Clarify your goals** through structured conversation
- **Map your knowledge** to those goals
- **Explore strategic options** for achieving them
- **Execute with confidence** via a personalized action plan

LUMIA is designed for professionals who work with complex domains — product managers, consultants, researchers, strategists — and need to go from "I have a lot of information" to "I know exactly what to do and why."

---

## 2. The BDI Framework: Core Concepts

LUMIA is built on the **BDI (Beliefs, Desires, Intentions)** cognitive framework — a model borrowed from AI research that describes how rational agents make decisions.

In practical terms:

| Concept | What it means | Example |
|---------|--------------|---------|
| **Beliefs** | What you know about your domain | "Our customer churn rate is 18% in the first 30 days" |
| **Desires** | What you want to achieve | "Reduce first-month churn by 50%" |
| **Intentions** | How you plan to act | "Run a structured onboarding campaign targeting day 3, 7, and 14" |

The power of this framework is **traceability**: every plan is grounded in real knowledge, every action connects back to a stated goal.

### The BDI Pipeline

```
Documents → Beliefs → Desires → Intentions → Action Plan
    ↑                    ↑
  (Knol)              (Alì)
```

LUMIA guides you through building this chain step by step, with AI assistance at every stage.

---

## 3. Getting Started

### Prerequisites

Before using LUMIA Studio, you need:

- Access to the running LUMIA Studio application (provided by your administrator)
- At least one of: a Google API key (for Gemini models) or an OpenAI API key
- Some documents related to your domain (PDFs, web pages, or text files)

### Recommended First Steps

1. **Prepare your documents** — Gather PDFs, web links, or text documents that describe your domain. These could be research reports, product specs, user feedback, market analyses, etc.
2. **Open LUMIA Studio** — Navigate to the application URL in your browser
3. **Follow the workflow** shown on the home page:

```
📚 Knol → 🧭 Compass → 🎯 Alì → 💡 Believer → 🔮 Cuma → ⚡ Genius
```

> **Important**: The modules are designed to be used in order. Each builds on the output of the previous one.

---

## 4. The Complete Workflow

Here is a typical journey through LUMIA Studio from start to a finished action plan.

### Step 1 — Build Your Knowledge Base (Knol)

Upload your domain documents. LUMIA reads and indexes them so every AI conversation can draw from your actual information, not generic knowledge.

*Estimated time: 10–30 minutes depending on document volume*

### Step 2 — Configure Your Session (Compass)

Create a "session" — a named working space that ties together your knowledge base, your AI model preference, and all the outputs you'll generate.

*Estimated time: 2–5 minutes*

### Step 3 — Define Your Goals (Alì)

Have a conversation with Alì, LUMIA's desires specialist. Through guided dialogue, Alì helps you articulate what you truly want to achieve and who you're achieving it for.

*Estimated time: 20–45 minutes*

### Step 4 — Map Your Knowledge to Goals (Believer)

Work with Believer to connect your domain knowledge to your goals. The result is a structured map showing which facts and insights support (or challenge) each of your desires.

*Estimated time: 30–60 minutes*

### Step 5 — Explore Strategic Options (Cuma)

Cuma helps you think through multiple ways of achieving your goals. Instead of jumping to the first solution, you explore 3–5 different strategic scenarios.

*Estimated time: 20–40 minutes*

### Step 6 — Build and Execute Your Plan (Genius)

Genius takes everything you've built and turns it into a personalized, step-by-step action plan. You then track your progress directly in the platform.

*Estimated time: 15–20 minutes to generate; ongoing for execution*

---

## 5. Module Reference

---

### Knol — Knowledge Base

**The symbol:** 📚
**One line:** Upload and index your domain documents

#### What Knol does

Knol is your document library. It reads your files, extracts their content, and stores it in a searchable database that all other LUMIA agents can access. Every insight the AI generates will be grounded in what you've loaded here.

Knol also includes an AI-powered **Belief Extraction** feature: after loading documents, you can ask Knol to automatically identify the key facts and insights in your knowledge base.

#### How to use Knol

**1. Create or select a Context**

A *Context* is a named knowledge base. You might create separate contexts for different projects or domains (e.g., "E-commerce Platform", "Q4 Market Research").

- Click **New Context** and give it a name
- Or select an existing context from the dropdown

**2. Upload your documents**

Knol accepts three types of sources:

| Source Type | How to add | Best for |
|-------------|-----------|---------|
| **PDF files** | Click "Upload PDF" and select your files | Reports, papers, specs |
| **Web pages** | Paste a URL and click "Load URL" | Online articles, websites |
| **Text/Markdown** | Upload .txt or .md files | Notes, documentation |

After loading, you'll see a count of how many document chunks have been indexed.

**3. Extract beliefs (optional but recommended)**

Once documents are loaded, click **Extract Beliefs** to have the AI analyze your entire knowledge base and produce a structured list of key facts, concepts, and relationships.

You can review and edit these beliefs before proceeding. This gives you a head start in the Believer module.

**4. Check your stats**

The dashboard shows:
- Number of document chunks indexed
- Sources loaded
- Number of beliefs extracted

#### Tips for Knol

- **Quality over quantity**: A smaller set of highly relevant documents will produce better results than a large collection of loosely related material
- **Be specific**: Documents focused on your actual domain work better than broad references
- **Review extracted beliefs**: The AI extraction is good but not perfect — take a few minutes to review and remove any beliefs that seem off

---

### Compass — Session Manager

**The symbol:** 🧭
**One line:** Create and manage your working sessions

#### What Compass does

Compass is your control center. It lets you create "sessions" — named workspaces that hold all your configuration choices and link together your knowledge base, your goals, your beliefs, and your plans.

Think of a session as a project folder that LUMIA keeps organized for you.

#### How to use Compass

**1. Create a new session**

Click **New Session** and fill in:
- **Session name**: A meaningful name (e.g., "Customer Retention Q2 2026")
- **Description** (optional): A brief note about what you're working on
- **Context**: Select the knowledge base you created in Knol

**2. Configure your AI model**

Choose which AI model will power your conversations:
- **Provider**: Gemini (Google) or OpenAI
- **Model**: Select from available options (more capable models produce better results but may be slower)

**3. Activate the session**

Click **Activate** to make this your active session. All other modules will work within this session until you switch.

**4. Manage existing sessions**

The sidebar shows your recent sessions. You can:
- **Load** a previous session to continue your work
- **View** the BDI data (desires, beliefs, intentions) stored in any session
- **Export** a session as a ZIP file to share or back it up
- **Delete** sessions you no longer need

#### The BDI Editor

Compass includes a built-in JSON editor that lets you view and manually edit the raw BDI data for your session. This is for advanced users who want precise control over the structured output.

---

### Alì — Desires Agent

**The symbol:** 🎯
**One line:** Clarify what you want to achieve through guided conversation

#### What Alì does

Alì is a conversational AI specialist in goal discovery. Through a structured dialogue, Alì helps you:
- Articulate your goals clearly and precisely
- Identify the priorities behind each goal
- Define what success looks like (measurable outcomes)
- Understand *who* benefits from achieving these goals (the beneficiary)

Alì uses the Socratic method — asking questions to help you discover and clarify your own thinking, rather than telling you what your goals should be.

#### How a conversation with Alì works

**Opening**: Alì greets you and acknowledges your knowledge base. The first question is open: *"What do you want to accomplish?"*

**Exploration**: As you respond, Alì asks follow-up questions to clarify:
- The scope and context of your goal
- Why this matters to you and your organization
- What "done" looks like
- Who will benefit and how

**Beneficiary discovery**: Alì pays careful attention to understand who the end user or beneficiary of your work is. This is done through indirect questions rather than asking directly (a more natural and insightful approach).

**Formalization**: When the conversation has produced enough clarity, Alì formalizes your goals into structured *desires* — precise goal statements with priorities and success metrics.

#### Suggested replies

Throughout the conversation, you'll see quick-reply buttons at the bottom of the chat. These are AI-generated suggestions for how to continue the conversation productively. You can click one to send it, or type your own response freely.

#### The desires panel

On the right sidebar, you'll see the desires being built up as the conversation progresses. Each desire shows:
- **ID** (D1, D2, etc.)
- **Statement**: The goal in clear language
- **Priority**: High / Medium / Low
- **Success metrics**: How you'll know you've achieved it
- **Motivation**: Why this goal matters

You can also **add desires manually** using the form at the bottom of the sidebar — useful if you already know some of your goals clearly.

#### When to finish

Alì will signal when it has enough to formalize all your desires into structured output. You can also ask Alì directly: *"Can you now formalize the desires we've discussed?"*

---

### Believer — Beliefs Agent

**The symbol:** 💡
**One line:** Map your domain knowledge to your goals

#### What Believer does

Believer helps you build a structured map of your domain knowledge, connecting each fact and insight to the specific goals it supports (or challenges).

The result is a **belief map**: a list of key statements about your domain, each tagged with how critical it is to your desires.

This is the foundation of everything that follows. A solid belief map means your strategies and plans will be genuinely grounded in your domain, not generic best practices.

#### How a conversation with Believer works

**Starting point**: Believer loads your existing desires from the session. If you ran the Belief Extraction in Knol, those base beliefs are available to import.

**Conversation**: Believer guides a structured dialogue to:
- Review and refine the base beliefs (if loaded)
- Identify additional beliefs relevant to your goals
- Clarify the meaning and source of each belief
- Connect each belief to the specific desires it supports

**Relevance tagging**: For each belief, Believer assigns a relevance level to each desire:

| Level | Meaning |
|-------|---------|
| 🔴 **CRITICAL** | Essential — the plan cannot succeed without this knowledge |
| 🟡 **HIGH** | Strongly supports achieving the desire |
| 🟢 **MEDIUM** | Useful context and background |
| 🔵 **LOW** | Peripherally related |

**Finalization**: When you feel the belief map is complete, signal this to Believer (e.g., *"I think we've covered everything — can you generate the final beliefs?"*). Believer will then produce the structured output.

#### What a belief looks like

Each belief has:
- **Subject**: The entity or concept it's about (e.g., "Customer churn")
- **Definition**: What it means in your domain context
- **Source**: The exact document excerpt it came from
- **Importance**: How significant this knowledge is (0–1 scale)
- **Confidence**: How certain you are about this fact (0–1 scale)
- **Related desires**: Which goals this belief connects to, and how

#### Tips for working with Believer

- **Be precise**: Push for specific, atomic facts rather than broad generalizations
- **Source everything**: Believer will ask for the document evidence behind each belief
- **Don't skip relevance**: The connections between beliefs and desires are what make the later planning powerful
- **Challenge assumptions**: If something is marked as a belief but is actually an assumption, say so — Believer will adjust the confidence rating

---

### Cuma — Intentions Mapper

**The symbol:** 🔮
**One line:** Explore multiple strategic paths to your goals

#### What Cuma does

Cuma is a strategic scenario explorer. Rather than jumping to a single "right answer," Cuma helps you think through **3–5 different strategic approaches** to achieving your desires, each grounded in your belief map.

This module is about **breadth before depth**: opening up the solution space before committing to one path.

#### How a conversation with Cuma works

**Context loading**: Cuma automatically loads your desires and beliefs from the active session.

**Strategy generation**: Through conversation, Cuma proposes diverse strategic angles. These might include:
- Efficiency-focused approaches (do more with less)
- Innovation approaches (new ways of working)
- Risk mitigation approaches (reduce what could go wrong)
- Growth approaches (expand capabilities or reach)
- Collaborative approaches (work with others)

**Deep dive**: For any strategy you find interesting, Cuma generates a detailed action plan showing:
- The specific steps involved
- Which beliefs support this approach
- Expected outcomes
- Estimated effort

**Comparison**: By exploring multiple strategies, you develop a clearer picture of trade-offs and can make a more informed choice.

#### Saving intentions

When you've explored enough options, click **Complete Session** to save your intentions to the session BDI data. This makes them available to the Genius coach.

#### Note on work-in-progress

Cuma is an actively evolving module. Some features are still being refined. The core scenario exploration is fully functional.

---

### Genius — Execution Coach

**The symbol:** ⚡
**One line:** Turn your BDI framework into a personalized action plan

#### What Genius does

Genius is where strategy meets execution. It takes everything you've built in the previous modules — your knowledge, goals, and strategic intentions — and turns it into a **personalized, step-by-step action plan** tailored to your specific role, timeline, and constraints.

Then it stays with you as you execute, providing guidance and support for each step.

#### Phase 1: Select your BDI Framework

When you open Genius, you'll see a list of available BDI frameworks. These are the completed outputs from your Compass/Alì/Believer work.

Each framework shows:
- Number of desires
- Number of beliefs
- Creation date

Select the one you want to work with.

#### Phase 2: Discovery Conversation

Before generating a plan, Genius asks you a few questions to personalize it:

- **Which desire** do you want to focus on? (You can reference it by ID or describe it in your own words)
- **What is your role?** (e.g., Product Manager, Team Lead, Consultant)
- **What is your timeframe?** (e.g., "3 months", "next quarter")
- **What is your current situation?** (Where are you starting from?)
- **Any constraints?** (Team size, budget, technical limitations, etc.)

Genius asks one question at a time and works with natural, conversational answers.

#### Phase 3: Plan Generation

Based on your answers, Genius generates a comprehensive action plan organized into **phases → steps → tasks**.

Each step in the plan includes:
- **Description**: What to do and why
- **Concrete tasks**: Specific actions to take
- **Supporting beliefs**: Which knowledge from your belief map is relevant (with relevance indicators)
- **Verification criteria**: How to know this step is complete
- **Practical tips**: Specific, domain-grounded guidance
- **Effort estimate**: Expected time investment
- **Assigned role**: Who should do this

#### Phase 4: Execution Tracking

Once your plan is generated, you can track your progress directly in LUMIA:

- **Progress bar** at the top shows overall completion percentage
- **Step checkboxes** in the sidebar let you mark each step done
- **Step guidance** — click on any step to ask Genius for more detailed help
- **Q&A mode** — ask any question during execution and Genius will answer using your belief map

#### Additional features

**Add Tips and Tools**: Click this button to have Genius enrich your plan with practical tools, templates, and workflow suggestions for each step.

**Export plan**: Download your complete action plan as a Markdown file to share with your team or use in other tools.

**Load existing plans**: If you've previously generated plans, you can load and resume them from the session browser.

---

## 6. Managing Your Work

### Sessions

A **session** is your primary unit of work in LUMIA. It contains:
- Your AI model configuration
- Your linked knowledge base (context)
- All your desires, beliefs, and intentions
- Any plans generated by Genius

Sessions are automatically saved as you work. You can return to any session and continue from where you left off.

### Contexts (Knowledge Bases)

A **context** is a named collection of indexed documents. You can:
- Create multiple contexts for different domains or projects
- Reuse the same context across multiple sessions
- Export a context (as a ZIP file) to share or archive it

### Exporting and Sharing

From Compass, you can export a complete session as a ZIP file. This includes:
- All BDI data (desires, beliefs, intentions)
- Session metadata and configuration

You can also import sessions from ZIP files, making it easy to share work or restore archived sessions.

### Plans

Plans generated by Genius are saved automatically and can be:
- Resumed at any time
- Exported as Markdown files
- Tracked for progress

---

## 7. Tips for Best Results

### Document Quality

The quality of LUMIA's outputs depends heavily on the quality of your input documents.

- ✅ Use documents that are specific to your domain
- ✅ Include a mix of descriptive content (what things are) and analytical content (what they mean)
- ✅ More recent documents are generally better than outdated ones
- ❌ Avoid overly generic documents that could apply to any domain
- ❌ Very large documents with lots of irrelevant content can dilute quality

### Conversations

- **Be specific**: The more concrete your answers, the better the AI can help you
- **Correct freely**: If the AI misunderstands something, just correct it — *"No, what I mean is..."*
- **Use the suggested replies** as a starting point, but feel free to write your own
- **Go deep before moving on**: Don't rush to the next module; the quality of later stages depends on the depth you achieve in earlier ones

### BDI Framework Quality

- **Desires**: Aim for 3–7 well-defined desires. Too few may be too vague; too many may be unfocused.
- **Beliefs**: A strong belief map has 15–30 beliefs, each clearly connected to at least one desire
- **Intentions**: Explore at least 3 different strategic approaches before choosing which to pursue in Genius

### When to Use Genius

Genius works best when:
- You have at least 3 desires in your session
- Your belief map has at least 10 beliefs with desire connections
- You have a specific role and timeframe in mind

---

## 8. Glossary

**BDI (Beliefs, Desires, Intentions)**
The cognitive framework at the core of LUMIA. Beliefs represent knowledge, Desires represent goals, and Intentions represent plans.

**Belief**
A structured statement of fact or knowledge about your domain, sourced from your documents.

**Belief Map**
The complete set of beliefs in a session, with their connections to desires and relevance ratings.

**Beneficiary**
The person or group who benefits from achieving your desires. Alì helps identify this through conversation.

**Context**
A named knowledge base created in Knol. Contains your indexed documents.

**Desire**
A precisely stated goal with a priority level, success metrics, and motivation.

**Intention**
A strategic approach to achieving one or more desires, with an associated action plan.

**Plan**
A step-by-step personalized action plan generated by Genius for a specific desire, tailored to your role and constraints.

**RAG (Retrieval-Augmented Generation)**
The technique LUMIA uses to ground AI responses in your documents. When the AI answers a question, it searches your knowledge base for relevant content and incorporates it into its response.

**Session**
A named workspace in LUMIA that holds your configuration, knowledge base selection, and all BDI outputs.

**Relevance Level**
The classification of how much a belief supports a desire:
- 🔴 Critical — essential to success
- 🟡 High — strongly supportive
- 🟢 Medium — useful context
- 🔵 Low — peripheral

---

*LUMIA Studio | User Manual v1.0*
*For technical issues or feedback, contact your system administrator.*
