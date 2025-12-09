"""
Stage 2: Installment Tracking

Track and manage individual installments with reactive calculations.
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import date, datetime
import streamlit as st
import pandas as pd

from chit_fund_analyzer.models import ChitFundConfig, ChitFundAnalysisResult
from chit_fund_analyzer.analyzer import ChitFundAnalyzer
from chit_fund_analyzer.exceptions import ChitFundAnalysisError

from streamlit_app.data_manager.base import DataManager
from streamlit_app.utils import (
    show_success, show_error, show_warning, show_info,
    format_currency, format_percentage, show_metric_card
)


def render(db: DataManager) -> None:
    """
    Render the installment tracking stage.
    
    Args:
        db: Database instance
    """
    # Check if a chit is selected
    if 'selected_chit' not in st.session_state or st.session_state['selected_chit'] is None:
        show_warning("No chit fund selected. Please go back to the dashboard.")
        if st.button("⬅️ Back to Dashboard"):
            st.session_state['current_stage'] = 1
            st.rerun()
        return
    
    chit = st.session_state['selected_chit']
    
    st.title(f"📝 Installment Tracking: {chit['name']}")
    
    # Check if start date is in the future
    start_date = chit['start_date']
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date).date()
    
    if start_date > date.today():
        show_warning(f"⏰ This chit fund starts on {start_date}. No installments are due yet.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Dashboard"):
                st.session_state['current_stage'] = 1
                st.rerun()
        with col2:
            if st.button("➡️ Skip to Analysis"):
                st.session_state['current_stage'] = 3
                st.rerun()
        return
    
    # Load installments from database
    installments = db.get_installments(chit['chit_id'])
    
    if not installments:
        show_error("No installment data found for this chit.")
        return
    
    # Display chit summary
    render_chit_summary(chit)
    
    st.markdown("---")
    
    # Render installment editor
    render_installment_editor(db, chit, installments)
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Dashboard", use_container_width=True):
            st.session_state['current_stage'] = 1
            st.rerun()
    
    with col2:
        if st.button("📊 Go to Analysis", use_container_width=True, type="primary"):
            st.session_state['current_stage'] = 3
            st.rerun()


def render_chit_summary(chit: Dict[str, Any]) -> None:
    """Display summary of the chit fund."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Installments", chit['total_installments'])
    
    with col2:
        st.metric("Full Chit Value", format_currency(chit['full_chit_value']))
    
    with col3:
        base_installment = Decimal(str(chit['full_chit_value'])) / chit['total_installments']
        st.metric("Base Installment", format_currency(base_installment))
    
    with col4:
        st.metric("Frequency/Year", chit['chit_frequency_per_year'])


def render_installment_editor(
    db: DataManager, 
    chit: Dict[str, Any], 
    installments: List[Dict[str, Any]]
) -> None:
    """Render the installment data editor with reactive calculations."""
    
    st.subheader("Installment Details")
    
    # Convert to DataFrame for editing
    df = pd.DataFrame(installments)
    
    # Convert text columns to string to fix data type compatibility
    if 'winner_name' in df.columns:
        df['winner_name'] = df['winner_name'].fillna('').astype(str)
    if 'notes' in df.columns:
        df['notes'] = df['notes'].fillna('').astype(str)
    
    # Select columns to display/edit (removed bid_amount, added annual_irr_winner)
    display_columns = [
        'installment_number', 'date', 'amount_paid',
        'prize_amount', 'discount', 'annual_irr_winner', 'winner_name', 'is_winner', 'notes'
    ]
    
    # Ensure all columns exist
    for col in display_columns:
        if col not in df.columns:
            df[col] = None
    
    df = df[display_columns]
    
    # Convert numeric columns to proper types for data_editor
    numeric_cols = ['amount_paid', 'prize_amount', 'discount', 'annual_irr_winner']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Format for display
    df['date'] = pd.to_datetime(df['date']).dt.date
    
    # Column configuration for st.data_editor
    column_config = {
        'installment_number': st.column_config.NumberColumn(
            'Installment #',
            disabled=True,
            help="Installment number (read-only)"
        ),
        'date': st.column_config.DateColumn(
            'Date',
            help="Date of installment"
        ),
        'amount_paid': st.column_config.NumberColumn(
            'Amount Paid',
            help="Amount paid by non-winner members (enter to trigger calculations)",
            min_value=0
        ),
        'prize_amount': st.column_config.NumberColumn(
            'Prize Amount',
            help="Prize amount (auto-calculated)",
            disabled=True
        ),
        'discount': st.column_config.NumberColumn(
            'Discount',
            help="Discount (auto-calculated from amount paid)",
            disabled=True
        ),
        'annual_irr_winner': st.column_config.NumberColumn(
            'Annual IRR Winner',
            help="Annual IRR for winner (auto-calculated)",
            disabled=True
        ),
        'winner_name': st.column_config.TextColumn(
            'Winner Name',
            help="Name of the winner for this installment"
        ),
        'is_winner': st.column_config.CheckboxColumn(
            'Is Winner?',
            help="Check if you are the winner for this installment"
        ),
        'notes': st.column_config.TextColumn(
            'Notes',
            help="Additional notes"
        )
    }
    
    # Pre-calculate values for rows with amount_paid before displaying
    for idx, row in df.iterrows():
        amount_val = pd.to_numeric(row['amount_paid'], errors='coerce')
        if pd.notna(amount_val) and amount_val > 0:
            current_installment = int(row['installment_number'])
            
            try:
                # Get previous installments data
                previous_installments_df = df[df['installment_number'] < current_installment]
                
                previous_amounts = []
                for prev_idx, prev_row in previous_installments_df.iterrows():
                    prev_val = pd.to_numeric(prev_row['amount_paid'], errors='coerce')
                    if pd.notna(prev_val) and prev_val > 0:
                        previous_amounts.append(Decimal(str(prev_val)))
                
                remaining_installments = chit['total_installments'] - current_installment
                total_value = Decimal(str(chit['full_chit_value']))
                amount_paid_dec = Decimal(str(amount_val))
                base_installment = total_value / Decimal(str(chit['total_installments']))
                
                # Calculate implied bid amount (discount)
                # Formula: Amount Paid = (Total Value - Bid Amount) / Total Installments
                # So: Bid Amount = Total Value - (Amount Paid * Total Installments)
                
                bid_amount = total_value - (amount_paid_dec * Decimal(chit['total_installments']))
                
                if bid_amount <= 0:
                    bid_amount = Decimal('0')
                
                # Create ChitFundConfig with the calculated bid_amount
                config = ChitFundConfig(
                    total_installments=chit['total_installments'],
                    current_installment_number=current_installment,
                    full_chit_value=total_value,
                    chit_frequency_per_year=chit['chit_frequency_per_year'],
                    previous_installments=previous_amounts,
                    bid_amount=bid_amount
                )
                
                # Analyze
                analyzer = ChitFundAnalyzer(config)
                result = analyzer.analyze()
                
                # Update the DataFrame with calculated values
                df.loc[idx, 'discount'] = float(bid_amount)
                df.loc[idx, 'prize_amount'] = float(result.prize_amount)
                df.loc[idx, 'annual_irr_winner'] = float(result.annual_irr) * 100
                
            except Exception as e:
                show_error(f"Pre-calculation error for installment {current_installment}: {str(e)}")
    
    # Data editor with pre-calculated values
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        use_container_width=True,
        num_rows="fixed",
        key="installments_editor"
    )
    
    # Check if data was edited and recalculate
    data_changed = False
    for idx, row in edited_df.iterrows():
        orig_amount = df.loc[idx, 'amount_paid']
        new_amount = row['amount_paid']
        
        # Safely handle empty strings and None values
        try:
            # Convert to numeric, handling empty strings
            if isinstance(orig_amount, str) and orig_amount.strip() == '':
                orig_val = None
            else:
                orig_val = pd.to_numeric(orig_amount, errors='coerce')
            
            if isinstance(new_amount, str) and new_amount.strip() == '':
                new_val = None
            else:
                new_val = pd.to_numeric(new_amount, errors='coerce')
            
            # Check if amount_paid changed
            if pd.isna(orig_val) and pd.notna(new_val):
                data_changed = True
            elif pd.notna(orig_val) and pd.notna(new_val) and orig_val != new_val:
                data_changed = True
        except (ValueError, AttributeError):
            # Skip comparison if there's a conversion error
            continue
    
    # If data changed, save and rerun to recalculate
    if data_changed:
        try:
            # Save the edited data
            updates = []
            for idx, row in edited_df.iterrows():
                # Safely convert amount_paid, handling empty strings
                try:
                    if isinstance(row['amount_paid'], str) and row['amount_paid'].strip() == '':
                        amount_paid = None
                    else:
                        amount_val = pd.to_numeric(row['amount_paid'], errors='coerce')
                        amount_paid = float(amount_val) if pd.notna(amount_val) and amount_val > 0 else None
                except (ValueError, AttributeError, TypeError):
                    amount_paid = None
                
                update = {
                    'installment_number': int(row['installment_number']),
                    'date': row['date'],
                    'amount_paid': amount_paid,
                    'prize_amount': None,  # Will be recalculated
                    'discount': None,
                    'annual_irr_winner': None,
                    'winner_name': str(row['winner_name']).strip() if pd.notna(row['winner_name']) and str(row['winner_name']).strip() else None,
                    'is_winner': bool(row['is_winner']) if pd.notna(row['is_winner']) else False,
                    'notes': str(row['notes']).strip() if pd.notna(row['notes']) else ''
                }
                updates.append(update)
            
            db.update_installments(chit['chit_id'], updates)
            st.session_state['selected_chit'] = db.get_chit_by_id(chit['chit_id'])
            st.rerun()
            
        except Exception as e:
            show_error(f"Auto-save error: {str(e)}")
    
    # Reactive calculations section
    st.markdown("---")
    st.subheader("🔄 Real-time Analysis")
    
    # Process reactive calculations for display metrics
    calculations_made = False
    
    for idx, row in edited_df.iterrows():
        amount_val = pd.to_numeric(row['amount_paid'], errors='coerce')
        if pd.notna(amount_val) and amount_val > 0:
            calculations_made = True
            break
    
    # Display summary if calculations were made
    if calculations_made:
        # Find the last row with amount_paid for display
        last_calc_row = None
        for idx, row in edited_df.iterrows():
            amount_val = pd.to_numeric(row['amount_paid'], errors='coerce')
            if pd.notna(amount_val) and amount_val > 0:
                last_calc_row = row
        
        if last_calc_row is not None:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "💰 Prize Amount",
                    format_currency(last_calc_row['prize_amount']) if pd.notna(last_calc_row['prize_amount']) else "₹0.00"
                )
            
            with col2:
                st.metric(
                    "🎯 Discount",
                    format_currency(last_calc_row['discount']) if pd.notna(last_calc_row['discount']) else "₹0.00"
                )
            
            with col3:
                irr_value = last_calc_row['annual_irr_winner'] if pd.notna(last_calc_row['annual_irr_winner']) else 0
                # Convert to float safely
                try:
                    irr_float = float(irr_value) if irr_value else 0
                    st.metric(
                        "📈 Annual IRR (Winner)",
                        f"{irr_float:.4f}%" if irr_float else "0.00%"
                    )
                except (ValueError, TypeError):
                    st.metric(
                        "📈 Annual IRR (Winner)",
                        "0.00%"
                    )
            
            with col4:
                try:
                    winner_inst_amount = Decimal(str(chit['full_chit_value'])) - Decimal(str(last_calc_row['discount']) if pd.notna(last_calc_row['discount']) else 0)
                    st.metric(
                        "💵 Winner Gets",
                        format_currency(winner_inst_amount)
                    )
                except:
                    st.metric("💵 Winner Gets", "₹0.00")
            
            # Calculate amount for non-winners
            current_inst = int(last_calc_row['installment_number'])
            remaining_installments = chit['total_installments'] - current_inst
            
            if remaining_installments > 0:
                st.info(
                    f"💡 **Amount to be paid by non-winners:** "
                    f"{format_currency(last_calc_row['amount_paid'])} "
                    f"for the next {remaining_installments} installments"
                )
    else:
        show_info("💡 Enter an amount paid for an installment to see real-time calculations of Prize Amount, Discount, and Annual IRR.")
    
    # Manual Save button (for other field changes like winner_name, notes, etc.)
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        if st.button("💾 Save All Changes", type="primary", use_container_width=True):
            try:
                # Prepare updates with calculated values
                updates = []
                for idx, row in edited_df.iterrows():
                    # Recalculate if amount_paid exists
                    prize_amount = None
                    discount = None
                    annual_irr = None
                    
                    # Safely parse amount_paid from potentially formatted string
                    try:
                        if isinstance(row['amount_paid'], str):
                            # Remove currency symbol and commas if present
                            clean_amount = str(row['amount_paid']).replace('₹', '').replace(',', '').strip()
                            if clean_amount == '' or clean_amount == 'None':
                                amount_val = pd.NA
                            else:
                                amount_val = pd.to_numeric(clean_amount, errors='coerce')
                        else:
                            amount_val = pd.to_numeric(row['amount_paid'], errors='coerce')
                    except Exception:
                        amount_val = pd.NA
                    
                    if pd.notna(amount_val) and float(amount_val) > 0:
                        try:
                            current_installment = int(row['installment_number'])
                            previous_installments_df = edited_df[edited_df['installment_number'] < current_installment]
                            
                            previous_amounts = []
                            for prev_idx, prev_row in previous_installments_df.iterrows():
                                try:
                                    if isinstance(prev_row['amount_paid'], str):
                                        clean_prev = str(prev_row['amount_paid']).replace('₹', '').replace(',', '').strip()
                                        if clean_prev and clean_prev != 'None':
                                            prev_val = pd.to_numeric(clean_prev, errors='coerce')
                                        else:
                                            prev_val = pd.NA
                                    else:
                                        prev_val = pd.to_numeric(prev_row['amount_paid'], errors='coerce')
                                    
                                    if pd.notna(prev_val) and float(prev_val) > 0:
                                        previous_amounts.append(Decimal(str(float(prev_val))))
                                except Exception:
                                    continue
                            
                            remaining_installments = chit['total_installments'] - current_installment
                            total_value = Decimal(str(chit['full_chit_value']))
                            amount_paid = Decimal(str(float(amount_val)))
                            base_installment = total_value / Decimal(str(chit['total_installments']))
                            
                            bid_amount = total_value - ((amount_paid * remaining_installments) + base_installment)
                            if bid_amount <= 0:
                                bid_amount = Decimal('0')
                            
                            config = ChitFundConfig(
                                total_installments=chit['total_installments'],
                                current_installment_number=current_installment,
                                full_chit_value=total_value,
                                chit_frequency_per_year=chit['chit_frequency_per_year'],
                                previous_installments=previous_amounts,
                                bid_amount=bid_amount
                            )
                            
                            analyzer = ChitFundAnalyzer(config)
                            result = analyzer.analyze()
                            
                            prize_amount = float(result.prize_amount)
                            discount = float(bid_amount)
                            annual_irr = float(result.annual_irr) * 100
                        except:
                            pass
                    
                    update = {
                        'installment_number': int(row['installment_number']),
                        'date': row['date'],
                        'amount_paid': float(row['amount_paid']) if pd.notna(row['amount_paid']) else None,
                        'prize_amount': prize_amount,
                        'discount': discount,
                        'annual_irr_winner': annual_irr,
                        'winner_name': str(row['winner_name']) if pd.notna(row['winner_name']) else None,
                        'is_winner': bool(row['is_winner']) if pd.notna(row['is_winner']) else False,
                        'notes': str(row['notes']) if pd.notna(row['notes']) else ''
                    }
                    updates.append(update)
                
                # Save to database
                db.update_installments(chit['chit_id'], updates)
                
                show_success("✅ Installment data saved successfully!")
                
                # Refresh the selected chit
                st.session_state['selected_chit'] = db.get_chit_by_id(chit['chit_id'])
                
            except Exception as e:
                show_error(f"Failed to save: {str(e)}")
