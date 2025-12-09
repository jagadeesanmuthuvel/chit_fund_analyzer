import pytest
from playwright.sync_api import Page, expect
import time
from datetime import date

def test_full_user_flow(page: Page):
    """
    Test the full user flow:
    1. Select Local Storage
    2. Login
    3. Create a new Chit
    4. Enter installment data
    5. Verify calculations
    """
    
    # 1. Select Local Storage
    # Wait for the storage selection screen
    expect(page.get_by_text("Storage Configuration")).to_be_visible(timeout=10000)
    
    # Click "Use Local Storage"
    page.get_by_role("button", name="Use Local Storage").click()
    
    # 2. Login
    # Wait for login screen
    # Use a more specific selector or exact text to avoid ambiguity
    expect(page.get_by_role("button", name="🔐 Login to Continue")).to_be_visible(timeout=10000)
    
    # Click Login
    page.get_by_role("button", name="🔐 Login to Continue").click()
    
    # 3. Create New Chit
    # Wait for Dashboard
    expect(page.get_by_text("Chit Fund Dashboard")).to_be_visible(timeout=10000)
    
    # Click "Create New Chit" tab
    # Streamlit tabs are buttons with role="tab"
    page.get_by_role("tab", name="➕ Create New Chit").click()
    
    # Fill form
    # Chit Name
    page.get_by_label("Chit Fund Name").fill("E2E Test Chit")
    
    # Total Installments
    page.get_by_label("Total Installments").fill("12")
    
    # Full Chit Value
    page.get_by_label("Full Chit Value (₹)").fill("120000")
    
    # Payment Frequency (Selectbox)
    # Selectboxes are tricky. We click the element to open it, then select the option.
    # Try to find the selectbox by label
    page.get_by_label("Payment Frequency").click()
    # Select "Monthly" from the dropdown - use exact=True to avoid matching "Bi-Monthly"
    page.get_by_role("option", name="Monthly", exact=True).click()
    
    # Submit
    page.get_by_role("button", name="🚀 Initialize Chit Fund").click()
    
    # 4. Verify Success & Navigate
    # Wait for success message
    expect(page.get_by_text("Chit Fund 'E2E Test Chit' created successfully!")).to_be_visible(timeout=10000)
    
    # Click "Go to Installment Tracking"
    # There might be multiple buttons if we ran this test before, but the new one should be visible
    page.get_by_role("button", name="➡️ Go to Installment Tracking").click()
    
    # 5. Installment Tracking
    # Wait for Installment Tracking page
    expect(page.get_by_text("Installment Tracking: E2E Test Chit")).to_be_visible(timeout=10000)
    
    # Interact with Data Editor
    # Note: Streamlit's st.data_editor uses Glide Data Grid which is canvas-based
    # Canvas grids don't expose cells as DOM elements, so we must use mouse coordinates
    # Column positions (measured from screenshots):
    # - Index (row numbers): X ~400-430
    # - Installment #: X ~455-530
    # - Date: X ~535-630
    # - Amount Paid (₹): X ~635-730
    # First data row (row 0): Y ~492
    
    # Wait for the grid container to be visible
    grid = page.locator('[data-testid="stDataEditor"]').or_(page.locator('[data-testid="stDataFrame"]'))
    expect(grid).to_be_visible(timeout=15000)
    
    # Click on the first row (index 0) in the Installment Details
    # Index column is at X ~415, first data row (index 0) at Y ~470
    # Based on MCP validation: Clicking at X=653 lands on Installment# column
    # Amount Paid column is further right, around X=740
    # Base installment = 120000/12 = 10000
    # Amount paid must be >60% (>6000) and <100% (<10000) of base installment
    page.mouse.click(415, 470)
    page.wait_for_timeout(500)
    
    # Navigate to Amount Paid column by pressing Right Arrow 3 times
    # (Index -> Installment# -> Date -> Amount Paid)
    page.keyboard.press("ArrowRight")
    page.wait_for_timeout(200)
    page.keyboard.press("ArrowRight")
    page.wait_for_timeout(200)
    page.keyboard.press("ArrowRight")
    page.wait_for_timeout(500)
    
    # Type the amount (9000) by pressing individual digit keys
    # Press 9
    page.keyboard.press("9")
    page.wait_for_timeout(200)
    # Press 0 three times
    page.keyboard.press("0")
    page.wait_for_timeout(200)
    page.keyboard.press("0")
    page.wait_for_timeout(200)
    page.keyboard.press("0")
    page.wait_for_timeout(500)
    
    # Press Enter to commit the edit and trigger Streamlit recalculation
    page.keyboard.press("Enter")
    
    # Wait for Streamlit to rerun and recalculate metrics
    page.wait_for_timeout(7000)
    
    # Verify Real-time Analysis section is visible
    expect(page.get_by_text("Real-time Analysis")).to_be_visible(timeout=10000)
    
    # Verify metrics appeared using simple text matching
    # The metrics are rendered as paragraph elements with emoji icons
    expect(page.get_by_text("💰 Prize Amount")).to_be_visible(timeout=5000)
    expect(page.get_by_text("🎯 Discount")).to_be_visible(timeout=5000)
    expect(page.get_by_text("📈 Annual IRR (Winner)")).to_be_visible(timeout=5000)
    expect(page.get_by_text("💵 Winner Gets")).to_be_visible(timeout=5000)
    
    # Verify the calculated values are present
    expect(page.get_by_text("₹98,000.00")).to_be_visible()  # Prize Amount value
    expect(page.get_by_text("₹12,000.00")).to_be_visible()  # Discount value

