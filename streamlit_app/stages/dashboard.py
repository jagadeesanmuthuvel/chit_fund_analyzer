"""
Stage 1: Dashboard

Chit selection, creation, and editing interface.
"""

from typing import Optional
from decimal import Decimal
from datetime import date, timedelta
import time
import streamlit as st
from streamlit_app.db import ChitFundDB
from streamlit_app.utils import (
    show_success, show_error, show_warning, 
    validate_positive_number, validate_positive_integer,
    format_currency, get_frequency_label
)


def render(db: ChitFundDB) -> None:
    """
    Render the dashboard stage.
    
    Args:
        db: Database instance
    """
    st.title("📊 Chit Fund Dashboard")
    
    # Create tabs
    tab1, tab2 = st.tabs(["📂 Select / Edit Chit", "➕ Create New Chit"])
    
    with tab1:
        render_select_edit_tab(db)
    
    with tab2:
        render_create_tab(db)


def render_select_edit_tab(db: ChitFundDB) -> None:
    """Render the select/edit existing chit tab."""
    st.subheader("Select an Existing Chit")
    
    # Get all chits
    chits = db.get_all_chits()
    
    if not chits:
        show_warning("No chits found. Create a new chit using the 'Create New Chit' tab.")
        return
    
    # Create selection dropdown
    chit_options = {
        f"{chit['name']} (ID: {chit['chit_id'][:8]}...)": chit['chit_id']
        for chit in chits
    }
    
    selected_display = st.selectbox(
        "Choose a Chit Fund",
        options=list(chit_options.keys()),
        key="chit_selector"
    )
    
    if selected_display:
        selected_chit_id = chit_options[selected_display]
        selected_chit = db.get_chit_by_id(selected_chit_id)
        
        if selected_chit:
            # Display chit details
            st.markdown("---")
            st.markdown("### Chit Fund Details")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Installments", selected_chit['total_installments'])
            
            with col2:
                st.metric("Full Chit Value", format_currency(selected_chit['full_chit_value']))
            
            with col3:
                st.metric(
                    "Frequency", 
                    get_frequency_label(selected_chit['chit_frequency_per_year'])
                )
            
            # Show description if available
            if selected_chit.get('description'):
                st.markdown(f"**Description:** {selected_chit['description']}")
            
            st.markdown(f"**Start Date:** {selected_chit['start_date']}")
            st.markdown(f"**Version:** {selected_chit['version']}")
            
            # Edit section
            st.markdown("---")
            st.markdown("### Edit Chit Details")
            
            # Use columns for better layout
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input(
                    "Chit Name",
                    value=selected_chit['name'],
                    key=f"edit_name_{selected_chit_id}"
                )
            
            with col2:
                new_description = st.text_area(
                    "Description",
                    value=selected_chit.get('description', ''),
                    height=100,
                    key=f"edit_description_{selected_chit_id}"
                )
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                def save_chit_changes():
                    try:
                        db.update_chit_metadata(
                            selected_chit_id,
                            {
                                'name': new_name,
                                'description': new_description
                            }
                        )
                        st.session_state['_chit_updated'] = True
                    except Exception as e:
                        st.session_state['_update_error'] = str(e)
                
                st.button(
                    "💾 Save Changes",
                    type="primary",
                    use_container_width=True,
                    key=f"save_chit_{selected_chit_id}",
                    on_click=save_chit_changes
                )
            
            with col2:
                def go_to_installments():
                    st.session_state['selected_chit'] = selected_chit
                    st.session_state['current_stage'] = 2
                
                st.button(
                    "➡️ Proceed to Installments",
                    use_container_width=True,
                    key=f"proceed_inst_{selected_chit_id}",
                    on_click=go_to_installments
                )
            
            # Show status messages
            if st.session_state.get('_chit_updated'):
                # Reload the chit data
                st.session_state['_chit_updated'] = False
                updated_chit = db.get_chit_by_id(selected_chit_id)
                st.session_state['selected_chit'] = updated_chit
                show_success("✅ Chit details updated successfully!")
                st.rerun()
            
            if st.session_state.get('_update_error'):
                error_msg = st.session_state.pop('_update_error')
                show_error(f"Failed to update chit: {error_msg}")


def render_create_tab(db: ChitFundDB) -> None:
    """Render the create new chit tab."""
    st.subheader("Initialize a New Chit Fund")
    
    st.markdown("""
    Create a new chit fund by providing the essential details. All fields are required.
    """)
    
    with st.form("create_chit_form"):
        # Chit Name
        chit_name = st.text_input(
            "Chit Fund Name *",
            placeholder="e.g., Family Chit 2024",
            help="A unique name to identify this chit fund"
        )
        
        # Description
        description = st.text_area(
            "Description (Optional)",
            placeholder="Additional details about this chit fund",
            help="Any additional information you'd like to track"
        )
        
        # Two columns for numeric inputs
        col1, col2 = st.columns(2)
        
        with col1:
            total_installments = st.number_input(
                "Total Installments *",
                min_value=1,
                max_value=100,
                value=12,
                step=1,
                help="Total number of installments in this chit fund"
            )
            
            chit_frequency = st.selectbox(
                "Payment Frequency *",
                options=[1, 2, 4, 6, 12],
                format_func=get_frequency_label,
                index=4,  # Default to monthly
                help="How many times per year installments are paid"
            )
        
        with col2:
            full_chit_value = st.number_input(
                "Full Chit Value (₹) *",
                min_value=1000.0,
                max_value=100000000.0,
                value=100000.0,
                step=1000.0,
                help="Total value of the chit fund"
            )
            
            start_date = st.date_input(
                "First Installment Date *",
                value=date.today(),
                help="Date of the first installment"
            )
        
        # Submit button
        st.markdown("<br>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button(
            "🚀 Initialize Chit Fund",
            type="primary",
            use_container_width=True
        )
    
    # Handle form submission outside the form context
    if submitted:
        # Validate inputs
        if not chit_name or chit_name.strip() == "":
            show_error("Please provide a chit fund name")
            return
        
        if not validate_positive_integer(total_installments, "Total Installments"):
            return
        
        if not validate_positive_number(full_chit_value, "Full Chit Value"):
            return
        
        # Create the chit
        try:
            chit_id = db.create_chit({
                'name': chit_name.strip(),
                'description': description.strip() if description else '',
                'total_installments': total_installments,
                'full_chit_value': Decimal(str(full_chit_value)),
                'chit_frequency_per_year': chit_frequency,
                'start_date': start_date
            })
            
            show_success(f"✨ Chit Fund '{chit_name}' created successfully!")
            st.balloons()
            
            # Load the created chit and verify installments
            created_chit = db.get_chit_by_id(chit_id)
            installments = db.get_installments(chit_id)
            
            if not created_chit or not installments:
                show_error("Failed to initialize chit or installments. Please try again.")
                return
            
            # Store in session state BEFORE showing button
            st.session_state['selected_chit'] = created_chit
            
            # Show next steps with delayed button
            st.markdown("---")
            st.markdown("### Next Steps")
            st.info(f"✅ Chit created with {len(installments)} installments")
            
            # Use callback to handle navigation
            def go_to_installments():
                st.session_state['current_stage'] = 2
            
            col1, col2 = st.columns([2, 1])
            with col2:
                st.button(
                    "➡️ Go to Installment Tracking", 
                    type="primary", 
                    use_container_width=True, 
                    key="goto_installments_btn",
                    on_click=go_to_installments
                )
            
        except Exception as e:
            show_error(f"Failed to create chit: {str(e)}")
