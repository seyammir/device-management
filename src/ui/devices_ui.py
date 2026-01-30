import streamlit as st
from datetime import datetime, time, timedelta
import time as tm
import pandas as pd
from src.database.db_manager import DBManager
from src.models.device import Device, DeviceValidationError
from src.ui.components import (
    apply_custom_css,
    show_status_badge,
    create_export_buttons,
    show_empty_state,
    show_success_message,
    show_error_message,
    show_warning_message
)
from src.core.config import Config
from src.core.utils import (
    format_currency, 
    get_status_emoji, 
    format_date,
    date_to_datetime,
    create_user_map,
    create_user_id_to_name_map,
)


def show_devices_ui() -> None:
    """
    Render the Device Management interface with full CRUD operations.
    """
    apply_custom_css()
    db = DBManager()
    st.header("🔧 Device Management")

    # Fetch users for the dropdown menu
    users = db.get_all_users()
    
    if not users:
        show_warning_message("No users found. Please add users in 'User Management' before adding devices.")
        return

    # Create lookup maps using utility functions
    user_map = create_user_map(users)
    user_id_to_name = create_user_id_to_name_map(users)

    # Tab layout for different operations
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Device List", 
        "➕ Add Device", 
        "✏️ Edit Device",
        "🔧 Maintenance"
    ])
    
    with tab1:
        _show_devices_list(db, user_id_to_name)
    
    with tab2:
        _show_add_device_form(db, user_map)
    
    with tab3:
        _show_edit_device_form(db, user_map, user_id_to_name)
    
    with tab4:
        _show_maintenance_section(db, user_id_to_name)


def _show_devices_list(db: DBManager, user_id_to_name: dict) -> None:
    """Display the list of devices with search and filter options."""
    devices = db.get_all_devices()
    
    if not devices:
        show_empty_state(
            "No Devices Found",
            "Add your first device using the 'Add Device' tab.",
            "📱"
        )
        return
    
    # Search and Filter Section
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 Search",
            placeholder="Search by name, ID, or location...",
            key="device_search"
        )
    
    with col2:
        status_filter = st.selectbox(
            "Status",
            ["All"] + Config.DEVICE_STATUSES,
            key="device_status_filter"
        )
    
    with col3:
        maint_filter = st.selectbox(
            "Maintenance",
            ["All", "Overdue", "Upcoming (7 days)", "OK"],
            key="device_maint_filter"
        )
    
    with col4:
        sort_by = st.selectbox(
            "Sort by",
            ["Name", "Next Maintenance", "Cost", "Location"],
            key="device_sort"
        )
    
    # Apply filters
    filtered_devices = devices
    
    if search_query:
        search_lower = search_query.lower()
        filtered_devices = [
            d for d in filtered_devices 
            if search_lower in d.name.lower() 
            or search_lower in d.id.lower()
            or search_lower in d.location.lower()
        ]
    
    if status_filter != "All":
        filtered_devices = [d for d in filtered_devices if d.status == status_filter]
    
    if maint_filter == "Overdue":
        filtered_devices = [d for d in filtered_devices if d.maintenance_status == "overdue"]
    elif maint_filter == "Upcoming (7 days)":
        filtered_devices = [d for d in filtered_devices if d.maintenance_status == "upcoming"]
    elif maint_filter == "OK":
        filtered_devices = [d for d in filtered_devices if d.maintenance_status == "ok"]
    
    # Sort devices
    if sort_by == "Name":
        filtered_devices = sorted(filtered_devices, key=lambda d: d.name.lower())
    elif sort_by == "Next Maintenance":
        filtered_devices = sorted(filtered_devices, key=lambda d: d.next_maintenance)
    elif sort_by == "Cost":
        filtered_devices = sorted(filtered_devices, key=lambda d: d.maintenance_cost, reverse=True)
    elif sort_by == "Location":
        filtered_devices = sorted(filtered_devices, key=lambda d: d.location.lower())
    
    # Display results count
    st.caption(f"Showing {len(filtered_devices)} of {len(devices)} devices")
    
    # Display devices in a dataframe
    if filtered_devices:
        device_data = [{
            "Status": show_status_badge(d.status),
            "ID": d.id,
            "Name": d.name,
            "Location": d.location or "N/A",
            "Responsible": user_id_to_name.get(d.responsible_person_id, "Unknown"),
            "Maintenance": show_status_badge(d.maintenance_status),
            "Next Maint.": format_date(d.next_maintenance),
            "Days": d.days_until_maintenance,
            "Cost": format_currency(d.maintenance_cost)
        } for d in filtered_devices]
        
        st.dataframe(
            pd.DataFrame(device_data),
            width='stretch',
            hide_index=True
        )
        
        # Export Options
        export_data = [d.to_dict() for d in filtered_devices]
        create_export_buttons(export_data, "devices", "devices_export")
    else:
        st.info("No devices match your search criteria.")


def _show_add_device_form(db: DBManager, user_map: dict) -> None:
    """Display form for adding a new device."""
    
    with st.form("add_device_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            device_name = st.text_input(
                "Device Name *",
                placeholder="e.g. Prusa i3 MK3S+"
            )
            device_id = st.text_input(
                "Inventory ID *",
                placeholder="e.g. INV-2023-001"
            )
            responsible_user = st.selectbox(
                "Responsible Person *",
                options=list(user_map.keys())
            )
            location = st.text_input(
                "Location",
                placeholder="e.g. Lab A, Room 101"
            )
        
        with col2:
            description = st.text_area(
                "Description",
                placeholder="Device description and notes...",
                height=100
            )
            tags_input = st.text_input(
                "Tags (comma-separated)",
                placeholder="e.g. 3D printing, prototyping"
            )
            status = st.selectbox(
                "Status",
                options=Config.DEVICE_STATUSES,
                format_func=lambda x: f"{get_status_emoji(x)} {x.title()}"
            )
        
        st.markdown("#### Maintenance Settings")
        col3, col4 = st.columns(2)
        
        with col3:
            maintenance_interval = st.number_input(
                "Maintenance Interval (Days)",
                min_value=1,
                value=90
            )
            maintenance_cost = st.number_input(
                "Maintenance Cost (€)",
                min_value=0.0,
                value=50.0,
                step=10.0
            )
        
        with col4:
            first_maint_date = st.date_input(
                "First Maintenance Date",
                value=datetime.today() + timedelta(days=90)
            )
            eol_date = st.date_input(
                "End of Life Date",
                value=datetime.today().replace(year=datetime.today().year + 5)
            )
        
        st.markdown("*Required fields")
        
        submitted = st.form_submit_button("➕ Register Device", type="primary")

        if submitted:
            if not device_name or not device_id or not responsible_user:
                show_warning_message("Please fill in all required fields.")
            else:
                # Check if device already exists
                existing = db.get_device(device_id)
                if existing:
                    show_error_message(f"A device with ID '{device_id}' already exists.")
                else:
                    try:
                        # Parse tags
                        tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []
                        
                        # Convert date objects to datetime
                        first_maint_dt = date_to_datetime(first_maint_date)
                        eol_dt = date_to_datetime(eol_date)
                        
                        new_device = Device(
                            id=device_id.strip(),
                            name=device_name.strip(),
                            responsible_person_id=user_map[responsible_user],
                            end_of_life=eol_dt,
                            first_maintenance=first_maint_dt,
                            next_maintenance=first_maint_dt,
                            maintenance_interval=int(maintenance_interval),
                            maintenance_cost=float(maintenance_cost),
                            description=description.strip(),
                            location=location.strip(),
                            status=status,
                            tags=tags
                        )
                        
                        db.add_device(new_device)
                        show_success_message(f"Device '{device_name}' added successfully!")
                        tm.sleep(1)
                        st.rerun()
                    except DeviceValidationError as e:
                        show_error_message(f"Validation error: {e}")
                    except Exception as e:
                        show_error_message(f"Error adding device: {e}")


def _show_edit_device_form(db: DBManager, user_map: dict, user_id_to_name: dict) -> None:
    """Display form for editing an existing device."""
    
    devices = db.get_all_devices()
    
    if not devices:
        st.info("No devices available to edit. Add devices first.")
        return
    
    # Device selection
    selected_device = st.selectbox(
        "Select Device to Edit",
        options=devices,
        format_func=lambda d: f"{d.name} ({d.id})",
        key="edit_device_select"
    )
    
    if selected_device:
        
        # Get the current responsible user key
        current_resp_key = user_id_to_name.get(
            selected_device.responsible_person_id, 
            list(user_map.keys())[0]
        )
        
        with st.form("edit_device_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input(
                    "Inventory ID",
                    value=selected_device.id,
                    disabled=True
                )
                device_name = st.text_input(
                    "Device Name *",
                    value=selected_device.name
                )
                responsible_user = st.selectbox(
                    "Responsible Person *",
                    options=list(user_map.keys()),
                    index=list(user_map.keys()).index(current_resp_key) if current_resp_key in user_map.keys() else 0
                )
                location = st.text_input(
                    "Location",
                    value=selected_device.location
                )
            
            with col2:
                description = st.text_area(
                    "Description",
                    value=selected_device.description,
                    height=100
                )
                tags_input = st.text_input(
                    "Tags (comma-separated)",
                    value=", ".join(selected_device.tags)
                )
                status = st.selectbox(
                    "Status",
                    options=Config.DEVICE_STATUSES,
                    index=Config.DEVICE_STATUSES.index(selected_device.status),
                    format_func=lambda x: f"{get_status_emoji(x)} {x.title()}"
                )
            
            st.markdown("#### Maintenance Settings")
            col3, col4 = st.columns(2)
            
            with col3:
                maintenance_interval = st.number_input(
                    "Maintenance Interval (Days)",
                    min_value=1,
                    value=selected_device.maintenance_interval
                )
                maintenance_cost = st.number_input(
                    "Maintenance Cost (€)",
                    min_value=0.0,
                    value=float(selected_device.maintenance_cost),
                    step=10.0
                )
            
            with col4:
                next_maint_date = st.date_input(
                    "Next Maintenance Date",
                    value=selected_device.next_maintenance.date()
                )
                eol_date = st.date_input(
                    "End of Life Date",
                    value=selected_device.end_of_life.date()
                )
            
            submitted = st.form_submit_button("💾 Save Changes", type="primary")
            
            if submitted:
                try:
                    tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []
                    next_maint_dt = date_to_datetime(next_maint_date)
                    eol_dt = date_to_datetime(eol_date)
                    
                    db.update_device(
                        selected_device.id,
                        name=device_name.strip(),
                        responsible_person_id=user_map[responsible_user],
                        description=description.strip(),
                        location=location.strip(),
                        status=status,
                        tags=tags,
                        maintenance_interval=int(maintenance_interval),
                        maintenance_cost=float(maintenance_cost),
                        next_maintenance=next_maint_dt,
                        end_of_life=eol_dt
                    )
                    show_success_message(f"Device '{device_name}' updated successfully!")
                    tm.sleep(1)
                    st.rerun()
                except DeviceValidationError as e:
                    show_error_message(f"Validation error: {e}")
                except Exception as e:
                    show_error_message(f"Error updating device: {e}")
        
        # Delete Section
        st.subheader("🗑️ Delete Device")
        
        st.warning(f"⚠️ You are about to delete device: **{selected_device.name}** ({selected_device.id})")
        
        # Check for active reservations
        reservations = db.get_reservations_by_device(selected_device.id)
        upcoming = [r for r in reservations if r.is_upcoming]
        
        if upcoming:
            st.info(f"ℹ️ Note: {len(upcoming)} upcoming reservation(s) will also be removed.")
        
        if st.button("🗑️ Delete Device", type="primary", key="delete_device_btn"):
            db.delete_device(selected_device.id)
            show_success_message(f"Device '{selected_device.name}' deleted successfully!")
            tm.sleep(1)
            st.rerun()


def _show_maintenance_section(db: DBManager, user_id_to_name: dict) -> None:
    """Display maintenance management section."""
    
    devices = db.get_all_devices()
    
    if not devices:
        st.info("No devices available.")
        return
    
    # Maintenance overview
    overdue = [d for d in devices if d.maintenance_status == "overdue"]
    upcoming = [d for d in devices if d.maintenance_status == "upcoming"]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🚨 Overdue", len(overdue))
    with col2:
        st.metric("⚠️ Upcoming (7 days)", len(upcoming))
    with col3:
        st.metric("✅ OK", len(devices) - len(overdue) - len(upcoming))
    
    # Devices needing maintenance
    needs_attention = sorted(overdue + upcoming, key=lambda d: d.next_maintenance)
    
    if needs_attention:
        st.markdown("#### Devices Needing Attention")
        
        for device in needs_attention:
            emoji = "🚨" if device.maintenance_status == "overdue" else "⚠️"
            days = device.days_until_maintenance
            days_text = f"{abs(days)} days overdue" if days < 0 else f"Due in {days} days"
            
            with st.expander(f"{emoji} {device.name} - {days_text}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**ID:** {device.id}")
                    st.write(f"**Location:** {device.location or 'N/A'}")
                    st.write(f"**Responsible:** {user_id_to_name.get(device.responsible_person_id, 'Unknown')}")
                with col2:
                    st.write(f"**Next Maintenance:** {format_date(device.next_maintenance)}")
                    st.write(f"**Cost:** {format_currency(device.maintenance_cost)}")
                    st.write(f"**Interval:** {device.maintenance_interval} days")
                
                if st.button(
                    "✅ Mark Maintenance Complete",
                    key=f"complete_maint_{device.id}"
                ):
                    device.schedule_next_maintenance()
                    db.add_device(device)
                    show_success_message(
                        f"Maintenance completed! Next maintenance scheduled for "
                        f"{format_date(device.next_maintenance)}"
                    )
                    tm.sleep(1)
                    st.rerun()
    else:
        st.success("✅ All devices are up to date with maintenance!")