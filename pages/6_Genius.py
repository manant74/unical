"""
Genius - BDI Execution Coach

Personal execution coach that helps users achieve their desires through
personalized action plans based on BDI frameworks.

Flow:
1. BDI Selection (from data/bdi_frameworks/)
2. Desire Customization (conversational)
3. User Context Gathering (role, timeline, constraints)
4. Plan Generation (future iteration)
5. Execution Coaching (future iteration)
"""

import streamlit as st
import os
from utils.genius_engine import GeniusEngine
from utils.llm_manager import LLMManager
from utils.prompts import get_prompt
from utils.ui_messages import get_random_thinking_message

# Page config
st.set_page_config(
    page_title="Genius - LumIA Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit default navigation menu
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Initialize managers
genius_engine = GeniusEngine()
llm_manager = LLMManager()

# Load system prompt (using prompt_suffix for discovery phase)
discovery_prompt = get_prompt("genius", prompt_suffix="discovery_prompt")

# ==================== Session State Initialization ====================

# Initialize Genius-specific session state
if 'genius_selected_bdi' not in st.session_state:
    st.session_state.genius_selected_bdi = None  # Currently selected BDI filename

if 'genius_bdi_data' not in st.session_state:
    st.session_state.genius_bdi_data = None  # Loaded BDI data

if 'genius_selected_desire' not in st.session_state:
    st.session_state.genius_selected_desire = None  # Selected desire ID

if 'genius_user_profile' not in st.session_state:
    st.session_state.genius_user_profile = None  # User context profile

if 'genius_messages' not in st.session_state:
    st.session_state.genius_messages = []  # Chat history

if 'genius_phase' not in st.session_state:
    st.session_state.genius_phase = "bdi_selection"  # Current phase

if 'genius_generated_plan' not in st.session_state:
    st.session_state.genius_generated_plan = None  # Generated action plan

# LLM settings (default from Gemini, can be overridden in sidebar)
if 'genius_llm_provider' not in st.session_state:
    st.session_state.genius_llm_provider = "OpenAI"

if 'genius_llm_model' not in st.session_state:
    st.session_state.genius_llm_model = "gpt-5.2"

if 'genius_llm_settings' not in st.session_state:
    st.session_state.genius_llm_settings = {
        "temperature": 0.7,  # Default for discovery phase
        "max_tokens": 2000,
        "top_p": 0.9,
        "reasoning_effort": "medium"  # Default for reasoning models
    }

# ==================== Sidebar ====================

with st.sidebar:
    st.markdown("### ⚡ Genius - Execution Coach")

    # Home button at the top
    if st.button("🏠 Back to Home", width='stretch'):
        st.switch_page("app.py")

    st.divider()

    # Phase indicator
    phase_emoji = {
        "bdi_selection": "📂",
        "desire_customization": "🎯",
        "context_gathering": "👤",
        "plan_generation": "📋",
        "execution": "🚀"
    }

    current_phase = st.session_state.genius_phase
    st.info(f"{phase_emoji.get(current_phase, '⚡')} **Phase**: {current_phase.replace('_', ' ').title()}")

    st.divider()

    # ==================== PROGRESS TRACKING (When plan is generated) ====================
    if st.session_state.genius_generated_plan is not None:
        plan = st.session_state.genius_generated_plan
        progress = plan['overall_progress']

        st.markdown("### 📊 Progress Tracking")

        # Overall progress bar
        st.progress(progress['percentage_complete'] / 100)
        st.caption(f"{progress['percentage_complete']:.0f}% complete ({progress['completed_steps']}/{progress['total_steps']} steps)")

        st.divider()

        # Current phase and step
        if progress['current_phase']:
            st.markdown(f"**Current Phase**: {progress['current_phase']}")
        if progress['current_step']:
            st.markdown(f"**Current Step**: {progress['current_step']}")

        st.divider()

        # Step checkboxes by phase
        st.markdown("**Steps:**")

        for phase in plan['plan_structure']['phases']:
            # Phase status emoji
            phase_status = phase.get('status', 'pending')
            if phase_status == 'completed':
                phase_emoji_status = "✅"
            elif phase_status == 'in_progress':
                phase_emoji_status = "🔵"
            else:
                phase_emoji_status = "⏳"

            with st.expander(f"{phase_emoji_status} {phase['phase_name']}", expanded=(phase_status == 'in_progress')):
                for step in phase.get('steps', []):
                    step_id = step['step_id']
                    step_status = step.get('status', 'pending')

                    # Checkbox for step completion
                    is_completed = step_status == 'completed'

                    # Unique key for checkbox
                    checkbox_key = f"step_checkbox_{step_id}"

                    # Checkbox with callback
                    new_status = st.checkbox(
                        f"{step_id}: {step['description'][:50]}...",
                        value=is_completed,
                        key=checkbox_key
                    )

                    # Update step status if changed
                    if new_status != is_completed:
                        target_status = 'completed' if new_status else 'pending'

                        # Update plan
                        success = genius_engine.update_plan_progress(
                            plan_id=plan['plan_id'],
                            step_id=step_id,
                            new_status=target_status,
                            user_notes="",
                            session_id=None
                        )

                        if success:
                            # Reload plan
                            updated_plan = genius_engine.load_plan(plan['plan_id'], session_id=None)
                            if updated_plan:
                                st.session_state.genius_generated_plan = updated_plan
                                st.rerun()

        st.divider()

    # LLM Configuration
    st.markdown("#### ⚙️ LLM Configuration")

    # Provider selection
    llm_provider = st.selectbox(
        "Provider",
        ["Gemini", "OpenAI"],
        index=0 if st.session_state.genius_llm_provider == "Gemini" else 1,
        key="genius_provider_select"
    )

    # Model selection based on provider
    if llm_provider == "Gemini":
        model_options = ["gemini-2.0-flash-exp", "gemini-2.5-flash", "gemini-2.5-pro"]
    else:  # OpenAI
        model_options = ["gpt-5.1", "gpt-5.2"]

    llm_model = st.selectbox(
        "Model",
        model_options,
        index=0,
        key="genius_model_select"
    )

    # Advanced settings
    with st.expander("🔧 Advanced Settings"):
        # Check if this is a reasoning model (GPT-5.x, o1, o3)
        is_reasoning_model = llm_model.startswith(("gpt-5", "o1", "o3"))

        if is_reasoning_model:
            # For reasoning models, only show reasoning_effort
            reasoning_effort = st.selectbox(
                "Reasoning Effort",
                options=["none", "low", "medium", "high"],
                index=2,  # default to "medium"
                help="Reasoning level for GPT-5.x models",
                key="genius_reasoning"
            )

            # Set default values for temperature/max_tokens/top_p (will be ignored by LLM)
            temperature = 0.7
            max_tokens = 2000
            top_p = 0.9

        else:
            # For standard models, show temperature/max_tokens/top_p
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=0.7,
                step=0.1,
                key="genius_temp"
            )

            max_tokens = st.number_input(
                "Max Tokens",
                min_value=500,
                max_value=8000,
                value=2000,
                step=100,
                key="genius_tokens"
            )

            top_p = st.slider(
                "Top P",
                min_value=0.0,
                max_value=1.0,
                value=0.9,
                step=0.05,
                key="genius_topp"
            )

            reasoning_effort = "medium"  # Default (not used for standard models)

    # Update session state
    st.session_state.genius_llm_provider = llm_provider
    st.session_state.genius_llm_model = llm_model
    st.session_state.genius_llm_settings = {
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "reasoning_effort": reasoning_effort
    }

    st.divider()

    # Current selection summary
    if st.session_state.genius_selected_bdi:
        st.markdown("#### 📊 Current Selection")
        st.write(f"**BDI**: {st.session_state.genius_selected_bdi.replace('_bdi.json', '').replace('_', ' ').title()}")

        if st.session_state.genius_selected_desire:
            desire = genius_engine.get_desire_by_id(
                st.session_state.genius_bdi_data,
                st.session_state.genius_selected_desire
            )
            if desire:
                st.write(f"**Desire**: {desire['desire_id']} - {desire['desire_statement'][:40]}...")

    st.divider()

    # Reset button
    if st.button("🔄 Start Over", width='stretch'):
        # Reset all Genius state
        st.session_state.genius_selected_bdi = None
        st.session_state.genius_bdi_data = None
        st.session_state.genius_selected_desire = None
        st.session_state.genius_user_profile = None
        st.session_state.genius_messages = []
        st.session_state.genius_phase = "bdi_selection"
        st.session_state.genius_generated_plan = None
        st.rerun()

# ==================== Main Area ====================

st.title("⚡ Genius - Your BDI Execution Coach")
st.markdown("_Transform strategic desires into concrete action plans_")
st.divider()

# ==================== PHASE 1: BDI Selection ====================

if st.session_state.genius_phase == "bdi_selection":
    st.markdown("### 📂 Select which BDI to work on")

    # Two tabs: New Plan or Load Existing Plan
    tab_new, tab_load = st.tabs(["🆕 New Plan", "📂 Load Existing Plan"])

    # ==================== TAB 1: NEW PLAN ====================
    with tab_new:
        st.markdown("Choose the BDI framework you want to work on:")

        # Load available BDI frameworks
        frameworks = genius_engine.load_bdi_frameworks()

        if not frameworks:
            st.warning("""
            ⚠️ **No BDI Framework found!**

            To use Genius, you must first create a BDI framework in `data/bdi_frameworks/`.

            **How to do it:**
            1. Go to **Compass**
            2. Load a session with complete BDI (Desires + Beliefs)
            3. Use the "Export as Framework" function (coming soon)
            4. Or manually copy the `current_bdi.json` file to the `data/bdi_frameworks/` folder
            """)

            if st.button("🧭 Go to Compass", width='stretch'):
                st.switch_page("pages/0_Compass.py")

        else:
            # Display BDI cards
            cols_per_row = 2
            for i in range(0, len(frameworks), cols_per_row):
                cols = st.columns(cols_per_row)

                for j in range(cols_per_row):
                    idx = i + j
                    if idx >= len(frameworks):
                        break

                    fw = frameworks[idx]

                    with cols[j]:
                        with st.container():
                            st.markdown(f"#### 🎯 {fw['display_name']}")
                            st.markdown(f"**Desires**: {fw['desire_count']} | **Beliefs**: {fw['belief_count']}")

                            if fw['tags']:
                                tags_str = ", ".join(fw['tags'][:3])  # Show max 3 tags
                                st.markdown(f"_Tags: {tags_str}_")

                            st.caption(f"Created: {fw['created_at'][:10]}")

                            if st.button(
                                f"Select",
                                key=f"select_bdi_{idx}",
                                width='stretch',
                                type="primary"
                            ):
                                # Load BDI data
                                bdi_data = genius_engine.load_bdi(fw['filename'])

                                if bdi_data:
                                    st.session_state.genius_selected_bdi = fw['filename']
                                    st.session_state.genius_bdi_data = bdi_data
                                    st.session_state.genius_phase = "desire_customization"

                                    # Initialize chat with Genius greeting
                                    greeting = f"""Hello! I've loaded the BDI framework **"{fw['display_name']}"**.

I see **{fw['desire_count']} desires** defined:

"""
                                    for desire in bdi_data['desires']:
                                        # Convert priority to string to handle both int and string values
                                        priority_value = str(desire.get('priority', 'medium')).lower()
                                        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority_value, "⚪")
                                        greeting += f"- {priority_emoji} **{desire['desire_id']}**: {desire['desire_statement']} (Priority: {priority_value.upper()})\n"

                                    greeting += "\n**Which desire would you like to work on today?** You can choose by ID (e.g., 'D2') or describe what interests you."

                                    st.session_state.genius_messages = [
                                        {"role": "assistant", "content": greeting}
                                    ]

                                    st.rerun()

                        st.divider()

    # ==================== TAB 2: LOAD EXISTING PLAN ====================
    with tab_load:
        st.markdown("Load a previously generated plan:")

        # List all existing plans
        existing_plans = genius_engine.list_plans(session_id=None)

        if not existing_plans:
            st.info("""
            📭 **No plans found**

            There are no saved plans. Create your first plan in the "🆕 New Plan" tab!
            """)
        else:
            st.markdown(f"**{len(existing_plans)} plans available**")
            st.divider()

            # Display plans as cards
            for plan_meta in existing_plans:
                with st.container():
                    col_info, col_action = st.columns([4, 1])

                    with col_info:
                        # Plan header
                        st.markdown(f"### 📋 {plan_meta['desire_statement'][:60]}...")

                        # Metadata
                        col_meta1, col_meta2, col_meta3 = st.columns(3)
                        with col_meta1:
                            st.metric("Phases", plan_meta['total_phases'])
                        with col_meta2:
                            st.metric("Steps", plan_meta['total_steps'])
                        with col_meta3:
                            st.metric("Progress", f"{plan_meta['progress_percentage']:.0f}%")

                        # Additional info
                        st.caption(f"🎯 **BDI**: {plan_meta['bdi_source'].replace('_bdi.json', '').replace('_', ' ').title()}")
                        st.caption(f"👤 **Role**: {plan_meta['user_role']} | ⏱️ **Timeline**: {plan_meta['timeline_weeks']} weeks")
                        st.caption(f"📅 **Created**: {plan_meta['created_at'][:16]}")

                    with col_action:
                        if st.button("📂 Load", key=f"load_plan_{plan_meta['plan_id']}", width='stretch', type="primary"):
                            # Load full plan
                            full_plan = genius_engine.load_plan(plan_meta['plan_id'], session_id=None)

                            if full_plan:
                                # Load associated BDI data
                                bdi_filename = plan_meta['bdi_source']
                                bdi_data = genius_engine.load_bdi(bdi_filename)

                                if bdi_data:
                                    # Set session state
                                    st.session_state.genius_selected_bdi = bdi_filename
                                    st.session_state.genius_bdi_data = bdi_data
                                    st.session_state.genius_selected_desire = plan_meta['desire_id']
                                    st.session_state.genius_user_profile = full_plan['user_profile']
                                    st.session_state.genius_generated_plan = full_plan
                                    st.session_state.genius_phase = "plan_generation"  # Skip to display phase

                                    st.success(f"✅ Plan '{plan_meta['desire_statement'][:30]}...' loaded!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ BDI source '{bdi_filename}' not found")
                            else:
                                st.error("❌ Failed to load plan")

                    st.divider()

# ==================== PHASE 2: Desire Customization + Context Gathering ====================

elif st.session_state.genius_phase in ["desire_customization", "context_gathering"]:

    # Display chat history
    for message in st.session_state.genius_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if user_input := st.chat_input("Your message..."):
        # Add user message to history
        st.session_state.genius_messages.append({
            "role": "user",
            "content": user_input
        })

        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate Genius response
        with st.chat_message("assistant"):
            with st.spinner(get_random_thinking_message()):
                # Build LLM context
                bdi_context = genius_engine.format_bdi_for_llm(
                    st.session_state.genius_bdi_data,
                    desire_id=st.session_state.genius_selected_desire
                )

                # Build messages for LLM
                messages = [
                    {"role": "system", "content": discovery_prompt},
                    {"role": "system", "content": f"\n\nLOADED BDI FRAMEWORK:\n{bdi_context}"},
                ]

                # Add conversation history
                for msg in st.session_state.genius_messages:
                    messages.append({"role": msg["role"], "content": msg["content"]})

                # Call LLM
                try:
                    # Extract settings
                    llm_settings = st.session_state.genius_llm_settings

                    response = llm_manager.chat(
                        provider=st.session_state.genius_llm_provider,
                        model=st.session_state.genius_llm_model,
                        messages=messages,
                        temperature=llm_settings.get("temperature", 0.7),
                        max_tokens=llm_settings.get("max_tokens", 2000),
                        top_p=llm_settings.get("top_p", 0.9),
                        reasoning_effort=llm_settings.get("reasoning_effort", "medium")
                    )

                    # Check for completion signal
                    if "USER_PROFILE_COMPLETE" in response:
                        # Extract profile from conversation
                        # Parse user profile from conversation messages
                        user_profile = genius_engine.create_user_profile(
                            role="User",  # Will be extracted from conversation in future
                            timeline_weeks=12,  # Will be extracted from conversation
                            current_situation="Working on implementing desire",
                            constraints=[],  # Will be extracted from conversation
                            additional_notes=""
                        )

                        st.session_state.genius_user_profile = user_profile
                        st.session_state.genius_phase = "plan_generation"

                        response = response.replace("USER_PROFILE_COMPLETE", "").strip()

                        if not response:
                            response = "✅ Perfect! I have all the necessary information. Now generating your personalized action plan..."

                    # Check if desire was customized (simple heuristic)
                    if st.session_state.genius_selected_desire is None:
                        # Try to detect desire customization (look for "D1", "D2", etc. in user input)
                        for desire in st.session_state.genius_bdi_data['desires']:
                            desire_id = desire['desire_id']
                            # Convert to string to handle both int and string IDs
                            desire_id_str = str(desire_id).lower()
                            if desire_id_str in user_input.lower():
                                st.session_state.genius_selected_desire = desire_id
                                st.session_state.genius_phase = "context_gathering"
                                break

                    # Display response
                    st.markdown(response)

                    # Add to history
                    st.session_state.genius_messages.append({
                        "role": "assistant",
                        "content": response
                    })

                except Exception as e:
                    error_msg = f"❌ LLM Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.genius_messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

# ==================== PHASE 3: Plan Generation ====================

elif st.session_state.genius_phase == "plan_generation":

    # Check if plan already generated
    if 'genius_generated_plan' not in st.session_state or st.session_state.genius_generated_plan is None:
        st.info("⚡ **Plan Generation in Progress...**")

        with st.spinner("Generating your personalized action plan... This may take 30-60 seconds."):
            try:
                # Generate plan structure via LLM
                plan_structure = genius_engine.generate_plan_structure(
                    llm_manager=llm_manager,
                    bdi_data=st.session_state.genius_bdi_data,
                    desire_id=st.session_state.genius_selected_desire,
                    user_profile=st.session_state.genius_user_profile,
                    llm_provider=st.session_state.genius_llm_provider,
                    llm_model=st.session_state.genius_llm_model
                )

                if plan_structure:
                    # Create full plan with metadata
                    full_plan = genius_engine.create_full_plan(
                        plan_structure=plan_structure,
                        bdi_data=st.session_state.genius_bdi_data,
                        desire_id=st.session_state.genius_selected_desire,
                        user_profile=st.session_state.genius_user_profile,
                        bdi_source=st.session_state.genius_selected_bdi,
                        session_id=None  # Will add session support later
                    )

                    st.session_state.genius_generated_plan = full_plan

                    # Save plan to disk
                    try:
                        plan_path = genius_engine.save_plan(full_plan, session_id=None)
                        print(f"Plan saved to: {plan_path}")
                    except Exception as save_error:
                        print(f"Warning: Could not save plan: {str(save_error)}")

                    st.rerun()
                else:
                    st.error("❌ Error generating plan. Please try again.")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    else:
        # Plan already generated - display it
        plan = st.session_state.genius_generated_plan

        st.success("✅ **Plan Generated Successfully!**")

        # Plan summary
        st.markdown(f"### 📋 {plan['target_desire']['desire_statement']}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Phases", plan['plan_structure']['total_phases'])
        with col2:
            st.metric("Total Steps", plan['plan_structure']['total_steps'])
        with col3:
            st.metric("Estimated Duration", f"{plan['plan_structure']['estimated_duration_weeks']} weeks")

        st.divider()

        # Display phases and steps
        for phase in plan['plan_structure']['phases']:
            with st.expander(f"📍 **{phase['phase_name']}** ({phase['duration_weeks']} weeks)", expanded=True):
                for step in phase['steps']:
                    st.markdown(f"#### {step['step_id']}: {step['description']}")

                    col_tasks, col_beliefs = st.columns([3, 2])

                    with col_tasks:
                        st.markdown("**Tasks:**")
                        for task in step.get('tasks', []):
                            st.markdown(f"- {task}")

                        st.markdown("**Verification:**")
                        for criterion in step.get('verification_criteria', []):
                            st.markdown(f"✓ {criterion}")

                    with col_beliefs:
                        st.markdown("**Supporting Beliefs:**")
                        for belief in step.get('supporting_beliefs', []):
                            if isinstance(belief, dict):
                                level_emoji = {"CRITICO": "🔴", "ALTO": "🟡", "MEDIO": "🟢"}.get(belief.get('relevance_level', 'MEDIO'), "⚪")
                                st.markdown(f"{level_emoji} {belief.get('subject', 'N/A')}")
                            else:
                                st.markdown(f"• {belief}")

                    # Show practical tips if available
                    if 'practical_tips' in step and step['practical_tips']:
                        st.markdown("**💡 Practical Tips:**")
                        for tip in step['practical_tips']:
                            st.markdown(f"💡 {tip}")

                    st.markdown(f"⏱️ **Effort**: {step.get('estimated_effort_days', 'N/A')} days | 👤 **Who**: {step.get('assigned_to', 'N/A')}")
                    st.divider()

        st.divider()

        # Action buttons
        col_enrich, col_save, col_export = st.columns(3)

        with col_enrich:
            # Check if tips already generated
            has_tips = False
            for phase in plan['plan_structure']['phases']:
                for step in phase.get('steps', []):
                    if 'practical_tips' in step and step['practical_tips']:
                        has_tips = True
                        break
                if has_tips:
                    break

            if not has_tips:
                if st.button("💡 Enrich with Tips and Tools", width='stretch', type="primary"):
                    with st.spinner("Generating practical tips for each step... This may take 1-2 minutes."):
                        try:
                            enriched_plan = genius_engine.enrich_plan_with_tips(
                                llm_manager=llm_manager,
                                plan=plan,
                                llm_provider=st.session_state.genius_llm_provider,
                                llm_model=st.session_state.genius_llm_model
                            )

                            # Update session state and save
                            st.session_state.genius_generated_plan = enriched_plan
                            genius_engine.save_plan(enriched_plan, session_id=None)

                            st.success("✅ Tips generated successfully!")
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error in enrichment: {str(e)}")
            else:
                st.button("✅ Tips Already Generated", width='stretch', disabled=True)

        with col_save:
            if st.button("💾 Save Plan", width='stretch', type="secondary"):
                try:
                    plan_path = genius_engine.save_plan(plan, session_id=None)
                    st.success(f"✅ Plan saved successfully!\n\nPath: `{plan_path}`")
                except Exception as e:
                    st.error(f"❌ Error saving plan: {str(e)}")

        with col_export:
            if st.button("📄 Export Markdown", width='stretch', type="secondary"):
                try:
                    # Generate markdown
                    markdown_content = genius_engine.export_plan_to_markdown(plan)

                    # Create download button
                    plan_filename = f"genius_plan_{plan['plan_id'][:8]}.md"

                    st.download_button(
                        label="⬇️ Download Markdown",
                        data=markdown_content,
                        file_name=plan_filename,
                        mime="text/markdown",
                        width='stretch'
                    )

                except Exception as e:
                    st.error(f"❌ Error exporting: {str(e)}")

        st.divider()

        # Beliefs summary
        with st.expander("🧠 **Beliefs Used in the Plan**"):
            for belief in plan.get('relevant_beliefs_summary', []):
                level_emoji = {"CRITICO": "🔴", "ALTO": "🟡", "MEDIO": "🟢"}.get(belief['relevance_level'], "⚪")
                st.markdown(f"{level_emoji} **{belief['subject']}** ({belief['relevance_level']})")
                st.caption(belief['definition'])
                st.caption(f"Used in: {', '.join(belief['used_in_steps'])}")
                st.divider()

    st.info("""
    ### 🚧 Upcoming Features

    - **Progress Tracking**: Mark steps as completed
    - **Interactive Coaching**: Ask specific questions about each step
    - **User Notes**: Add notes for each completed step
    - **Export**: Export the plan to Markdown

    For now, you can start over by clicking "🔄 Start Over" in the sidebar.
    """)

    if st.button("📋 View Summary", type="primary"):
        st.markdown("#### 📊 Genius Session Summary")

        st.markdown(f"**BDI Framework**: {st.session_state.genius_selected_bdi}")

        if st.session_state.genius_selected_desire:
            desire = genius_engine.get_desire_by_id(
                st.session_state.genius_bdi_data,
                st.session_state.genius_selected_desire
            )
            st.markdown(f"**Desire**: {desire['desire_id']} - {desire['desire_statement']}")
            st.markdown(f"**Priority**: {desire.get('priority', 'N/A').upper()}")
            st.markdown(f"**Success Metrics**:")
            for metric in desire.get('success_metrics', []):
                st.markdown(f"- {metric}")

        st.markdown("#### 💬 Conversation")
        for msg in st.session_state.genius_messages:
            role_emoji = "🤖" if msg['role'] == "assistant" else "👤"
            st.markdown(f"{role_emoji} **{msg['role'].title()}**: {msg['content'][:100]}...")

# Navigation removed - Home button is in sidebar
