# LUMIA Studio — Architecture Documentation

> Generated: 2026-03-13 | Version: 1.0

## Chapters

| # | Chapter | Description |
|---|---------|-------------|
| 1 | [Architectural Overview](01-architectural-overview.md) | Guiding principles, layered multi-agent pattern, tech stack |
| 2 | [Architecture Visualization](02-architecture-visualization.md) | C4 diagrams: system context, container, BDI data flow |
| 3 | [Core Architectural Components](03-core-architectural-components.md) | API reference for all 7 manager classes |
| 4 | [Architectural Layers and Dependencies](04-architectural-layers-and-dependencies.md) | Dependency rules between pages/, utils/, data/ |
| 5 | [Data Architecture](05-data-architecture.md) | BDI JSON schema, session/context structure, ChromaDB, caching |
| 6 | [Cross-Cutting Concerns](06-cross-cutting-concerns.md) | Auth, error handling, logging, validation, config |
| 7 | [Service Communication Patterns](07-service-communication-patterns.md) | Intra-app communication, LLM API calls, RAG retrieval flow |
| 8 | [Python-Specific Architectural Patterns](08-python-specific-architectural-patterns.md) | Lazy init, LRU cache, OOP manager pattern, manual DI |
| 9 | [Implementation Patterns](09-implementation-patterns.md) | 6 reusable code patterns with full examples |
| 10 | [Testing Architecture](10-testing-architecture.md) | Current state, recommended test boundaries by layer |
| 11 | [Deployment Architecture](11-deployment-architecture.md) | Setup, runtime requirements, env config, Windows notes |
| 12 | [Extension and Evolution Patterns](12-extension-and-evolution-patterns.md) | How to add agents, providers, document types, BDI fields |
| 13 | [Architectural Pattern Examples](13-architectural-pattern-examples.md) | 3 end-to-end code walkthroughs |
| 14 | [Architectural Decision Records](14-architectural-decision-records.md) | 6 ADRs explaining key design choices and trade-offs |
| 15 | [Blueprint for New Development](15-blueprint-for-new-development.md) | Templates, starting points, common pitfalls |

---

> Full single-file version: [../../Project_Architecture_Blueprint.md](../../Project_Architecture_Blueprint.md)
