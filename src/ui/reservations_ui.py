import streamlit as st
import pandas as pd
from datetime import datetime, time
from src.database.db_manager import DBManager
from src.models.reservation import Reservation

def show_reservations_ui() -> None:
    """
    Render the Reservation System interface.
    Allows creating new reservations with conflict checking.
    """
    db = DBManager()
    st.header("Reservation System")

    # Fetch Helper Data
    devices = db.get_all_devices()
    users = db.get_all_users()

    if not devices or not users:
        st.warning("Please add both Users and Devices before making reservations.")
        return

    # Map for Dropdowns
    device_map = {f"{d.name} ({d.id})": d.id for d in devices}
    user_map = {f"{u.name} ({u.user_id})": u.user_id for u in users}

    # Initialize session state for times if they don't exist yet
    # This allows the form to remember the last entered time
    if "res_start_time" not in st.session_state:
        st.session_state["res_start_time"] = time(9, 0)
    if "res_end_time" not in st.session_state:
        st.session_state["res_end_time"] = time(10, 0)

    # Add New Reservation Form
    st.subheader("Book a Device")
    
    with st.form("add_reservation_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            selected_device_key = st.selectbox("Select Device", options=list(device_map.keys()))
            selected_user_key = st.selectbox("Reserved By", options=list(user_map.keys()))
        
        with col2:
            date_col, time_col = st.columns(2)
            with date_col:
                res_date = st.date_input("Date", min_value=datetime.today())
            with time_col:
                start_time = st.time_input("Start Time", value=st.session_state["res_start_time"]) 
                end_time = st.time_input("End Time", value=st.session_state["res_end_time"])

        submitted = st.form_submit_button("Confirm Reservation")

        if submitted:
            # Update session state to remember these times for the next entry
            st.session_state["res_start_time"] = start_time
            st.session_state["res_end_time"] = end_time

            # Reconstruct Datetime objects
            start_dt = datetime.combine(res_date, start_time)
            end_dt = datetime.combine(res_date, end_time)

            # Validation 1: Logical Time
            if start_dt >= end_dt:
                st.error("Error: End time must be after start time.")
            else:
                # Validation 2: Availability Check
                device_id = device_map[selected_device_key]
                user_id = user_map[selected_user_key]
                
                if is_device_available(db, device_id, start_dt, end_dt):
                    reservation = Reservation.create_new(
                        device_id=device_id,
                        user_id=user_id,
                        start=start_dt,
                        end=end_dt
                    )
                    db.add_reservation(reservation)
                    st.success("Reservation confirmed successfully!")
                else:
                    st.error("Conflict: The device is already booked for this time slot.")

    # 3. List Reservations
    st.markdown("---")
    st.subheader("Current Reservations")
    
    all_reservations = []
    for dev in devices:
        res_list = db.get_reservations_by_device(dev.id)
        for res in res_list:
            dev_name = dev.name
            user_name = "Unknown"
            for u in users:
                if u.user_id == res.user_id:
                    user_name = u.name
                    break
            
            all_reservations.append({
                "Device": dev_name,
                "User": user_name,
                "Start": res.start_time.strftime("%Y-%m-%d %H:%M"),
                "End": res.end_time.strftime("%H:%M"),
                "DateObj": res.start_time # Hidden column for sorting
            })

    if all_reservations:
        df = pd.DataFrame(all_reservations)
        df = df.sort_values(by="DateObj", ascending=False)
        df = df.drop(columns=["DateObj"]) # Remove helper column
        
        st.dataframe(df, width='stretch', hide_index=True)
    else:
        st.info("No active reservations found.")

def is_device_available(db: DBManager, device_id: str, start: datetime, end: datetime) -> bool:
    """
    Checks if a device is free during the requested time slot.
    Returns True if available, False if there is a conflict.
    """
    existing_reservations = db.get_reservations_by_device(device_id)
    
    for res in existing_reservations:
        # Overlap Logic: (StartA < EndB) and (EndA > StartB)
        if start < res.end_time and end > res.start_time:
            return False
            
    return True