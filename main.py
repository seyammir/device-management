import streamlit as st
import os

# Import UI Modules
from src.ui.users_ui import show_users_ui
from src.ui.devices_ui import show_devices_ui

# Set page configuration
st.set_page_config(
    page_title="Device Manager",
    page_icon="🔧",
    layout="wide"
)

def main():
    st.title("🔧 Device Management System")
    
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["Dashboard", "Device Management", "User Management"])

    if selection == "Dashboard":
        st.info("Dashboard module coming ....")
        
    elif selection == "Device Management":
        show_devices_ui()
        
    elif selection == "User Management":
        show_users_ui()
    
    # System Status in Sidebar
    st.sidebar.markdown("---")
    st.sidebar.caption("System Status")
    if os.path.exists("data/db.json"):
        st.sidebar.success("Database Connected")
    else:
        st.sidebar.error("Database Missing")

if __name__ == "__main__":
    main()