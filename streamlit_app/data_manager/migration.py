from .local import LocalDataManager
from .gsheets import GoogleSheetsDataManager
import streamlit as st
import time

def migrate_local_to_gsheets(local_db: LocalDataManager, gsheets_db: GoogleSheetsDataManager):
    """
    Migrate all data from Local DB to Google Sheets DB.
    """
    # Get all chits from local
    chits = local_db.get_all_chits()
    
    if not chits:
        st.info("No local data to migrate.")
        return

    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_chits = len(chits)
    
    for idx, chit in enumerate(chits):
        status_text.text(f"Migrating chit: {chit['name']}...")
        
        # Check if chit already exists in destination
        existing = gsheets_db.get_chit_by_id(chit['chit_id'])
        if existing:
            status_text.text(f"Skipping existing chit: {chit['name']}")
            progress_bar.progress((idx + 1) / total_chits)
            continue
            
        # Create chit in GSheets (using existing ID)
        # create_chit will create empty installments
        gsheets_db.create_chit(chit)
        
        # Get installments from local
        installments = local_db.get_installments(chit['chit_id'])
        
        # Update installments in GSheets
        if installments:
            updates = []
            for inst in installments:
                update = inst.copy()
                updates.append(update)
                
            gsheets_db.update_installments(chit['chit_id'], updates)
            
        progress_bar.progress((idx + 1) / total_chits)
        time.sleep(0.5) # Rate limit to avoid hitting API quotas too hard
        
    status_text.text("Migration complete!")
    st.success("Successfully migrated data to Google Sheets!")
