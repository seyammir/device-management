import streamlit as st
import os

# Import UI Modules
from src.ui.users_ui import show_users_ui
from src.ui.devices_ui import show_devices_ui
from src.ui.reservations_ui import show_reservations_ui
from src.ui.dashboard_ui import show_dashboard_ui

# Set page configuration
st.set_page_config(
    page_title="Device Manager",
    page_icon="🔧",
    layout="wide"
)

def main():
    # st.title("Device Management System")
    
    pages = [
        st.Page(show_dashboard_ui, title="Dashboard", default=True),
        st.Page(show_users_ui, title="User Management"),
        st.Page(show_devices_ui, title="Device Management"),
        st.Page(show_reservations_ui, title="Reservations"),
    ]

    pg = st.navigation(pages)
    
    pg.run()
    
    # System Status in Sidebar
    st.sidebar.caption("System Status")
    if os.path.exists("data/db.json"):
        st.sidebar.success("Database Connected")
    else:
        st.sidebar.error("Database Missing")

if __name__ == "__main__":
    main()