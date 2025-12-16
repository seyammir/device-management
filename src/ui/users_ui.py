import streamlit as st
import pandas as pd
from src.database.db_manager import DBManager
from src.models.user import User

def show_users_ui() -> None:
    """
    Render the User Management interface.
    Allows adding new users and viewing the list of existing users.
    """
    db = DBManager()

    st.header("User Management")

    # Add New User
    st.subheader("Add New User")
    
    with st.form("add_user_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            user_id = st.text_input("User ID", placeholder="e.g. 123456 (Matriculation No.)")
        with col2:
            name_input = st.text_input("Full Name", placeholder="e.g. John Doe")
        with col3:
            email_input = st.text_input("Email", placeholder="e.g. dj1234@mci4me.at")
        
        submitted = st.form_submit_button("Register User")

        if submitted:
            if user_id and name_input and email_input:
                try:
                    new_user = User(user_id=user_id, name=name_input, email=email_input)
                    db.add_user(new_user)
                    st.success(f"User '{name_input}' (ID: {user_id}) added successfully!")
                except Exception as e:
                    st.error(f"Error adding user: {e}")
            else:
                st.warning("Please fill in all fields (ID, Name, and Email).")

    # List Users
    st.markdown("---")
    st.subheader("Existing Users")

    users = db.get_all_users()
    
    if users:
        user_data = [user.to_dict() for user in users]
        df = pd.DataFrame(user_data)
        
        # Rename columns for nicer display
        df = df.rename(columns={
            "user_id": "ID", 
            "name": "Full Name",
            "email": "Email Address"
        })
        
        st.dataframe(
            df, 
            width='stretch',
            hide_index=True
        )
    else:
        st.info("No users found. Add a user to get started.")