import streamlit as st
import pandas as pd
import time as tm
from src.database.db_manager import DBManager
from src.models.user import User, UserValidationError
from src.ui.components import (
    apply_custom_css,
    create_export_buttons,
    show_empty_state,
    show_success_message,
    show_error_message,
    show_warning_message
)
from src.core.utils import format_date

def show_users_ui() -> None:
    """
    Render the User Management interface with full CRUD operations.
    """
    apply_custom_css()
    db = DBManager()

    st.header("👥 User Management")

    # Tab layout for different operations
    tab1, tab2, tab3 = st.tabs(["📋 User List", "➕ Add User", "✏️ Edit User"])
    
    with tab1:
        _show_users_list(db)
    
    with tab2:
        _show_add_user_form(db)
    
    with tab3:
        _show_edit_user_form(db)


def _show_users_list(db: DBManager) -> None:
    """Display the list of users with search and filter options."""
    users = db.get_all_users()
    
    if not users:
        show_empty_state(
            "No Users Found",
            "Add your first user using the 'Add User' tab.",
            "👤"
        )
        return
    
    # Search and Filter Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 Search",
            placeholder="Search by name or email...",
            key="user_search"
        )
    
    with col2:
        status_filter = st.selectbox(
            "Status",
            ["All", "Active", "Inactive"],
            key="user_status_filter"
        )
    
    # Apply filters
    filtered_users = users
    
    if search_query:
        search_lower = search_query.lower()
        filtered_users = [
            u for u in filtered_users 
            if search_lower in u.name.lower() or search_lower in u.email.lower()
        ]
    
    if status_filter == "Active":
        filtered_users = [u for u in filtered_users if u.is_active]
    elif status_filter == "Inactive":
        filtered_users = [u for u in filtered_users if not u.is_active]
    
    # Display results count
    st.caption(f"Showing {len(filtered_users)} of {len(users)} users")
    
    # Display users in a dataframe
    if filtered_users:
        user_data = [{
            "Status": "✅ Active" if u.is_active else "❌ Inactive",
            "ID": u.user_id,
            "Name": u.name,
            "Email": u.email,
            "Phone": u.phone or "N/A",
            "Department": u.department or "N/A",
            "Created": format_date(u.created_at)
        } for u in filtered_users]
        
        st.dataframe(
            pd.DataFrame(user_data),
            width='stretch',
            hide_index=True
        )
        
        # Export Options
        export_data = [u.to_dict() for u in filtered_users]
        create_export_buttons(export_data, "users", "users_export")
    else:
        st.info("No users match your search criteria.")


def _show_add_user_form(db: DBManager) -> None:
    """Display form for adding a new user."""
    
    with st.form("add_user_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            user_id = st.text_input(
                "User ID *",
                placeholder="e.g. 123456 (Matriculation No.)",
                help="Unique identifier for the user"
            )
            name_input = st.text_input(
                "Full Name *",
                placeholder="e.g. John Doe"
            )
            email_input = st.text_input(
                "Email *",
                placeholder="e.g. john.doe@mci4me.at"
            )
        
        with col2:
            phone_input = st.text_input(
                "Phone",
                placeholder="e.g. +43 123 456789"
            )
            department_input = st.text_input(
                "Department",
                placeholder="e.g. Engineering"
            )
        
        st.markdown("*Required fields*")
        
        submitted = st.form_submit_button("➕ Register User", type="primary")

        if submitted:
            if not user_id or not name_input or not email_input:
                show_warning_message("Please fill in all required fields (ID, Name, and Email).")
            else:
                # Check if user already exists
                existing = db.get_user(user_id)
                if existing:
                    show_error_message(f"A user with ID '{user_id}' already exists.")
                else:
                    try:
                        new_user = User(
                            user_id=user_id.strip(),
                            name=name_input.strip(),
                            email=email_input.strip(),
                            phone=phone_input.strip(),
                            department=department_input.strip()
                        )
                        db.add_user(new_user)
                        show_success_message(f"User '{name_input}' (ID: {user_id}) added successfully!")
                        tm.sleep(1)
                        st.rerun()
                    except UserValidationError as e:
                        show_error_message(f"Validation error: {e}")
                    except Exception as e:
                        show_error_message(f"Error adding user: {e}")


def _show_edit_user_form(db: DBManager) -> None:
    """Display form for editing an existing user."""

    users = db.get_all_users()
    
    if not users:
        st.info("No users available to edit. Add users first.")
        return
    
    # User selection
    selected_user = st.selectbox(
        "Select User to Edit",
        options=users,
        format_func=lambda u: f"{u.name} ({u.user_id})",
        key="edit_user_select"
    )
    
    if selected_user:
        
        with st.form("edit_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input(
                    "User ID",
                    value=selected_user.user_id,
                    disabled=True,
                    help="User ID cannot be changed"
                )
                name_input = st.text_input(
                    "Full Name *",
                    value=selected_user.name
                )
                email_input = st.text_input(
                    "Email *",
                    value=selected_user.email
                )
            
            with col2:
                phone_input = st.text_input(
                    "Phone",
                    value=selected_user.phone
                )
                department_input = st.text_input(
                    "Department",
                    value=selected_user.department
                )
            
            is_active = st.checkbox(
                "Active",
                value=selected_user.is_active,
                help="Inactive users cannot make reservations"
            )
            
            submitted = st.form_submit_button("💾 Save Changes", type="primary")
            
            if submitted:
                try:
                    db.update_user(
                        selected_user.user_id,
                        name=name_input.strip(),
                        email=email_input.strip(),
                        phone=phone_input.strip(),
                        department=department_input.strip(),
                        is_active=is_active
                    )
                    show_success_message(f"User '{name_input}' updated successfully!")
                    tm.sleep(1)
                    st.rerun()
                except UserValidationError as e:
                    show_error_message(f"Validation error: {e}")
                except Exception as e:
                    show_error_message(f"Error updating user: {e}")
        
        # Delete Section
        st.subheader("🗑️ Delete User")
        
        st.warning(f"⚠️ You are about to delete user: **{selected_user.name}** ({selected_user.user_id})")
        
        # Check for dependencies
        reservations = db.get_reservations_by_user(selected_user.user_id)
        devices = [d for d in db.get_all_devices() if d.responsible_person_id == selected_user.user_id]
        
        if devices:
            st.error(
                f"❌ Cannot delete: User is responsible for {len(devices)} device(s). "
                "Reassign devices first."
            )
        else:
            if reservations:
                st.info(f"ℹ️ Note: {len(reservations)} associated reservation(s) will also be removed.")
            
            if st.button("🗑️ Delete User", type="primary", key="delete_user_btn"):
                db.delete_user(selected_user.user_id)
                show_success_message(f"User '{selected_user.name}' deleted successfully!")
                tm.sleep(1)
                st.rerun()