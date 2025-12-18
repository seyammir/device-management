import streamlit as st
import pandas as pd
from src.database.db_manager import DBManager

def show_dashboard_ui():
    st.header("Dashboard")
    
    db = DBManager()
    
    # Fetch data
    devices = db.get_all_devices()
    users = db.get_all_users()
    reservations = db.get_all_reservations()
    
    # Create user map for name lookup
    user_map = {u.user_id: u.name for u in users}
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Devices", len(devices))
    col2.metric("Total Users", len(users))
    col3.metric("Total Reservations", len(reservations))

    total_cost = sum(d.maintenance_cost for d in devices)
    col4.metric("Total Maint. Cost", f"€{total_cost:,.2f}")
    
    # Recent Activity or Quick Views
    st.subheader("Quick Overview")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Devices", "Recent Reservations", "Upcoming Maintenance", "Quarterly Costs"])
    
    with tab1:
        if devices:
            device_data = [{
                "Name": d.name, 
                "ID": d.id, 
                "Responsible": user_map.get(d.responsible_person_id, d.responsible_person_id),
                "Next Maint.": d.next_maintenance.date()
            } for d in devices]
            st.dataframe(pd.DataFrame(device_data), width='stretch')
        else:
            st.info("No devices found.")
            
    with tab2:
        if reservations:
            # Sort reservations by start time (descending)
            sorted_reservations = sorted(reservations, key=lambda x: x.start_time, reverse=True)
            res_data = [{
                "Device": next((d.name for d in devices if d.id == r.device_id), r.device_id),
                "User": user_map.get(r.user_id, r.user_id),
                "Start": r.start_time,
                "End": r.end_time
            } for r in sorted_reservations]
            st.dataframe(pd.DataFrame(res_data), width='stretch')
        else:
            st.info("No reservations found.")

    with tab3:
        if devices:
            # Sort by next maintenance date
            maint_devices = sorted(devices, key=lambda x: x.next_maintenance)
            maint_data = [{
                "Device": d.name,
                "Next Maintenance": d.next_maintenance.date(),
                "Cost": f"€{d.maintenance_cost:.2f}",
                "Interval (Days)": d.maintenance_interval
            } for d in maint_devices]
            st.dataframe(pd.DataFrame(maint_data), width='stretch')
        else:
            st.info("No devices found.")

    with tab4:
        # Calculate quarterly costs
        quarterly_costs = {}
        for d in devices:
            year = d.next_maintenance.year
            quarter = (d.next_maintenance.month - 1) // 3 + 1
            key = f"{year} Q{quarter}"
            quarterly_costs[key] = quarterly_costs.get(key, 0.0) + d.maintenance_cost
            
        if quarterly_costs:
            quarterly_data = [{"Quarter": k, "Total Cost (€)": v} for k, v in quarterly_costs.items()]
            df_quarterly = pd.DataFrame(quarterly_data).sort_values("Quarter")
            
            st.bar_chart(df_quarterly.set_index("Quarter"))
            st.dataframe(df_quarterly, width='stretch')
        else:
            st.info("No maintenance data available.")