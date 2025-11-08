"""
Historical Logs Module
Provides calendar-based and date-range views of patient care logs.

This module allows doctors and carers to review past care records,
identify patterns, and export data for reporting purposes.
"""

import streamlit as st
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import calendar
"""
Provides both calendar-based and date-range views of patient care logs.
This module allows doctors and carers to review past care records,
identify patterns, and export data for reporting purposes.
"""

class LogViewSelector:
    """
    """
    
    @staticmethod
    def render() -> str:
        """
        Render view mode selector.
        
        Returns:
            Selected view mode ('Calendar View' or 'Date Range')
        """
        return st.radio(
            "View Mode",
            ["Calendar View", "Date Range"],
            horizontal=True
        )


class CalendarViewController:
    """
    """
    
    @staticmethod
    def render(patient_id: str) -> None:
        """
        """
        selected_year, selected_month = CalendarViewController._render_date_selector()
        
        st.divider()
        
        if patient_id not in st.session_state.daily_logs:
            st.info("No logs recorded yet for this patient")
            return
        
        logs_by_date = CalendarViewController._get_logs_for_month(
            patient_id,
            selected_year,
            selected_month
        )
        
        CalendarViewController._render_calendar_grid(
            selected_year,
            selected_month,
            logs_by_date
        )
        
        CalendarViewController._display_selected_date_logs(logs_by_date)
    
    @staticmethod
    def _render_date_selector() -> Tuple[int, int]:
        """
        """
        col1, col2 = st.columns(2)
        
        with col1:
            selected_year = st.selectbox(
                "Year",
                range(2020, 2030),
                index=date.today().year - 2020
            )
        
        with col2:
            selected_month = st.selectbox(
                "Month",
                range(1, 13),
                format_func=lambda x: calendar.month_name[x],
                index=date.today().month - 1
            )
        
        return selected_year, selected_month
    
    @staticmethod
    def _get_logs_for_month(
        patient_id: str,
        year: int,
        month: int
    ) -> Dict[str, List[Dict]]:
        """
        Get all logs for specified month.
        """
        all_logs = st.session_state.daily_logs[patient_id]
        
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)
        
        logs_by_date = {}
        for log in all_logs:
            log_date = log['date']
            if month_start.isoformat() <= log_date <= month_end.isoformat():
                if log_date not in logs_by_date:
                    logs_by_date[log_date] = []
                logs_by_date[log_date].append(log)
        
        return logs_by_date
    
    @staticmethod
    def _render_calendar_grid(
        year: int,
        month: int,
        logs_by_date: Dict[str, List[Dict]]
    ) -> None:
        """
        """
        st.subheader(f"{calendar.month_name[month]} {year}")
        
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        cols = st.columns(7)
        for idx, day in enumerate(days):
            cols[idx].markdown(f"**{day}**")
        
        cal = calendar.monthcalendar(year, month)
        
        for week in cal:
            cols = st.columns(7)
            for idx, day in enumerate(week):
                if day == 0:
                    cols[idx].write("")
                else:
                    CalendarViewController._render_calendar_day(
                        cols[idx],
                        year,
                        month,
                        day,
                        logs_by_date
                    )
    
    @staticmethod
    def _render_calendar_day(
        col,
        year: int,
        month: int,
        day: int,
        logs_by_date: Dict[str, List[Dict]]
    ) -> None:
        """
        """
        day_date = date(year, month, day)
        day_str = day_date.isoformat()
        
        if day_str in logs_by_date:
            num_logs = len(logs_by_date[day_str])
            if col.button(
                f"**{day}** ({num_logs})",
                key=f"day_{day}",
                use_container_width=True
            ):
                st.session_state.selected_calendar_date = day_str
        else:
            col.button(
                f"{day}",
                key=f"day_{day}",
                disabled=True,
                use_container_width=True
            )
    
    @staticmethod
    def _display_selected_date_logs(logs_by_date: Dict[str, List[Dict]]) -> None:
        """
        """
        st.divider()
        
        if 'selected_calendar_date' not in st.session_state:
            return
        
        selected_date = st.session_state.selected_calendar_date
        
        if selected_date not in logs_by_date:
            st.info("No logs recorded for this date")
            return
        
        selected_date_logs = logs_by_date[selected_date]
        selected_date_obj = datetime.fromisoformat(selected_date)
        
        st.subheader(
            f"Logs for {selected_date_obj.strftime('%A, %d %B %Y')}"
        )
        
        for log in sorted(selected_date_logs, key=lambda x: x.get('time', '00:00')):
            LogDetailRenderer.render_log_expander(log)


class DateRangeController:
    """
    Handles date range selection and filtering.
    """
    
    @staticmethod
    def render() -> Tuple[date, date]:
        """
        Render date range selection controls.
        
        Returns:
            Tuple of (start_date, end_date)
        """
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "From Date",
                value=date.today() - timedelta(days=30),
                max_value=date.today()
            )
        
        with col2:
            end_date = st.date_input(
                "To Date",
                value=date.today(),
                max_value=date.today()
            )
        
        DateRangeController._render_quick_buttons()
        
        return start_date, end_date
    
    @staticmethod
    def _render_quick_buttons() -> None:
        """Render quick date range selection buttons."""
        col1, col2, col3, col4 = st.columns(4)
        
        quick_ranges = {
            "Last 7 Days": 7,
            "Last 30 Days": 30,
            "Last 3 Months": 90,
            "This Year": None
        }
        
        cols = [col1, col2, col3, col4]
        
        for idx, (label, days) in enumerate(quick_ranges.items()):
            with cols[idx]:
                if st.button(label):
                    DateRangeController._apply_quick_range(days)
    
    @staticmethod
    def _apply_quick_range(days: Optional[int]) -> None:
        """
        Apply quick date range selection.
        
        Args:
            days: Number of days to go back, or None for this year
        """
        if days:
            st.session_state.range_start = date.today() - timedelta(days=days)
            st.session_state.range_end = date.today()
        else:
            st.session_state.range_start = date(date.today().year, 1, 1)
            st.session_state.range_end = date.today()
        
        st.rerun()


class LogDetailRenderer:
    """
    Renders detailed log information in expandable sections.
    """
    
    @staticmethod
    def render_log_expander(log: Dict[str, Any]) -> None:
        """
        Render log details in expandable section.
        
        Args:
            log: Log entry dictionary
        """
        with st.expander(
            f"{log.get('time', 'N/A')} - by {log.get('logged_by', 'Unknown')}"
        ):
            tab1, tab2, tab3, tab4 = st.tabs(
                ["Vitals", "Status", "Medications", "Notes"]
            )
            
            with tab1:
                LogDetailRenderer._render_vitals_tab(log)
            
            with tab2:
                LogDetailRenderer._render_status_tab(log)
            
            with tab3:
                LogDetailRenderer._render_medications_tab(log)
            
            with tab4:
                LogDetailRenderer._render_notes_tab(log)
    
    @staticmethod
    def _render_vitals_tab(log: Dict[str, Any]) -> None:
        """Render vitals information tab."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Temperature", f"{log['vitals']['temperature']}°C")
            st.metric("Heart Rate", f"{log['vitals']['heart_rate']} bpm")
        
        with col2:
            st.metric("Blood Pressure", log['vitals']['blood_pressure'])
            st.metric("Oxygen", f"{log['vitals']['oxygen_saturation']}%")
        
        with col3:
            st.metric("Weight", f"{log['vitals']['weight']} kg")
    
    @staticmethod
    def _render_status_tab(log: Dict[str, Any]) -> None:
        """Render status information tab."""
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Mood:** {log['activities']['mood']}")
            st.write(f"**Sleep:** {log['activities']['sleep_quality']}")
            st.write(f"**Appetite:** {log['activities']['appetite']}")
        
        with col2:
            st.write(f"**Activity:** {log['activities']['activity_level']}")
            st.write(f"**Social:** {log['activities']['social_engagement']}")
            st.write(f"**Communication:** {log['activities']['communication']}")
        
        if log.get('meals'):
            st.write("**Nutrition:**")
            st.write(
                f"Calories: {log['meals'].get('total_calories', 0)} kcal | "
                f"Fluids: {log['meals'].get('total_fluids', 0)} ml"
            )
            st.write(
                f"Breakfast: {log['meals']['breakfast'].get('amount', 'N/A')} | "
                f"Lunch: {log['meals']['lunch'].get('amount', 'N/A')} | "
                f"Dinner: {log['meals']['dinner'].get('amount', 'N/A')}"
            )
    
    @staticmethod
    def _render_medications_tab(log: Dict[str, Any]) -> None:
        """Render medications information tab."""
        if log.get('medications_given'):
            st.write("**Medications Administered:**")
            for med in log['medications_given']:
                st.write(f"- **{med['medication']}** ({med['dosage']})")
                st.write(
                    f"  Scheduled: {med['scheduled_time']} | "
                    f"Given: {med['time_given']}"
                )
                st.write(f"  By: {med.get('given_by', 'Unknown')}")
                st.divider()
        else:
            st.info("No medications recorded for this day")
    
    @staticmethod
    def _render_notes_tab(log: Dict[str, Any]) -> None:
        """Render notes information tab."""
        if log.get('general_notes'):
            st.info(f"**Notes:** {log['general_notes']}")
        
        if log.get('incidents'):
            st.error(f"**Incidents:** {log['incidents']}")


class LogExporter:
    """
    Handles exporting logs to CSV format.
    """
    
    @staticmethod
    def render_export_button(
        patient_name: str,
        logs: List[Dict],
        start_date: date,
        end_date: date
    ) -> None:
        """
        export button and handle CSV generation.
        """
        if st.button("Export to CSV"):
            csv_data = LogExporter._generate_csv(logs)
            
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"{patient_name}_logs_{start_date}_to_{end_date}.csv",
                mime="text/csv"
            )
    
    @staticmethod
    def _generate_csv(logs: List[Dict]) -> str:
        """
        """
        export_data = []
        
        for log in logs:
            meds_given = ""
            if log.get('medications_given'):
                meds_list = [
                    f"{m['medication']} ({m['dosage']}) at {m['time_given']}"
                    for m in log['medications_given']
                ]
                meds_given = "; ".join(meds_list)
            
            export_data.append({
                'Date': log['date'],
                'Time': log.get('time', 'N/A'),
                'Temperature': log['vitals']['temperature'],
                'Blood Pressure': log['vitals']['blood_pressure'],
                'Heart Rate': log['vitals']['heart_rate'],
                'Oxygen': log['vitals']['oxygen_saturation'],
                'Mood': log['activities']['mood'],
                'Sleep': log['activities']['sleep_quality'],
                'Appetite': log['activities']['appetite'],
                'Total Calories': log['meals'].get('total_calories', 0) if log.get('meals') else 0,
                'Total Fluids': log['meals'].get('total_fluids', 0) if log.get('meals') else 0,
                'Medications Given': meds_given,
                'Notes': log.get('general_notes', ''),
                'Incidents': log.get('incidents', ''),
                'Logged By': log.get('logged_by', 'Unknown')
            })
        
        df = pd.DataFrame(export_data)
        return df.to_csv(index=False)


def render_page() -> None:
    """Main function to render the Historical Logs page."""
    st.title("Historical Logs")
    
    from pages.daily_logs import PatientSelector
    patient_info = PatientSelector.render_selector()
    
    if not patient_info:
        st.stop()
    
    patient_id, patient_name = patient_info
    
    st.divider()
    
    view_mode = LogViewSelector.render()
    
    if view_mode == "Calendar View":
        CalendarViewController.render(patient_id)
    else:
        start_date, end_date = DateRangeController.render()
        
        st.divider()
        
        if patient_id not in st.session_state.daily_logs:
            st.info("No logs recorded yet for this patient")
            return
        
        all_logs = st.session_state.daily_logs[patient_id]
        
        filtered_logs = [
            log for log in all_logs
            if start_date.isoformat() <= log['date'] <= end_date.isoformat()
        ]
        
        if filtered_logs:
            st.success(
                f"Found {len(filtered_logs)} logs between "
                f"{start_date.strftime('%d %b %Y')} and "
                f"{end_date.strftime('%d %b %Y')}"
            )
            
            sorted_logs = sorted(filtered_logs, key=lambda x: x['date'], reverse=True)
            
            for log in sorted_logs:
                log_date = datetime.fromisoformat(log['date']).strftime(
                    '%A, %d %B %Y'
                )
                
                with st.expander(
                    f"{log_date} at {log.get('time', 'N/A')} - "
                    f"by {log.get('logged_by', 'Unknown')}"
                ):
                    LogDetailRenderer.render_log_expander(log)
            
            st.divider()
            LogExporter.render_export_button(
                patient_name,
                sorted_logs,
                start_date,
                end_date
            )
        else:
            st.info(
                f"No logs found between {start_date.strftime('%d %b %Y')} and "
                f"{end_date.strftime('%d %b %Y')}"
            )


if __name__ == "__main__":
    render_page()