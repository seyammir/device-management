"""
Device Management System - Main Application Entry Point

A comprehensive device management system built with Streamlit and TinyDB
for tracking devices, users, reservations, and maintenance schedules.
"""
import streamlit as st
import os

# Import UI Modules
from src.ui.users_ui import show_users_ui
from src.ui.devices_ui import show_devices_ui
from src.ui.reservations_ui import show_reservations_ui
from src.ui.dashboard_ui import show_dashboard_ui
from src.core.config import Config
from src.core.logger import setup_logging

# Initialize logging
logger = setup_logging()

# Set page configuration
st.set_page_config(
    page_title=Config.APP_NAME,
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': f"# {Config.APP_NAME}\nVersion {Config.APP_VERSION}\n\nA comprehensive device management system."
    }
)


def main():
    """Main application entry point."""
    # Ensure required directories exist
    Config.ensure_directories()
    
    # Define navigation pages
    pages = [
        st.Page(show_dashboard_ui, title="Dashboard", icon="📊", default=True),
        st.Page(show_users_ui, title="User Management", icon="👥"),
        st.Page(show_devices_ui, title="Device Management", icon="🔧"),
        st.Page(show_reservations_ui, title="Reservations", icon="📅"),
    ]

    pg = st.navigation(pages)
    pg.run()
    
    # Sidebar content
    _render_sidebar()


def _render_sidebar():
    """Render the sidebar with system status and quick info."""
    
    # System Status
    st.sidebar.caption("⚙️ System Status")
    
    if os.path.exists(Config.DB_PATH):
        st.sidebar.success("✅ Database Connected")
        
        # Quick stats
        from src.database.db_manager import DBManager
        try:
            db = DBManager()
            stats = db.get_statistics()
            
            st.sidebar.markdown("**Quick Stats:**")
            col1, col2 = st.sidebar.columns(2)
            col1.metric("Users", stats["total_users"], label_visibility="visible")
            col2.metric("Devices", stats["total_devices"], label_visibility="visible")
            
            # Alerts
            if stats["devices_needing_maintenance"] > 0:
                st.sidebar.warning(
                    f"⚠️ {stats['devices_needing_maintenance']} device(s) need maintenance"
                )
            
            if stats["upcoming_reservations"] > 0:
                st.sidebar.info(
                    f"📅 {stats['upcoming_reservations']} upcoming reservation(s)"
                )
        except Exception as e:
            logger.error(f"Error loading sidebar stats: {e}")
    else:
        st.sidebar.error("❌ Database Missing")
    
    # App info
    st.sidebar.markdown("---")
    st.sidebar.caption(f"{Config.APP_NAME}")
    st.sidebar.caption(f"Version {Config.APP_VERSION}")


if __name__ == "__main__":
    main()