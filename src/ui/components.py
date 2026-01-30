"""Shared UI components and utilities for the Device Management System."""
import json
import streamlit as st
import pandas as pd
from typing import List, Dict
from datetime import datetime

from src.core.utils import get_status_emoji


def apply_custom_css():
    """Apply custom CSS styling to the application."""
    st.markdown("""
        <style>
        /* Card-like containers - using CSS variables for theme compatibility */
        .stMetric {
            background-color: var(--secondary-background-color, rgba(128, 128, 128, 0.1));
            padding: 15px;
            border-radius: 10px;
        }
        
        /* Tabs - theme aware */
        .stTabs [data-baseweb="tab-list"] {
            background-color: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
        }
        .stTabs [data-baseweb="tab-panel"] {
            background-color: transparent;
        }
        
        /* Status badges */
        .status-badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
        }
        .status-active { background-color: #d4edda; color: #155724; }
        .status-maintenance { background-color: #fff3cd; color: #856404; }
        .status-retired { background-color: #f8d7da; color: #721c24; }
        .status-overdue { background-color: #f8d7da; color: #721c24; }
        .status-upcoming { background-color: #fff3cd; color: #856404; }
        .status-ok { background-color: #d4edda; color: #155724; }
        
        /* Better button styling */
        .stButton > button {
            border-radius: 8px;
        }
        
        /* Info cards - theme aware */
        .info-card {
            background-color: var(--secondary-background-color, rgba(128, 128, 128, 0.1));
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }
        
        /* Section headers */
        .section-header {
            border-bottom: 2px solid var(--secondary-background-color, #e0e0e0);
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)


def show_status_badge(status: str) -> str:
    """Generate HTML for a status badge."""
    emoji = get_status_emoji(status)
    return f"{emoji} {status.title()}"


def show_success_message(message: str):
    """Show a success message."""
    st.success(f"✅ {message}")


def show_error_message(message: str):
    """Show an error message."""
    st.error(f"❌ {message}")


def show_warning_message(message: str):
    """Show a warning message."""
    st.warning(f"⚠️ {message}")


def create_export_buttons(
    data: List[Dict],
    filename_prefix: str,
    key: str
) -> None:
    """Create export buttons for data."""
    if not data:
        return
    
    # CSV export
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    
    # JSON export
    json_data = json.dumps(data, indent=2, default=str)
    
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        st.download_button(
            label="📥 CSV",
            data=csv,
            file_name=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key=f"{key}_csv",
            use_container_width=True
        )
    
    with col2:
        st.download_button(
            label="📥 JSON",
            data=json_data,
            file_name=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            key=f"{key}_json",
            use_container_width=True
        )


def show_empty_state(
    title: str,
    message: str,
    icon: str = "📭"
) -> None:
    """Show an empty state message."""
    st.markdown(f"""
        <div style="text-align: center; padding: 40px;">
            <h1 style="font-size: 3em;">{icon}</h1>
            <h3>{title}</h3>
            <p style="color: #666;">{message}</p>
        </div>
    """, unsafe_allow_html=True)
