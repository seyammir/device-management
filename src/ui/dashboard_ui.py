import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.database.db_manager import DBManager
from src.ui.components import (
    apply_custom_css,
    show_status_badge,
    create_export_buttons,
    show_empty_state
)
from src.core.utils import (
    format_currency, 
    get_status_emoji, 
    format_date, 
    format_time,
    create_device_id_to_name_map,
    create_user_id_to_name_map,
)


def show_dashboard_ui():
    """Display the main dashboard with system overview and analytics."""
    apply_custom_css()
    st.header("📊 Dashboard")
    
    db = DBManager()
    
    # Fetch data
    devices = db.get_all_devices()
    users = db.get_all_users()
    reservations = db.get_all_reservations()
    stats = db.get_statistics()
    
    # Create lookup maps using utility functions
    user_map = create_user_id_to_name_map(users)
    device_map = create_device_id_to_name_map(devices)
    
    # Top Metrics Row
    st.subheader("📈 System Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "👥 Total Users", 
            stats["total_users"],
            delta=f"{stats['active_users']} active"
        )
    
    with col2:
        st.metric(
            "🔧 Total Devices", 
            stats["total_devices"],
            delta=f"{stats['active_devices']} active"
        )
    
    with col3:
        st.metric(
            "📅 Reservations", 
            stats["total_reservations"],
            delta=f"{stats['upcoming_reservations']} upcoming"
        )
    
    with col4:
        st.metric(
            "💰 Total Maint. Cost", 
            format_currency(stats["total_maintenance_cost"])
        )
    
    # Alert Section
    maintenance_needed = db.get_devices_needing_maintenance()
    if maintenance_needed:
        st.markdown("---")
        with st.expander(f"🚨 Maintenance Alerts ({len(maintenance_needed)} devices)", expanded=True):
            for device in maintenance_needed:
                status = device.maintenance_status
                emoji = get_status_emoji(status)
                days = device.days_until_maintenance
                
                if status == "overdue":
                    st.error(f"{emoji} **{device.name}** - Maintenance overdue by {abs(days)} days!")
                else:
                    st.warning(f"{emoji} **{device.name}** - Maintenance due in {days} days")
    
    # Main Content Tabs
    st.markdown("---")
    st.subheader("📋 Quick Overview")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📱 Devices", 
        "📅 Recent Reservations", 
        "🔧 Maintenance Schedule", 
        "💵 Cost Analysis",
        "📊 Statistics"
    ])
    
    with tab1:
        _show_devices_overview(devices, user_map)
    
    with tab2:
        _show_reservations_overview(reservations, devices, user_map, device_map)
    
    with tab3:
        _show_maintenance_schedule(devices, user_map)
    
    with tab4:
        _show_cost_analysis(devices)
    
    with tab5:
        _show_statistics(stats, devices, reservations, users)


def _show_devices_overview(devices, user_map):
    """Show devices overview tab."""
    if not devices:
        show_empty_state(
            "No Devices",
            "Add devices in the Device Management section.",
            "📱"
        )
        return
    
    # Filter options
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("🔍 Search devices", key="dash_device_search")
    with col2:
        status_filter = st.selectbox(
            "Status",
            ["All", "active", "maintenance", "retired"],
            key="dash_device_status"
        )
    
    # Filter devices
    filtered_devices = devices
    if search:
        filtered_devices = [d for d in filtered_devices if search.lower() in d.name.lower()]
    if status_filter != "All":
        filtered_devices = [d for d in filtered_devices if d.status == status_filter]
    
    device_data = [{
        "Status": show_status_badge(d.status),
        "Name": d.name,
        "ID": d.id,
        "Location": d.location or "N/A",
        "Responsible": user_map.get(d.responsible_person_id, "Unknown"),
        "Maintenance": show_status_badge(d.maintenance_status),
        "Next Maint.": format_date(d.next_maintenance)
    } for d in filtered_devices]
    
    st.dataframe(pd.DataFrame(device_data), width='stretch', hide_index=True)
    
    # Export
    export_data = [d.to_dict() for d in filtered_devices]
    create_export_buttons(export_data, "devices", "dash_devices_export")


def _show_reservations_overview(reservations, devices, user_map, device_map):
    """Show recent reservations overview."""
    if not reservations:
        show_empty_state(
            "No Reservations",
            "Book devices in the Reservations section.",
            "📅"
        )
        return
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        time_filter = st.selectbox(
            "Time Period",
            ["All", "Today", "This Week", "Upcoming", "Past"],
            key="dash_res_time"
        )
    with col2:
        device_filter = st.selectbox(
            "Device",
            ["All"] + list(device_map.values()),
            key="dash_res_device"
        )
    
    # Filter reservations
    now = datetime.now()
    filtered_res = reservations
    
    if time_filter == "Today":
        filtered_res = [r for r in filtered_res if r.start_time.date() == now.date()]
    elif time_filter == "This Week":
        week_end = now + timedelta(days=7)
        filtered_res = [r for r in filtered_res if now.date() <= r.start_time.date() <= week_end.date()]
    elif time_filter == "Upcoming":
        filtered_res = [r for r in filtered_res if r.is_upcoming]
    elif time_filter == "Past":
        filtered_res = [r for r in filtered_res if r.is_past]
    
    if device_filter != "All":
        device_id = next((k for k, v in device_map.items() if v == device_filter), None)
        if device_id:
            filtered_res = [r for r in filtered_res if r.device_id == device_id]
    
    # Sort by start time (descending)
    sorted_reservations = sorted(filtered_res, key=lambda x: x.start_time, reverse=True)
    
    res_data = [{
        "Status": show_status_badge(r.status),
        "Device": device_map.get(r.device_id, r.device_id),
        "User": user_map.get(r.user_id, r.user_id),
        "Date": format_date(r.start_time),
        "Time": f"{format_time(r.start_time)} - {format_time(r.end_time)}",
        "Duration": f"{r.duration_hours:.1f}h",
        "Purpose": r.purpose or "N/A"
    } for r in sorted_reservations[:50]]  # Limit to 50 most recent
    
    st.dataframe(pd.DataFrame(res_data), width='stretch', hide_index=True)


def _show_maintenance_schedule(devices, user_map):
    """Show maintenance schedule."""
    if not devices:
        show_empty_state("No Devices", "Add devices to see maintenance schedule.", "🔧")
        return
    
    # Sort by next maintenance date
    maint_devices = sorted(devices, key=lambda x: x.next_maintenance)
    
    maint_data = [{
        "Status": show_status_badge(d.maintenance_status),
        "Device": d.name,
        "Next Maintenance": format_date(d.next_maintenance),
        "Days Until": d.days_until_maintenance,
        "Responsible": user_map.get(d.responsible_person_id, "Unknown"),
        "Cost": format_currency(d.maintenance_cost),
        "Interval (Days)": d.maintenance_interval
    } for d in maint_devices]
    
    st.dataframe(pd.DataFrame(maint_data), width='stretch', hide_index=True)


def _show_cost_analysis(devices):
    """Show cost analysis and charts."""
    if not devices:
        show_empty_state("No Devices", "Add devices to see cost analysis.", "💵")
        return
    
    # Calculate quarterly costs
    quarterly_costs = {}
    monthly_costs = {}
    
    for d in devices:
        # Calculate expected maintenance occurrences
        year = d.next_maintenance.year
        quarter = (d.next_maintenance.month - 1) // 3 + 1
        month_key = d.next_maintenance.strftime("%Y-%m")
        quarter_key = f"{year} Q{quarter}"
        
        quarterly_costs[quarter_key] = quarterly_costs.get(quarter_key, 0.0) + d.maintenance_cost
        monthly_costs[month_key] = monthly_costs.get(month_key, 0.0) + d.maintenance_cost
    
    # Quarterly bar chart
    if quarterly_costs:
        st.subheader("📊 Quarterly Maintenance Costs")
        quarterly_data = pd.DataFrame([
            {"Quarter": k, "Cost (€)": v} 
            for k, v in sorted(quarterly_costs.items())
        ])
        st.bar_chart(quarterly_data.set_index("Quarter"))
        
        # Summary table
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(quarterly_data, width='stretch', hide_index=True)
        with col2:
            st.metric("Total Quarterly", format_currency(sum(quarterly_costs.values())))
            st.metric("Average per Quarter", format_currency(sum(quarterly_costs.values()) / len(quarterly_costs)))
    
    # Cost by device
    st.subheader("💰 Cost by Device")
    cost_by_device = pd.DataFrame([
        {"Device": d.name, "Maintenance Cost (€)": d.maintenance_cost}
        for d in sorted(devices, key=lambda x: x.maintenance_cost, reverse=True)
    ])
    st.bar_chart(cost_by_device.set_index("Device"))


def _show_statistics(stats, devices, reservations, users):
    """Show detailed statistics."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 User Statistics")
        st.write(f"- Total Users: **{stats['total_users']}**")
        st.write(f"- Active Users: **{stats['active_users']}**")
        
        # Department distribution
        dept_counts = {}
        for u in users:
            dept = u.department or "Unassigned"
            dept_counts[dept] = dept_counts.get(dept, 0) + 1
        if dept_counts:
            st.write("**Department Distribution:**")
            for dept, count in dept_counts.items():
                st.write(f"  - {dept}: {count}")
    
    with col2:
        st.subheader("📱 Device Statistics")
        st.write(f"- Total Devices: **{stats['total_devices']}**")
        st.write(f"- Active Devices: **{stats['active_devices']}**")
        st.write(f"- Needing Maintenance: **{stats['devices_needing_maintenance']}**")
        
        # Status distribution
        status_counts = {}
        for d in devices:
            status_counts[d.status] = status_counts.get(d.status, 0) + 1
        if status_counts:
            st.write("**Status Distribution:**")
            for status, count in status_counts.items():
                st.write(f"  - {get_status_emoji(status)} {status.title()}: {count}")
    
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("📅 Reservation Statistics")
        st.write(f"- Total Reservations: **{stats['total_reservations']}**")
        st.write(f"- Upcoming: **{stats['upcoming_reservations']}**")
        st.write(f"- Currently Active: **{stats['active_reservations']}**")
        
        # Status distribution
        res_status_counts = {}
        for r in reservations:
            res_status_counts[r.status] = res_status_counts.get(r.status, 0) + 1
        if res_status_counts:
            st.write("**Status Distribution:**")
            for status, count in res_status_counts.items():
                st.write(f"  - {get_status_emoji(status)} {status.title()}: {count}")
    
    with col4:
        st.subheader("💰 Financial Summary")
        st.write(f"- Total Maintenance Cost: **{format_currency(stats['total_maintenance_cost'])}**")
        if devices:
            avg_cost = stats['total_maintenance_cost'] / len(devices)
            st.write(f"- Average per Device: **{format_currency(avg_cost)}**")