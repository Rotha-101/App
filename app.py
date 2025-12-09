import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ------------- PAGE CONFIG -------------
st.set_page_config(
    page_title="Power Logger UI",
    page_icon="⚡",
    layout="wide",
)

# ------------- INITIAL STATE -------------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Date Time", "Power"])

# ------------- HEADER -------------
st.title("⚡ Power Logger – Dynamic Interface")
st.markdown(
    """
A simple & dynamic web interface to:
- Input integer power values (50, 40, …)
- Automatically attach current **Date Time** (from your computer)
- Edit data in a table (add / delete / change)
- Visualize **Date Time vs Power** in real-time
- Download the edited data as CSV
"""
)

# ------------- TOP METRICS -------------
df = st.session_state.df

col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    st.metric("Total rows", len(df))

with col_b:
    latest_power = int(df["Power"].iloc[-1]) if not df.empty else "—"
    st.metric("Latest Power", latest_power)

with col_c:
    avg_power = round(df["Power"].mean(), 2) if not df.empty else "—"
    st.metric("Average Power", avg_power)

with col_d:
    if not df.empty:
        try:
            first_time = pd.to_datetime(df["Date Time"]).min()
            st.metric("Start time", str(first_time))
        except Exception:
            st.metric("Start time", "Invalid Date")

st.markdown("---")

# ------------- TABS -------------
tab_input, tab_plot, tab_export = st.tabs(
    ["📥 Input & Table", "📈 Visualization", "💾 Export"]
)

# ------------- TAB 1: INPUT & TABLE -------------
with tab_input:
    st.subheader("📥 Input new power data")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        power_value = st.number_input(
            "Power (integer, e.g. 50, 40, ...)",
            min_value=-100000,
            max_value=100000,
            step=1,
            value=50,
        )

    with col2:
        st.write("")  # space
        add_clicked = st.button("➕ Add to table", use_container_width=True)

    with col3:
        st.write("")
        clear_clicked = st.button("🗑️ Clear all data", use_container_width=True)

    if add_clicked:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = pd.DataFrame(
            {
                "Date Time": [now],
                "Power": [int(power_value)],
            }
        )
        st.session_state.df = pd.concat(
            [st.session_state.df, new_row],
            ignore_index=True,
        )
        st.success(f"Added row → {now} | Power = {int(power_value)}")

    if clear_clicked:
        st.session_state.df = pd.DataFrame(columns=["Date Time", "Power"])
        st.warning("All data cleared.")

    st.markdown("### 🧾 Data table (editable)")
    st.caption("You can edit cells, add new rows, or delete rows in this table.")

    edited_df = st.data_editor(
        st.session_state.df,
        num_rows="dynamic",
        use_container_width=True,
        key="data_editor",
    )
    st.session_state.df = edited_df

# ------------- TAB 2: VISUALIZATION -------------
with tab_plot:
    st.subheader("📈 Power vs Date Time")

    df_plot = st.session_state.df.copy()

    if df_plot.empty:
        st.info("No data to plot yet. Add some power values in the **Input & Table** tab.")
    else:
        # Try to convert Date Time to datetime
        try:
            df_plot["Date Time"] = pd.to_datetime(df_plot["Date Time"])
        except Exception:
            st.warning("Could not parse 'Date Time' as datetime. Plot will treat it as text.")

        left, right = st.columns([2, 1])

        with right:
            chart_type = st.selectbox(
                "Chart type",
                ["Line", "Scatter", "Bar"],
            )
            show_markers = st.checkbox("Show markers", value=True)
            sort_by_time = st.checkbox("Sort by Date Time", value=True)

        if sort_by_time:
            try:
                df_plot = df_plot.sort_values("Date Time")
            except Exception:
                pass

        with left:
            st.caption("Chart updates automatically as you edit the table.")

        # Build chart dynamically
        try:
            if chart_type == "Line":
                fig = px.line(
                    df_plot,
                    x="Date Time",
                    y="Power",
                    markers=show_markers,
                    title="Power vs Date Time",
                )
            elif chart_type == "Scatter":
                fig = px.scatter(
                    df_plot,
                    x="Date Time",
                    y="Power",
                    title="Power vs Date Time",
                )
            else:  # Bar
                fig = px.bar(
                    df_plot,
                    x="Date Time",
                    y="Power",
                    title="Power vs Date Time",
                )

            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating chart: {e}")

# ------------- TAB 3: EXPORT -------------
with tab_export:
    st.subheader("💾 Save / download CSV")

    if st.session_state.df.empty:
        st.info("Table is empty. Add some data before saving.")
    else:
        file_name = st.text_input(
            "CSV file name",
            value="power_data.csv",
        )

        csv_bytes = st.session_state.df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="💾 Save CSV",
            data=csv_bytes,
            file_name=file_name,
            mime="text/csv",
            use_container_width=True,
        )

        st.caption("The downloaded CSV includes all edits you made in the table.")
