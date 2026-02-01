"""
GeniusEngine - Business logic for Genius agent (BDI Execution Coach)

This module handles:
- Loading BDI frameworks from data/bdi_frameworks/
- Filtering beliefs by relevance level
- Creating user profiles from conversation
- Generating action plans (structure + details)
- Managing plan persistence and progress tracking

Author: LUMIA Development Team
Version: 1.0 (MVP)
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from utils.prompts import get_prompt


class GeniusEngine:
    """
    Core engine for Genius agent functionality.

    Manages BDI framework loading, belief filtering, and plan generation.
    """

    def __init__(self, data_dir: str = "./data"):
        """
        Initialize GeniusEngine.

        Args:
            data_dir: Root data directory (default: "./data")
        """
        self.data_dir = data_dir
        self.bdi_frameworks_dir = os.path.join(data_dir, "bdi_frameworks")
        self.sessions_dir = os.path.join(data_dir, "sessions")

        # Ensure directories exist
        os.makedirs(self.bdi_frameworks_dir, exist_ok=True)

    # ==================== BDI Framework Management ====================

    def load_bdi_frameworks(self) -> List[Dict]:
        """
        Load all available BDI frameworks from data/bdi_frameworks/

        Returns:
            List of BDI framework metadata dicts with:
            - filename: str (e.g., "ecommerce_retention_bdi.json")
            - display_name: str (extracted from domain_summary)
            - domain: str (domain_summary)
            - desire_count: int
            - belief_count: int
            - tags: List[str] (extracted from beliefs/desires)
            - created_at: str (file creation time)
            - is_valid: bool (JSON validation status)

        Example:
            >>> engine = GeniusEngine()
            >>> frameworks = engine.load_bdi_frameworks()
            >>> print(frameworks[0]['display_name'])
            'E-commerce Retention Strategy'
        """
        frameworks = []

        # List all JSON files in bdi_frameworks/
        if not os.path.exists(self.bdi_frameworks_dir):
            return []

        for filename in os.listdir(self.bdi_frameworks_dir):
            if not filename.endswith('.json'):
                continue

            filepath = os.path.join(self.bdi_frameworks_dir, filename)

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    bdi_data = json.load(f)

                # Validate BDI structure
                is_valid = self._validate_bdi_structure(bdi_data)

                if not is_valid:
                    # Skip invalid BDI files but log warning
                    print(f"Warning: Invalid BDI structure in {filename}")
                    continue

                # Extract metadata
                domain_summary = bdi_data.get('domain_summary', 'Unknown Domain')
                desires = bdi_data.get('desires', [])
                beliefs = bdi_data.get('beliefs', [])

                # Extract tags from desires and beliefs
                tags = set()
                for desire in desires:
                    tags.update(desire.get('tags', []))
                for belief in beliefs:
                    tags.update(belief.get('tags', []))

                # Get file creation time
                created_at = datetime.fromtimestamp(
                    os.path.getctime(filepath)
                ).isoformat()

                # Create metadata dict
                framework_metadata = {
                    'filename': filename,
                    'display_name': domain_summary[:50],  # Truncate if too long
                    'domain': domain_summary,
                    'desire_count': len(desires),
                    'belief_count': len(beliefs),
                    'tags': sorted(list(tags)) if tags else [],
                    'created_at': created_at,
                    'is_valid': True
                }

                frameworks.append(framework_metadata)

            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in {filename}: {str(e)}")
                continue
            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")
                continue

        # Sort by creation time (newest first)
        frameworks.sort(key=lambda x: x['created_at'], reverse=True)

        return frameworks

    def load_bdi(self, filename: str) -> Optional[Dict]:
        """
        Load a specific BDI framework by filename.

        Args:
            filename: BDI file name (e.g., "ecommerce_retention_bdi.json")

        Returns:
            Complete BDI data dict, or None if file doesn't exist/invalid

        Example:
            >>> engine = GeniusEngine()
            >>> bdi = engine.load_bdi("ecommerce_retention_bdi.json")
            >>> print(bdi['domain_summary'])
            'E-commerce SaaS platform...'
        """
        filepath = os.path.join(self.bdi_frameworks_dir, filename)

        if not os.path.exists(filepath):
            print(f"Error: BDI file not found: {filename}")
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                bdi_data = json.load(f)

            # Validate structure
            if not self._validate_bdi_structure(bdi_data):
                print(f"Error: Invalid BDI structure in {filename}")
                return None

            return bdi_data

        except Exception as e:
            print(f"Error loading BDI {filename}: {str(e)}")
            return None

    def _validate_bdi_structure(self, bdi_data: Dict) -> bool:
        """
        Validate BDI data has required structure.

        Args:
            bdi_data: BDI dict to validate

        Returns:
            True if valid, False otherwise
        """
        required_keys = ['domain_summary', 'desires', 'beliefs']

        # Check required top-level keys
        for key in required_keys:
            if key not in bdi_data:
                return False

        # Validate desires structure
        if not isinstance(bdi_data['desires'], list):
            return False

        for desire in bdi_data['desires']:
            if not all(k in desire for k in ['desire_id', 'desire_statement', 'priority']):
                return False

        # Validate beliefs structure
        if not isinstance(bdi_data['beliefs'], list):
            return False

        for belief in bdi_data['beliefs']:
            if not all(k in belief for k in ['subject', 'definition']):
                return False

        return True

    # ==================== Belief Filtering ====================

    def filter_beliefs(
        self,
        bdi_data: Dict,
        desire_id: Optional[str] = None,
        min_relevance_level: str = "ALTO"
    ) -> List[Dict]:
        """
        Filter beliefs by desire and relevance level.

        Args:
            bdi_data: Complete BDI framework data
            desire_id: Filter beliefs related to this desire (optional)
            min_relevance_level: Minimum relevance level to include
                Options: "CRITICO", "ALTO", "MEDIO", "BASSO"
                Default: "ALTO" (includes CRITICO + ALTO)

        Returns:
            List of belief dicts that match criteria, sorted by relevance

        Example:
            >>> engine = GeniusEngine()
            >>> bdi = engine.load_bdi("ecommerce_retention_bdi.json")
            >>> critical_beliefs = engine.filter_beliefs(bdi, desire_id="D2", min_relevance_level="CRITICO")
            >>> len(critical_beliefs)
            1
        """
        relevance_hierarchy = {
            "CRITICO": 4,
            "ALTO": 3,
            "MEDIO": 2,
            "BASSO": 1
        }

        min_level_value = relevance_hierarchy.get(min_relevance_level, 3)

        filtered_beliefs = []

        # Normalize desire_id for comparison (handle both int and "D{int}" formats)
        normalized_desire_id = None
        if desire_id:
            if isinstance(desire_id, int):
                # Convert int to "D{int}" format
                normalized_desire_id = f"D{desire_id}"
            elif isinstance(desire_id, str):
                # Already string, ensure it has "D" prefix
                if desire_id.startswith("D"):
                    normalized_desire_id = desire_id
                else:
                    normalized_desire_id = f"D{desire_id}"

        for belief in bdi_data.get('beliefs', []):
            # Check if belief is related to desire (if specified)
            if normalized_desire_id:
                related_desires = belief.get('related_desires', [])

                # Find matching desire (handle both formats)
                matching_desire = None
                for rd in related_desires:
                    rd_id = rd.get('desire_id')
                    # Normalize belief's desire_id too
                    normalized_rd_id = None
                    if isinstance(rd_id, int):
                        normalized_rd_id = f"D{rd_id}"
                    elif isinstance(rd_id, str):
                        normalized_rd_id = rd_id if rd_id.startswith("D") else f"D{rd_id}"

                    if normalized_rd_id == normalized_desire_id:
                        matching_desire = rd
                        break

                if not matching_desire:
                    continue  # Skip belief if not related to desire

                # Check relevance level
                relevance_level = matching_desire.get('relevance_level', 'BASSO')
                level_value = relevance_hierarchy.get(relevance_level, 1)

                if level_value >= min_level_value:
                    # Add relevance info to belief for easy access
                    belief_with_relevance = belief.copy()
                    belief_with_relevance['_relevance_to_desire'] = {
                        'desire_id': desire_id,
                        'level': relevance_level,
                        'level_value': level_value,
                        'definition': matching_desire.get('definition', '')
                    }
                    filtered_beliefs.append(belief_with_relevance)
            else:
                # No desire filter, include all beliefs
                filtered_beliefs.append(belief)

        # Sort by relevance level (highest first) if desire_id specified
        if desire_id:
            filtered_beliefs.sort(
                key=lambda b: b.get('_relevance_to_desire', {}).get('level_value', 0),
                reverse=True
            )

        return filtered_beliefs

    # ==================== User Profile Management ====================

    def create_user_profile(
        self,
        role: str,
        timeline_weeks: int,
        current_situation: str,
        constraints: List[str],
        skill_level: str = "intermediate",
        additional_notes: str = ""
    ) -> Dict:
        """
        Create user profile from gathered context.

        Args:
            role: User's role (e.g., "Product Manager")
            timeline_weeks: Available timeline in weeks
            current_situation: Current state description
            constraints: List of constraints (e.g., ["small_team", "limited_budget"])
            skill_level: User's skill level (default: "intermediate")
            additional_notes: Any additional context

        Returns:
            User profile dict

        Example:
            >>> engine = GeniusEngine()
            >>> profile = engine.create_user_profile(
            ...     role="Product Manager",
            ...     timeline_weeks=12,
            ...     current_situation="Basic onboarding exists",
            ...     constraints=["small_team", "limited_budget"]
            ... )
            >>> profile['timeline_weeks']
            12
        """
        profile = {
            "profile_id": str(uuid.uuid4())[:8],  # Short UUID
            "role": role,
            "timeline_weeks": timeline_weeks,
            "current_situation": current_situation,
            "constraints": constraints,
            "skill_level": skill_level,
            "additional_notes": additional_notes,
            "created_at": datetime.now().isoformat()
        }

        return profile

    # ==================== Plan Generation ====================

    def generate_plan_structure(
        self,
        llm_manager,
        bdi_data: Dict,
        desire_id: str,
        user_profile: Dict,
        llm_provider: str = "Gemini",
        llm_model: str = "gemini-2.0-flash-exp"
    ) -> Optional[Dict]:
        """
        Generate action plan structure using LLM.

        Args:
            llm_manager: LLMManager instance
            bdi_data: Complete BDI framework data
            desire_id: Target desire ID
            user_profile: User context profile
            llm_provider: LLM provider to use
            llm_model: LLM model to use

        Returns:
            Plan structure dict or None if generation fails
        """
        # Get desire
        desire = self.get_desire_by_id(bdi_data, desire_id)
        if not desire:
            return None

        # Filter relevant beliefs (CRITICO + ALTO)
        relevant_beliefs = self.filter_beliefs(bdi_data, desire_id, min_relevance_level="ALTO")

        # Build prompt for plan generation
        prompt = self._build_plan_generation_prompt(desire, user_profile, relevant_beliefs)

        # Call LLM
        try:
            response = llm_manager.chat(
                provider=llm_provider,
                model=llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=4000  # Higher for plan generation
            )

            # Parse JSON response
            import json
            # Extract JSON from markdown code blocks if present
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()

            plan_structure = json.loads(json_str)

            return plan_structure

        except Exception as e:
            print(f"Error generating plan: {str(e)}")
            return None

    def _build_plan_generation_prompt(
        self,
        desire: Dict,
        user_profile: Dict,
        relevant_beliefs: List[Dict]
    ) -> str:
        """Build LLM prompt for plan generation."""

        # Load prompt template
        prompt_template = get_prompt('genius', prompt_suffix='plan_generation_prompt')

        # Build beliefs_text with numbered list for easy reference
        beliefs_text = ""
        for i, belief in enumerate(relevant_beliefs[:10], 1):  # Limit to top 10
            rel_info = belief.get('_relevance_to_desire', {})
            level = rel_info.get('level', 'UNKNOWN')
            emoji = {"CRITICO": "🔴", "ALTO": "🟡"}.get(level, "⚪")

            beliefs_text += f"\n{i}. {emoji} **{belief['subject']}** ({level})\n"
            beliefs_text += f"   Definition: {belief['definition'][:250]}\n"
            if belief.get('source'):
                beliefs_text += f"   Source: {belief.get('source')}\n"

        # Prepare placeholders
        placeholders = {
            'USER_ROLE': user_profile.get('role', 'N/A'),
            'TIMELINE_WEEKS': str(user_profile.get('timeline_weeks', 'N/A')),
            'CURRENT_SITUATION': user_profile.get('current_situation', 'N/A'),
            'CONSTRAINTS_LIST': ', '.join(user_profile.get('constraints', [])),
            'DESIRE_ID': desire['desire_id'],
            'DESIRE_STATEMENT': desire['desire_statement'],
            'PRIORITY': desire.get('priority', 'N/A'),
            'SUCCESS_METRICS': ', '.join(desire.get('success_metrics', [])),
            'RELEVANT_BELIEFS': beliefs_text
        }

        # Apply placeholders
        prompt = prompt_template
        for key, value in placeholders.items():
            prompt = prompt.replace(f'{{{key}}}', str(value))

        return prompt

    def create_full_plan(
        self,
        plan_structure: Dict,
        bdi_data: Dict,
        desire_id: str,
        user_profile: Dict,
        bdi_source: str,
        session_id: Optional[str] = None
    ) -> Dict:
        """
        Create complete plan with metadata from LLM-generated structure.

        Args:
            plan_structure: Plan structure from LLM (phases, steps)
            bdi_data: Complete BDI data
            desire_id: Target desire ID
            user_profile: User context
            bdi_source: BDI framework filename
            session_id: Optional session ID

        Returns:
            Complete plan dict ready to save
        """
        import uuid
        from datetime import datetime

        desire = self.get_desire_by_id(bdi_data, desire_id)
        relevant_beliefs = self.filter_beliefs(bdi_data, desire_id, min_relevance_level="ALTO")

        # Calculate progress
        total_steps = sum(len(phase.get('steps', [])) for phase in plan_structure.get('phases', []))

        plan = {
            "plan_id": str(uuid.uuid4())[:8],
            "session_id": session_id,
            "bdi_source": bdi_source,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),

            "target_desire": {
                "desire_id": desire['desire_id'],
                "desire_statement": desire['desire_statement'],
                "priority": desire.get('priority', 'medium'),
                "success_metrics": desire.get('success_metrics', [])
            },

            "user_profile": user_profile,

            "plan_structure": {
                "total_phases": len(plan_structure.get('phases', [])),
                "total_steps": total_steps,
                "estimated_duration_weeks": sum(p.get('duration_weeks', 0) for p in plan_structure.get('phases', [])),
                "phases": self._enrich_phases_with_metadata(plan_structure.get('phases', []), relevant_beliefs)
            },

            "relevant_beliefs_summary": self._create_beliefs_summary(relevant_beliefs, plan_structure),

            "overall_progress": {
                "total_steps": total_steps,
                "completed_steps": 0,
                "in_progress_steps": 0,
                "pending_steps": total_steps,
                "percentage_complete": 0.0,
                "current_phase": plan_structure['phases'][0]['phase_id'] if plan_structure.get('phases') else None,
                "current_step": None
            },

            "metadata": {
                "llm_provider": "Gemini",  # Will be dynamic later
                "llm_model": "gemini-2.0-flash-exp",
                "generation_method": "single_shot",
                "refinement_iterations": 0
            }
        }

        return plan

    def _enrich_phases_with_metadata(self, phases: List[Dict], beliefs: List[Dict]) -> List[Dict]:
        """Add status and metadata to phases."""
        enriched_phases = []

        for i, phase in enumerate(phases):
            enriched_phase = phase.copy()
            enriched_phase['phase_order'] = i + 1
            enriched_phase['status'] = 'pending'  # pending|in_progress|completed
            enriched_phase['started_at'] = None
            enriched_phase['completed_at'] = None

            # Enrich steps
            enriched_steps = []
            for j, step in enumerate(phase.get('steps', [])):
                enriched_step = step.copy()
                enriched_step['step_order'] = j + 1
                enriched_step['status'] = 'pending'
                enriched_step['started_at'] = None
                enriched_step['completed_at'] = None
                enriched_step['user_notes'] = ""

                # Match beliefs to this step
                enriched_step['supporting_beliefs'] = self._match_beliefs_to_step(step, beliefs)

                enriched_steps.append(enriched_step)

            enriched_phase['steps'] = enriched_steps
            enriched_phases.append(enriched_phase)

        return enriched_phases

    def _match_beliefs_to_step(self, step: Dict, beliefs: List[Dict]) -> List[Dict]:
        """Match beliefs mentioned in step to actual belief objects."""
        mentioned_subjects = step.get('supporting_beliefs', [])
        matched = []

        # Debug logging
        if mentioned_subjects:
            print(f"\n[DEBUG] Matching beliefs for step {step.get('step_id', 'unknown')}")
            print(f"[DEBUG] Mentioned subjects: {mentioned_subjects}")
            print(f"[DEBUG] Available beliefs: {[b['subject'] for b in beliefs]}")

        for subject in mentioned_subjects:
            # Tokenize mentioned subject for better matching
            subject_tokens = set(subject.lower().split())

            # Find belief by subject (improved fuzzy match)
            best_match = None
            best_score = 0

            for belief in beliefs:
                belief_subject = belief['subject'].lower()
                belief_tokens = set(belief_subject.split())

                # Check substring match (exact)
                if subject.lower() in belief_subject or belief_subject in subject.lower():
                    best_match = belief
                    best_score = 1.0
                    break  # Exact match, use immediately

                # Check token overlap (Jaccard similarity)
                overlap = len(subject_tokens & belief_tokens)
                union = len(subject_tokens | belief_tokens)
                score = overlap / union if union > 0 else 0

                # If significant overlap (>= 30% Jaccard), consider it a match
                if score >= 0.3 and score > best_score:
                    best_score = score
                    best_match = belief

            # Add best match if found
            if best_match:
                matched.append({
                    "subject": best_match['subject'],
                    "definition": best_match['definition'],
                    "relevance_level": best_match.get('_relevance_to_desire', {}).get('level', 'MEDIO'),
                    "source": best_match.get('source', 'N/A')
                })
                print(f"[DEBUG] ✓ Matched '{subject}' → '{best_match['subject']}' (score: {best_score:.2f})")
            else:
                print(f"[DEBUG] ✗ No match found for '{subject}'")

        print(f"[DEBUG] Total matched: {len(matched)}/{len(mentioned_subjects)}\n")
        return matched

    def _create_beliefs_summary(self, beliefs: List[Dict], plan_structure: Dict) -> List[Dict]:
        """Create summary of beliefs used in plan."""
        summary = []

        for belief in beliefs[:10]:  # Top 10 most relevant
            # Find which steps use this belief
            used_in_steps = []
            for phase in plan_structure.get('phases', []):
                for step in phase.get('steps', []):
                    for mentioned in step.get('supporting_beliefs', []):
                        if mentioned.lower() in belief['subject'].lower() or belief['subject'].lower() in mentioned.lower():
                            used_in_steps.append(step['step_id'])
                            break

            if used_in_steps:
                summary.append({
                    "subject": belief['subject'],
                    "definition": belief['definition'][:200] + "...",
                    "relevance_level": belief.get('_relevance_to_desire', {}).get('level', 'MEDIO'),
                    "used_in_steps": used_in_steps,
                    "source": belief.get('source', 'N/A')
                })

        return summary

    def enrich_plan_with_tips(
        self,
        llm_manager,
        plan: Dict,
        llm_provider: str = "Gemini",
        llm_model: str = "gemini-2.0-flash-exp"
    ) -> Dict:
        """
        Enrich plan steps with practical tips, tool recommendations, and examples.

        Args:
            llm_manager: LLMManager instance
            plan: Complete plan dict
            llm_provider: LLM provider to use
            llm_model: LLM model to use

        Returns:
            Enriched plan with 'practical_tips' added to each step
        """
        enriched_plan = plan.copy()

        for phase in enriched_plan['plan_structure']['phases']:
            for step in phase.get('steps', []):
                # Generate tips for this step
                tips = self._generate_step_tips(
                    llm_manager,
                    step,
                    plan['target_desire'],
                    plan['user_profile'],
                    llm_provider,
                    llm_model
                )

                if tips:
                    step['practical_tips'] = tips

        return enriched_plan

    def _generate_step_tips(
        self,
        llm_manager,
        step: Dict,
        desire: Dict,
        user_profile: Dict,
        llm_provider: str,
        llm_model: str
    ) -> List[str]:
        """Generate practical tips for a specific step using LLM."""

        # Load prompt template
        prompt_template = get_prompt('genius', prompt_suffix='step_tips_prompt')

        # Prepare placeholders
        placeholders = {
            'USER_ROLE': user_profile.get('role', 'N/A'),
            'CONSTRAINTS_LIST': ', '.join(user_profile.get('constraints', [])),
            'STEP_ID': step['step_id'],
            'STEP_DESCRIPTION': step['description'],
            'TASKS_LIST': ', '.join(step.get('tasks', []))
        }

        # Apply placeholders
        prompt = prompt_template
        for key, value in placeholders.items():
            prompt = prompt.replace(f'{{{key}}}', str(value))

        try:
            response = llm_manager.chat(
                provider=llm_provider,
                model=llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,  # Slightly lower for focused tips
                max_tokens=1000
            )

            # Parse JSON response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()

            tips = json.loads(json_str)

            return tips if isinstance(tips, list) else []

        except Exception as e:
            print(f"Error generating tips for step {step['step_id']}: {str(e)}")
            return []

    def export_plan_to_markdown(self, plan: Dict) -> str:
        """
        Export plan to Markdown format.

        Args:
            plan: Complete plan dict

        Returns:
            Markdown-formatted string
        """
        md = []

        # Header
        md.append(f"# {plan['target_desire']['desire_statement']}\n")
        md.append(f"**Generated**: {plan.get('created_at', 'N/A')}\n")
        md.append(f"**BDI Source**: {plan.get('bdi_source', 'N/A')}\n")
        md.append(f"**Plan ID**: {plan.get('plan_id', 'N/A')}\n")
        md.append("\n---\n")

        # User Profile
        md.append("## 👤 User Profile\n")
        profile = plan['user_profile']
        md.append(f"- **Role**: {profile.get('role', 'N/A')}\n")
        md.append(f"- **Timeline**: {profile.get('timeline_weeks', 'N/A')} weeks\n")
        md.append(f"- **Current Situation**: {profile.get('current_situation', 'N/A')}\n")
        md.append(f"- **Constraints**: {', '.join(profile.get('constraints', []))}\n")
        md.append("\n---\n")

        # Target Desire
        md.append("## 🎯 Target Desire\n")
        desire = plan['target_desire']
        md.append(f"**ID**: {desire['desire_id']}\n")
        md.append(f"**Statement**: {desire['desire_statement']}\n")
        md.append(f"**Priority**: {desire.get('priority', 'N/A')}\n")
        md.append("\n**Success Metrics**:\n")
        for metric in desire.get('success_metrics', []):
            md.append(f"- {metric}\n")
        md.append("\n---\n")

        # Plan Overview
        md.append("## 📊 Plan Overview\n")
        structure = plan['plan_structure']
        md.append(f"- **Total Phases**: {structure['total_phases']}\n")
        md.append(f"- **Total Steps**: {structure['total_steps']}\n")
        md.append(f"- **Estimated Duration**: {structure['estimated_duration_weeks']} weeks\n")
        md.append("\n---\n")

        # Progress
        progress = plan['overall_progress']
        md.append("## 📈 Progress\n")
        md.append(f"- **Completed Steps**: {progress['completed_steps']}/{progress['total_steps']}\n")
        md.append(f"- **Percentage Complete**: {progress['percentage_complete']:.0f}%\n")
        if progress['current_phase']:
            md.append(f"- **Current Phase**: {progress['current_phase']}\n")
        if progress['current_step']:
            md.append(f"- **Current Step**: {progress['current_step']}\n")
        md.append("\n---\n")

        # Phases and Steps
        md.append("## 📋 Action Plan\n")

        for phase in structure['phases']:
            phase_status = phase.get('status', 'pending')
            status_emoji = {"completed": "✅", "in_progress": "🔵", "pending": "⏳"}.get(phase_status, "⏳")

            md.append(f"\n### {status_emoji} {phase['phase_name']}\n")
            md.append(f"**Duration**: {phase['duration_weeks']} weeks\n")
            md.append(f"**Status**: {phase_status}\n\n")

            for step in phase.get('steps', []):
                step_status = step.get('status', 'pending')
                step_emoji = {"completed": "✅", "in_progress": "🔵", "pending": "⏳"}.get(step_status, "⏳")

                md.append(f"#### {step_emoji} {step['step_id']}: {step['description']}\n")
                md.append(f"**Status**: {step_status}\n")
                md.append(f"**Effort**: {step.get('estimated_effort_days', 'N/A')} days\n")
                md.append(f"**Assigned to**: {step.get('assigned_to', 'N/A')}\n\n")

                # Tasks
                md.append("**Tasks**:\n")
                for task in step.get('tasks', []):
                    checkbox = "[x]" if step_status == "completed" else "[ ]"
                    md.append(f"- {checkbox} {task}\n")
                md.append("\n")

                # Verification Criteria
                md.append("**Verification Criteria**:\n")
                for criterion in step.get('verification_criteria', []):
                    md.append(f"- ✓ {criterion}\n")
                md.append("\n")

                # Practical Tips (if available)
                if 'practical_tips' in step and step['practical_tips']:
                    md.append("**💡 Practical Tips**:\n")
                    for tip in step['practical_tips']:
                        md.append(f"- {tip}\n")
                    md.append("\n")

                # Supporting Beliefs
                if step.get('supporting_beliefs'):
                    md.append("**Supporting Beliefs**:\n")
                    for belief in step['supporting_beliefs']:
                        if isinstance(belief, dict):
                            level = belief.get('relevance_level', 'MEDIO')
                            level_emoji = {"CRITICO": "🔴", "ALTO": "🟡", "MEDIO": "🟢"}.get(level, "⚪")
                            md.append(f"- {level_emoji} **{belief.get('subject', 'N/A')}** ({level})\n")
                            md.append(f"  - {belief.get('definition', 'N/A')[:150]}...\n")
                        else:
                            md.append(f"- {belief}\n")
                    md.append("\n")

                # User Notes (if available)
                if step.get('user_notes'):
                    md.append(f"**📝 User Notes**: {step['user_notes']}\n\n")

                md.append("---\n\n")

        # Relevant Beliefs Summary
        if plan.get('relevant_beliefs_summary'):
            md.append("## 🧠 Beliefs Summary\n")
            for belief in plan['relevant_beliefs_summary']:
                level = belief['relevance_level']
                level_emoji = {"CRITICO": "🔴", "ALTO": "🟡", "MEDIO": "🟢"}.get(level, "⚪")
                md.append(f"### {level_emoji} {belief['subject']} ({level})\n")
                md.append(f"{belief['definition']}\n\n")
                md.append(f"**Used in steps**: {', '.join(belief['used_in_steps'])}\n")
                md.append(f"**Source**: {belief.get('source', 'N/A')}\n\n")
                md.append("---\n\n")

        # Footer
        md.append("---\n\n")
        md.append("*Generated by LUMIA Studio - Genius Agent*\n")
        md.append(f"*Plan ID: {plan.get('plan_id', 'N/A')}*\n")

        return "".join(md)

    # ==================== Plan Persistence ====================

    def save_plan(self, plan: Dict, session_id: Optional[str] = None) -> str:
        """
        Save plan to filesystem.

        Args:
            plan: Complete plan dict
            session_id: Optional session ID (if None, saves to standalone plans/)

        Returns:
            Path to saved plan file
        """
        import json
        from datetime import datetime

        # Determine save location
        if session_id:
            # Save to session directory
            plans_dir = os.path.join(self.sessions_dir, session_id, "genius_plans")
        else:
            # Save to standalone plans directory
            plans_dir = os.path.join(self.data_dir, "genius_plans")

        os.makedirs(plans_dir, exist_ok=True)

        # Update last_updated timestamp
        plan['last_updated'] = datetime.now().isoformat()

        # Save plan
        plan_filename = f"plan_{plan['plan_id']}.json"
        plan_path = os.path.join(plans_dir, plan_filename)

        with open(plan_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)

        # Update active plan marker
        self._set_active_plan(plan['plan_id'], session_id)

        return plan_path

    def load_plan(self, plan_id: str, session_id: Optional[str] = None) -> Optional[Dict]:
        """
        Load plan from filesystem.

        Args:
            plan_id: Plan ID to load
            session_id: Optional session ID

        Returns:
            Plan dict or None if not found
        """
        import json

        # Determine load location
        if session_id:
            plan_path = os.path.join(self.sessions_dir, session_id, "genius_plans", f"plan_{plan_id}.json")
        else:
            plan_path = os.path.join(self.data_dir, "genius_plans", f"plan_{plan_id}.json")

        if not os.path.exists(plan_path):
            return None

        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading plan: {str(e)}")
            return None

    def get_active_plan(self, session_id: Optional[str] = None) -> Optional[Dict]:
        """
        Get currently active plan.

        Args:
            session_id: Optional session ID

        Returns:
            Plan dict or None if no active plan
        """
        import json

        # Determine location
        if session_id:
            marker_path = os.path.join(self.sessions_dir, session_id, "genius_plans", ".active_plan")
        else:
            marker_path = os.path.join(self.data_dir, "genius_plans", ".active_plan")

        if not os.path.exists(marker_path):
            return None

        try:
            with open(marker_path, 'r', encoding='utf-8') as f:
                marker_data = json.load(f)
                plan_id = marker_data.get('active_plan_id')

            if plan_id:
                return self.load_plan(plan_id, session_id)

        except Exception as e:
            print(f"Error loading active plan: {str(e)}")

        return None

    def list_plans(self, session_id: Optional[str] = None) -> List[Dict]:
        """
        List all plans (metadata only).

        Args:
            session_id: Optional session ID

        Returns:
            List of plan metadata dicts
        """
        import json

        # Determine location
        if session_id:
            plans_dir = os.path.join(self.sessions_dir, session_id, "genius_plans")
        else:
            plans_dir = os.path.join(self.data_dir, "genius_plans")

        if not os.path.exists(plans_dir):
            return []

        plans_metadata = []

        for filename in os.listdir(plans_dir):
            if not filename.startswith('plan_') or not filename.endswith('.json'):
                continue

            plan_path = os.path.join(plans_dir, filename)

            try:
                with open(plan_path, 'r', encoding='utf-8') as f:
                    plan = json.load(f)

                # Extract metadata
                metadata = {
                    'plan_id': plan.get('plan_id'),
                    'bdi_source': plan.get('bdi_source'),
                    'desire_id': plan.get('target_desire', {}).get('desire_id'),
                    'desire_statement': plan.get('target_desire', {}).get('desire_statement'),
                    'created_at': plan.get('created_at'),
                    'last_updated': plan.get('last_updated'),
                    'total_phases': plan.get('plan_structure', {}).get('total_phases', 0),
                    'total_steps': plan.get('plan_structure', {}).get('total_steps', 0),
                    'progress_percentage': plan.get('overall_progress', {}).get('percentage_complete', 0),
                    'user_role': plan.get('user_profile', {}).get('role', 'N/A'),
                    'timeline_weeks': plan.get('user_profile', {}).get('timeline_weeks', 0)
                }

                plans_metadata.append(metadata)

            except Exception as e:
                print(f"Error reading plan {filename}: {str(e)}")
                continue

        # Sort by last_updated (newest first)
        plans_metadata.sort(key=lambda x: x.get('last_updated', ''), reverse=True)

        return plans_metadata

    def update_plan_progress(
        self,
        plan_id: str,
        step_id: str,
        new_status: str,
        user_notes: str = "",
        session_id: Optional[str] = None
    ) -> bool:
        """
        Update step status in a plan.

        Args:
            plan_id: Plan ID
            step_id: Step ID to update
            new_status: New status (pending|in_progress|completed)
            user_notes: Optional user notes
            session_id: Optional session ID

        Returns:
            True if updated successfully
        """
        from datetime import datetime

        plan = self.load_plan(plan_id, session_id)
        if not plan:
            return False

        # Find and update step
        step_found = False
        for phase in plan['plan_structure']['phases']:
            for step in phase['steps']:
                if step['step_id'] == step_id:
                    old_status = step.get('status', 'pending')
                    step['status'] = new_status
                    step['user_notes'] = user_notes

                    # Update timestamps
                    if new_status == 'in_progress' and old_status == 'pending':
                        step['started_at'] = datetime.now().isoformat()
                    elif new_status == 'completed' and old_status != 'completed':
                        step['completed_at'] = datetime.now().isoformat()

                    step_found = True
                    break

            if step_found:
                # Update phase status
                phase_steps = phase['steps']
                if all(s.get('status') == 'completed' for s in phase_steps):
                    phase['status'] = 'completed'
                    phase['completed_at'] = datetime.now().isoformat()
                elif any(s.get('status') in ['in_progress', 'completed'] for s in phase_steps):
                    if phase.get('status') == 'pending':
                        phase['status'] = 'in_progress'
                        phase['started_at'] = datetime.now().isoformat()
                break

        if not step_found:
            return False

        # Recalculate overall progress
        all_steps = []
        for phase in plan['plan_structure']['phases']:
            all_steps.extend(phase['steps'])

        completed = sum(1 for s in all_steps if s.get('status') == 'completed')
        in_progress = sum(1 for s in all_steps if s.get('status') == 'in_progress')
        total = len(all_steps)

        plan['overall_progress'] = {
            'total_steps': total,
            'completed_steps': completed,
            'in_progress_steps': in_progress,
            'pending_steps': total - completed - in_progress,
            'percentage_complete': round((completed / total) * 100, 2) if total > 0 else 0,
            'current_phase': None,  # Will determine below
            'current_step': step_id if new_status == 'in_progress' else None
        }

        # Determine current phase
        for phase in plan['plan_structure']['phases']:
            if phase.get('status') == 'in_progress':
                plan['overall_progress']['current_phase'] = phase['phase_id']
                break

        # Save updated plan
        self.save_plan(plan, session_id)

        return True

    def _set_active_plan(self, plan_id: str, session_id: Optional[str] = None):
        """Set active plan marker."""
        import json
        from datetime import datetime

        # Determine location
        if session_id:
            plans_dir = os.path.join(self.sessions_dir, session_id, "genius_plans")
        else:
            plans_dir = os.path.join(self.data_dir, "genius_plans")

        os.makedirs(plans_dir, exist_ok=True)

        marker_path = os.path.join(plans_dir, ".active_plan")

        marker_data = {
            'active_plan_id': plan_id,
            'set_at': datetime.now().isoformat()
        }

        with open(marker_path, 'w', encoding='utf-8') as f:
            json.dump(marker_data, f, indent=2)

    # ==================== Helper Methods ====================

    def get_desire_by_id(self, bdi_data: Dict, desire_id: str) -> Optional[Dict]:
        """
        Get a specific desire from BDI by ID.

        Args:
            bdi_data: BDI framework data
            desire_id: Desire ID (e.g., "D1")

        Returns:
            Desire dict or None if not found
        """
        for desire in bdi_data.get('desires', []):
            if desire.get('desire_id') == desire_id:
                return desire
        return None

    def format_bdi_for_llm(self, bdi_data: Dict, desire_id: Optional[str] = None) -> str:
        """
        Format BDI data for LLM prompt.

        Args:
            bdi_data: Complete BDI data
            desire_id: Optional desire ID to highlight

        Returns:
            Formatted string for LLM context
        """
        output = []

        # Domain summary
        output.append(f"DOMAIN: {bdi_data.get('domain_summary', 'Unknown')}")
        output.append("")

        # Desires
        output.append("DESIRES:")
        for desire in bdi_data.get('desires', []):
            did = desire.get('desire_id', '')
            statement = desire.get('desire_statement', '')
            priority = desire.get('priority', 'medium').upper()

            # Highlight selected desire
            prefix = ">>> " if did == desire_id else "    "
            output.append(f"{prefix}{did}: {statement} (Priority: {priority})")

        output.append("")

        # Beliefs (if desire specified, show only relevant ones)
        if desire_id:
            filtered_beliefs = self.filter_beliefs(bdi_data, desire_id, min_relevance_level="ALTO")
            output.append(f"RELEVANT BELIEFS FOR {desire_id} (CRITICO + ALTO):")

            for belief in filtered_beliefs:
                subject = belief.get('subject', '')
                relevance_info = belief.get('_relevance_to_desire', {})
                level = relevance_info.get('level', 'UNKNOWN')

                emoji = {"CRITICO": "🔴", "ALTO": "🟡"}.get(level, "⚪")
                output.append(f"{emoji} {subject} ({level})")
        else:
            output.append(f"TOTAL BELIEFS: {len(bdi_data.get('beliefs', []))}")

        return "\n".join(output)


# ==================== Module-level convenience functions ====================

def load_bdi_frameworks() -> List[Dict]:
    """Convenience function to load all BDI frameworks."""
    engine = GeniusEngine()
    return engine.load_bdi_frameworks()


def load_bdi(filename: str) -> Optional[Dict]:
    """Convenience function to load specific BDI."""
    engine = GeniusEngine()
    return engine.load_bdi(filename)
