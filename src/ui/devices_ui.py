import streamlit as st
from datetime import datetime, time
import pandas as pd
from src.database.db_manager import DBManager
from src.models.device import Device

def show_devices_ui() -> None:
    """
    Render the Device Management interface.
    Allows adding new devices and viewing the list of existing devices.
    """
    db = DBManager()
    st.header("🖨 Device Management")

    # Fetch users for the dropdown menu
    users = db.get_all_users()
    
    if not users:
        st.warning("⚠ No users found. Please add users in 'User Management' before adding devices.")
        return

    # Create a dictionary for the dropdown: "Name (ID)" -> user_id
    user_map = {f"{u.name} ({u.user_id})": u.user_id for u in users}

    # Add New Device
    st.subheader("Add New Device")
    
    with st.form("add_device_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            device_name = st.text_input("Device Name", placeholder="e.g. Prusa i3 MK3S+")
            device_id = st.text_input("Inventory ID", placeholder="e.g. INV-2023-001")
            responsible_user = st.selectbox("Responsible Person", options=list(user_map.keys()))
            
        with col2:
            maintenance_interval = st.number_input("Maintenance Interval (Days)", min_value=1, value=90)
            maintenance_cost = st.number_input("Maintenance Cost (€)", min_value=0.0, value=50.0, step=10.0)
            
        col3, col4 = st.columns(2)
        with col3:
            first_maint_date = st.date_input("First Maintenance Date", value=datetime.today())
        with col4:
            eol_date = st.date_input("End of Life Date", value=datetime.today().replace(year=datetime.today().year + 5))

        submitted = st.form_submit_button("Register Device")

        if submitted:
            if device_name and device_id and responsible_user:
                try:
                    # Convert date objects to datetime
                    first_maint_dt = datetime.combine(first_maint_date, time.min)
                    eol_dt = datetime.combine(eol_date, time.min)
                    
                    # Create Device Object
                    new_device = Device(
                        id=device_id,
                        name=device_name,
                        responsible_person_id=user_map[responsible_user],
                        end_of_life=eol_dt,
                        first_maintenance=first_maint_dt,
                        next_maintenance=first_maint_dt, # Initially same as first
                        maintenance_interval=int(maintenance_interval),
                        maintenance_cost=float(maintenance_cost)
                    )
                    
                    db.add_device(new_device)
                    st.success(f"Device '{device_name}' added successfully!")
                except Exception as e:
                    st.error(f"Error adding device: {e}")
            else:
                st.warning("Please fill in all required fields.")

    # List Devices
    st.markdown("---")
    st.subheader("Device Inventory")

    devices = db.get_all_devices()
    
    if devices:
        # Prepare data for display
        device_data = []
        for dev in devices:
            # Find the name of the responsible person
            
            resp_name = "Unknown"
            for name, uid in user_map.items():
                if uid == dev.responsible_person_id:
                    resp_name = name
                    break
            
            device_data.append({
                "ID": dev.id,
                "Name": dev.name,
                "Responsible": resp_name,
                "Next Maint.": dev.next_maintenance.strftime("%Y-%m-%d"),
                "Cost": f"€{dev.maintenance_cost:.2f}"
            })
            
        df = pd.DataFrame(device_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No devices found in inventory.")