import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import time as tm
from src.database.db_manager import DBManager, DatabaseError
from src.models.reservation import Reservation
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
    format_date, 
    format_datetime, 
    format_time,
    create_user_map,
    create_user_id_to_name_map,
    create_device_map,
    create_device_id_to_name_map,
)


def show_reservations_ui() -> None:
    """
    Render the Reservation System interface with full CRUD operations.
    """
    apply_custom_css()
    db = DBManager()
    st.header("📅 Reservation System")

    # Fetch Helper Data
    devices = db.get_all_devices()
    users = db.get_all_users()
    active_devices = [d for d in devices if d.status == "active"]
    active_users = [u for u in users if u.is_active]

    if not devices or not users:
        show_warning_message("Please add both Users and Devices before making reservations.")
        return

    # Create lookup maps using utility functions
    device_map = create_device_map(active_devices)
    user_map = create_user_map(active_users)
    device_id_to_name = create_device_id_to_name_map(devices)
    user_id_to_name = create_user_id_to_name_map(users)

    if not device_map:
        show_warning_message("No active devices available for reservation.")
        return
    
    if not user_map:
        show_warning_message("No active users available to make reservations.")
        return

    # Tab layout
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Reservations", 
        "➕ Book Device", 
        "✏️ Edit Reservation",
        "📊 Calendar View"
    ])
    
    with tab1:
        _show_reservations_list(db, device_id_to_name, user_id_to_name, devices)
    
    with tab2:
        _show_booking_form(db, device_map, user_map, device_id_to_name)
    
    with tab3:
        _show_edit_reservation(db, device_id_to_name, user_id_to_name)
    
    with tab4:
        _show_calendar_view(db, device_id_to_name, user_id_to_name, devices)


def _show_reservations_list(
    db: DBManager, 
    device_id_to_name: dict, 
    user_id_to_name: dict,
    devices: list
) -> None:
    """Display the list of reservations with filters."""
    reservations = db.get_all_reservations()
    
    if not reservations:
        show_empty_state(
            "No Reservations",
            "Book a device using the 'Book Device' tab.",
            "📅"
        )
        return
    
    # Filter Section
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        time_filter = st.selectbox(
            "Time Period",
            ["All", "Today", "This Week", "Upcoming", "Active Now", "Past"],
            key="res_time_filter"
        )
    
    with col2:
        device_filter = st.selectbox(
            "Device",
            ["All"] + [f"{d.name}" for d in devices],
            key="res_device_filter"
        )
    
    with col3:
        status_filter = st.selectbox(
            "Status",
            ["All"] + Config.RESERVATION_STATUSES,
            key="res_status_filter"
        )
    
    with col4:
        sort_by = st.selectbox(
            "Sort by",
            ["Date (Newest)", "Date (Oldest)", "Duration", "Device"],
            key="res_sort"
        )
    
    # Apply filters
    now = datetime.now()
    filtered_res = reservations
    
    if time_filter == "Today":
        filtered_res = [r for r in filtered_res if r.start_time.date() == now.date()]
    elif time_filter == "This Week":
        week_end = now + timedelta(days=7)
        filtered_res = [r for r in filtered_res if now.date() <= r.start_time.date() <= week_end.date()]
    elif time_filter == "Upcoming":
        filtered_res = [r for r in filtered_res if r.is_upcoming]
    elif time_filter == "Active Now":
        filtered_res = [r for r in filtered_res if r.is_active]
    elif time_filter == "Past":
        filtered_res = [r for r in filtered_res if r.is_past]
    
    if device_filter != "All":
        device_id = next((k for k, v in device_id_to_name.items() if v == device_filter), None)
        if device_id:
            filtered_res = [r for r in filtered_res if r.device_id == device_id]
    
    if status_filter != "All":
        filtered_res = [r for r in filtered_res if r.status == status_filter]
    
    # Sort
    if sort_by == "Date (Newest)":
        filtered_res = sorted(filtered_res, key=lambda r: r.start_time, reverse=True)
    elif sort_by == "Date (Oldest)":
        filtered_res = sorted(filtered_res, key=lambda r: r.start_time)
    elif sort_by == "Duration":
        filtered_res = sorted(filtered_res, key=lambda r: r.duration_hours, reverse=True)
    elif sort_by == "Device":
        filtered_res = sorted(filtered_res, key=lambda r: device_id_to_name.get(r.device_id, ""))
    
    # Display count
    st.caption(f"Showing {len(filtered_res)} of {len(reservations)} reservations")
    
    if filtered_res:
        res_data = [{
            "Status": show_status_badge(r.status),
            "Device": device_id_to_name.get(r.device_id, r.device_id),
            "User": user_id_to_name.get(r.user_id, r.user_id),
            "Date": format_date(r.start_time),
            "Time": f"{format_time(r.start_time)} - {format_time(r.end_time)}",
            "Duration": f"{r.duration_hours:.1f}h",
            "Purpose": r.purpose or "N/A"
        } for r in filtered_res]
        
        st.dataframe(
            pd.DataFrame(res_data),
            width='stretch',
            hide_index=True
        )
        
        # Export section
        export_data = [r.to_dict() for r in filtered_res]
        create_export_buttons(export_data, "reservations", "res_export")
    else:
        st.info("No reservations match your search criteria.")


def _show_booking_form(
    db: DBManager, 
    device_map: dict, 
    user_map: dict,
    device_id_to_name: dict
) -> None:
    """Display the device booking form."""
    
    # Initialize session state for times
    if "res_start_time" not in st.session_state:
        st.session_state["res_start_time"] = time(9, 0)
    if "res_end_time" not in st.session_state:
        st.session_state["res_end_time"] = time(10, 0)
    
    with st.form("add_reservation_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            selected_device_key = st.selectbox(
                "Select Device *",
                options=list(device_map.keys())
            )
            selected_user_key = st.selectbox(
                "Reserved By *",
                options=list(user_map.keys())
            )
            purpose = st.text_input(
                "Purpose",
                placeholder="e.g. Project work, Testing"
            )
        
        with col2:
            res_date = st.date_input(
                "Date *",
                value=datetime.today(),
                min_value=datetime.today()
            )
            start_time = st.time_input(
                "Start Time *",
                value=st.session_state["res_start_time"]
            )
            end_time = st.time_input(
                "End Time *",
                value=st.session_state["res_end_time"]
            )
        
        notes = st.text_area(
            "Notes",
            placeholder="Additional notes or requirements...",
            height=80
        )
        
        # Quick booking options
        st.markdown("**Quick Duration:**")
        col1, col2, col3, col4 = st.columns(4)
        
        submitted = st.form_submit_button("✅ Confirm Reservation", type="primary")

        if submitted:
            st.session_state["res_start_time"] = start_time
            st.session_state["res_end_time"] = end_time

            start_dt = datetime.combine(res_date, start_time)
            end_dt = datetime.combine(res_date, end_time)

            if start_dt >= end_dt:
                show_error_message("End time must be after start time.")
            elif start_dt < datetime.now():
                show_error_message("Cannot book in the past.")
            else:
                device_id = device_map[selected_device_key]
                user_id = user_map[selected_user_key]
                
                if db.is_device_available(device_id, start_dt, end_dt):
                    try:
                        reservation = Reservation.create_new(
                            device_id=device_id,
                            user_id=user_id,
                            start=start_dt,
                            end=end_dt,
                            purpose=purpose.strip(),
                            notes=notes.strip()
                        )
                        db.add_reservation(reservation)
                        show_success_message(
                            f"Reservation confirmed for {device_id_to_name.get(device_id)} "
                            f"on {format_date(res_date)} from {start_time} to {end_time}"
                        )
                        tm.sleep(1)
                        st.rerun()
                    except DatabaseError as e:
                        show_error_message(str(e))
                    except Exception as e:
                        show_error_message(f"Error creating reservation: {e}")
                else:
                    show_error_message("Conflict: The device is already booked for this time slot.")
    
    # Show device availability
    st.subheader("📊 Check Availability")
    
    col1, col2 = st.columns(2)
    with col1:
        check_device = st.selectbox(
            "Device",
            options=list(device_map.keys()),
            key="check_device"
        )
    with col2:
        check_date = st.date_input(
            "Date",
            value=datetime.today(),
            key="check_date"
        )
    
    if check_device and check_date:
        device_id = device_map[check_device]
        reservations = db.get_reservations_by_device(device_id)
        day_reservations = [
            r for r in reservations 
            if r.start_time.date() == check_date and r.status not in ["cancelled"]
        ]
        
        if day_reservations:
            st.write(f"**Bookings on {format_date(check_date)}:**")
            for r in sorted(day_reservations, key=lambda x: x.start_time):
                st.write(
                    f"- {format_time(r.start_time)} - {format_time(r.end_time)}: "
                    f"{r.purpose or 'No purpose specified'}"
                )
        else:
            st.success(f"✅ Device is available all day on {format_date(check_date)}")


def _show_edit_reservation(
    db: DBManager,
    device_id_to_name: dict,
    user_id_to_name: dict
) -> None:
    """Display form for editing reservations."""
    
    reservations = db.get_all_reservations()
    editable = [r for r in reservations if r.status in ["pending", "confirmed"] and r.is_upcoming]
    
    if not editable:
        st.info("No upcoming reservations available to edit.")
        return
    
    selected_res = st.selectbox(
        "Select Reservation to Edit",
        options=editable,
        format_func=lambda r: (
            f"{device_id_to_name.get(r.device_id, r.device_id)} - "
            f"{format_datetime(r.start_time)} - "
            f"{user_id_to_name.get(r.user_id, r.user_id)}"
        ),
        key="edit_res_select"
    )
    
    if selected_res:
        with st.form("edit_reservation_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input(
                    "Device",
                    value=device_id_to_name.get(selected_res.device_id, selected_res.device_id),
                    disabled=True
                )
                st.text_input(
                    "User",
                    value=user_id_to_name.get(selected_res.user_id, selected_res.user_id),
                    disabled=True
                )
                purpose = st.text_input(
                    "Purpose",
                    value=selected_res.purpose
                )
            
            with col2:
                new_date = st.date_input(
                    "Date",
                    value=selected_res.start_time.date(),
                    min_value=datetime.today().date()
                )
                new_start = st.time_input(
                    "Start Time",
                    value=selected_res.start_time.time()
                )
                new_end = st.time_input(
                    "End Time",
                    value=selected_res.end_time.time()
                )
            
            notes = st.text_area(
                "Notes",
                value=selected_res.notes,
                height=80
            )
            
            status = st.selectbox(
                "Status",
                options=["pending", "confirmed"],
                index=["pending", "confirmed"].index(selected_res.status) if selected_res.status in ["pending", "confirmed"] else 0
            )
            
            submitted = st.form_submit_button("💾 Save Changes", type="primary")
            
            if submitted:
                new_start_dt = datetime.combine(new_date, new_start)
                new_end_dt = datetime.combine(new_date, new_end)
                
                if new_start_dt >= new_end_dt:
                    show_error_message("End time must be after start time.")
                else:
                    # Check availability (excluding current reservation)
                    if db.is_device_available(
                        selected_res.device_id, 
                        new_start_dt, 
                        new_end_dt,
                        exclude_id=selected_res.id
                    ):
                        try:
                            db.update_reservation(
                                selected_res.id,
                                start_time=new_start_dt,
                                end_time=new_end_dt,
                                purpose=purpose.strip(),
                                notes=notes.strip(),
                                status=status
                            )
                            show_success_message("Reservation updated successfully!")
                            tm.sleep(1)
                            st.rerun()
                        except Exception as e:
                            show_error_message(f"Error updating reservation: {e}")
                    else:
                        show_error_message("Time slot conflicts with another reservation.")
        
        # Cancel Section
        st.subheader("❌ Cancel Reservation")
        
        if selected_res.status not in ["cancelled", "completed"]:
            st.warning(
                f"⚠️ This will cancel the reservation for "
                f"**{device_id_to_name.get(selected_res.device_id, selected_res.device_id)}** on "
                f"{format_date(selected_res.start_time)} ({format_time(selected_res.start_time)} - {format_time(selected_res.end_time)})"
            )
            
            if st.button("❌ Cancel Reservation", key="cancel_res_btn"):
                db.cancel_reservation(selected_res.id)
                show_success_message("Reservation cancelled!")
                tm.sleep(1)
                st.rerun()
        else:
            st.info(f"This reservation is already {selected_res.status}.")


def _show_calendar_view(
    db: DBManager,
    device_id_to_name: dict,
    user_id_to_name: dict,
    devices: list
) -> None:
    """Display a calendar-like view of reservations."""
    st.subheader("📊 Weekly Calendar View")
    
    # Date selection
    col1, col2 = st.columns(2)
    with col1:
        selected_date = st.date_input(
            "Week starting",
            value=datetime.today(),
            key="calendar_date"
        )
    with col2:
        selected_device = st.selectbox(
            "Device",
            options=["All Devices"] + [d.name for d in devices if d.status == "active"],
            key="calendar_device"
        )
    
    # Calculate week dates
    start_of_week = selected_date - timedelta(days=selected_date.weekday())
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    
    # Get reservations for the week
    reservations = db.get_all_reservations()
    week_reservations = [
        r for r in reservations 
        if start_of_week <= r.start_time.date() <= week_dates[-1]
        and r.status not in ["cancelled"]
    ]
    
    if selected_device != "All Devices":
        device_id = next((d.id for d in devices if d.name == selected_device), None)
        if device_id:
            week_reservations = [r for r in week_reservations if r.device_id == device_id]
    
    # Display week header
    st.markdown("---")
    cols = st.columns(7)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    for i, (col, day, date) in enumerate(zip(cols, days, week_dates)):
        with col:
            is_today = date == datetime.today().date()
            if is_today:
                st.markdown(f"**{day}**")
                st.markdown(f"**{date.strftime('%d/%m')}** 📍")
            else:
                st.markdown(f"**{day}**")
                st.markdown(f"{date.strftime('%d/%m')}")
            
            # Get reservations for this day
            day_res = [r for r in week_reservations if r.start_time.date() == date]
            
            if day_res:
                for r in sorted(day_res, key=lambda x: x.start_time):
                    device_name = device_id_to_name.get(r.device_id, "")[:10]
                    time_str = format_time(r.start_time)
                    st.caption(f"🔹 {time_str}")
                    st.caption(f"{device_name}")
            else:
                st.caption("No bookings")
    
    # Summary below calendar
    st.markdown("---")
    st.subheader("📋 Week Summary")
    
    if week_reservations:
        summary_data = [{
            "Day": r.start_time.strftime("%A"),
            "Date": format_date(r.start_time),
            "Time": f"{format_time(r.start_time)} - {format_time(r.end_time)}",
            "Device": device_id_to_name.get(r.device_id, r.device_id),
            "User": user_id_to_name.get(r.user_id, r.user_id),
            "Purpose": r.purpose or "N/A"
        } for r in sorted(week_reservations, key=lambda x: x.start_time)]
        
        st.dataframe(pd.DataFrame(summary_data), width='stretch', hide_index=True)
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Bookings", len(week_reservations))
        with col2:
            total_hours = sum(r.duration_hours for r in week_reservations)
            st.metric("Total Hours", f"{total_hours:.1f}h")
        with col3:
            unique_devices = len(set(r.device_id for r in week_reservations))
            st.metric("Devices Used", unique_devices)
    else:
        st.info("No reservations for this week.")