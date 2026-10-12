import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Energy Consumption Analytics", page_icon="⚡", layout="wide")
st.title("⚡ Energy Consumption and Sustainability Analytics")
st.write("Explore household electricity use, compare patterns, and review energy-saving suggestions.")

uploaded_file = st.sidebar.file_uploader(
    "Upload the original household electricity dataset",
    type=["zip", "txt", "csv"]
)

if uploaded_file is None:
    st.info("Upload your original dataset in the left sidebar to open the dashboard.")
    st.markdown("### This dashboard includes")
    st.markdown("- Summary cards\n- Monthly estimated energy use\n- Hourly and weekday patterns\n- Measurement correlation heatmap\n- Data quality checks and downloadable CSV files")
    st.stop()

@st.cache_data(show_spinner="Reading and preparing the data...")
def prepare_data(file_bytes):
    if file_bytes[:2] == b"PK":
        data = pd.read_csv(io.BytesIO(file_bytes), sep=";", na_values=["?"], low_memory=False, compression="zip")
    else:
        data = pd.read_csv(io.BytesIO(file_bytes), sep=";", na_values=["?"], low_memory=False)
    required = [
        "Date", "Time", "Global_active_power", "Global_reactive_power",
        "Voltage", "Global_intensity", "Sub_metering_1", "Sub_metering_2", "Sub_metering_3"
    ]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError("Missing expected columns: " + ", ".join(missing))

    data["Date"] = pd.to_datetime(data["Date"], dayfirst=True, errors="coerce")
    numeric_columns = [
        "Global_active_power", "Global_reactive_power", "Voltage",
        "Global_intensity", "Sub_metering_1", "Sub_metering_2", "Sub_metering_3"
    ]
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data["DateTime"] = pd.to_datetime(
        data["Date"].dt.strftime("%Y-%m-%d") + " " + data["Time"].astype(str),
        errors="coerce"
    )
    data = data.dropna(subset=["DateTime"])
    data = data.drop_duplicates(subset=["DateTime"])
    data = data.sort_values("DateTime").set_index("DateTime")
    data = data[(data.index >= "2009-12-01") & (data.index < "2010-12-01")].copy()
    data[numeric_columns] = data[numeric_columns].interpolate(
        method="time", limit=5, limit_area="inside"
    )
    return data, numeric_columns

try:
    df, numeric_columns = prepare_data(uploaded_file.getvalue())
except Exception as error:
    st.error(f"Could not read this file: {error}")
    st.stop()

if df.empty:
    st.warning("No readings were found between December 2009 and November 2010. Please check the uploaded file.")
    st.stop()

st.caption(
    f"Selected period: {df.index.min():%d %b %Y} to {df.index.max():%d %b %Y}. "
    "The source dataset ends on 26 November 2010, so November is incomplete."
)

average_power = df["Global_active_power"].mean()
highest_power = df["Global_active_power"].max()
hourly_average = df.groupby(df.index.hour)["Global_active_power"].mean()
peak_hour = int(hourly_average.idxmax())
off_peak_hour = int(hourly_average.idxmin())
monthly_energy = df["Global_active_power"].resample("MS").sum(min_count=1) / 60
total_energy = monthly_energy.sum(min_count=1)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Average power", f"{average_power:.2f} kW")
c2.metric("Highest recorded power", f"{highest_power:.2f} kW")
c3.metric("Estimated energy total", f"{total_energy:,.0f} kWh")
c4.metric("Peak average hour", f"{peak_hour:02d}:00")

monthly_tab, hourly_tab, weekday_tab, correlation_tab, data_tab = st.tabs([
    "Monthly consumption", "Hourly pattern", "Weekday pattern", "Measurement relationships", "Data and downloads"
])

with monthly_tab:
    monthly_frame = monthly_energy.rename("Estimated energy (kWh)").reset_index()
    monthly_frame.columns = ["Month", "Estimated energy (kWh)"]
    monthly_frame["Month"] = monthly_frame["Month"].dt.strftime("%b %Y")
    fig = px.bar(monthly_frame, x="Month", y="Estimated energy (kWh)", title="Estimated Monthly Electricity Consumption")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Monthly energy is estimated from available one-minute power readings. Missing readings can make totals lower than actual use.")
    st.dataframe(monthly_frame, use_container_width=True, hide_index=True)

with hourly_tab:
    hourly_frame = hourly_average.rename("Average power (kW)").reset_index()
    hourly_frame.columns = ["Hour", "Average power (kW)"]
    fig = px.line(hourly_frame, x="Hour", y="Average power (kW)", markers=True, title="Average Electricity Consumption by Hour")
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)
    st.write(f"**Peak average hour:** {peak_hour:02d}:00")
    st.write(f"**Lowest average hour:** {off_peak_hour:02d}:00")

with weekday_tab:
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_data = df.groupby(df.index.day_name())["Global_active_power"].mean().reindex(order)
    weekday_frame = weekday_data.rename("Average power (kW)").reset_index()
    weekday_frame.columns = ["Weekday", "Average power (kW)"]
    fig = px.bar(weekday_frame, x="Weekday", y="Average power (kW)", title="Average Electricity Consumption by Weekday")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(weekday_frame.round(3), use_container_width=True, hide_index=True)

with correlation_tab:
    fig = px.imshow(
        df[numeric_columns].corr(), text_auto=".2f", aspect="auto",
        color_continuous_scale="RdBu_r", title="Relationship Between Electricity Measurements"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Correlation shows how measurements move together; it does not prove cause and effect.")

with data_tab:
    st.subheader("Data quality")
    st.write(f"**Rows in selected period:** {len(df):,}")
    st.write(f"**First reading:** {df.index.min()}")
    st.write(f"**Last reading:** {df.index.max()}")
    st.write("**Missing values after filling short gaps:**")
    st.dataframe(df[numeric_columns].isna().sum().rename("Missing values").to_frame())

    st.download_button(
        "Download cleaned dataset (CSV)",
        data=df.to_csv().encode("utf-8"),
        file_name="cleaned_household_power_2010.csv",
        mime="text/csv"
    )
    st.download_button(
        "Download monthly energy results (CSV)",
        data=monthly_energy.rename("Estimated_Energy_kWh").to_csv().encode("utf-8"),
        file_name="monthly_energy_consumption.csv",
        mime="text/csv"
    )
    summary = pd.DataFrame({
        "Metric": [
            "Average power consumption (kW)", "Highest recorded power consumption (kW)",
            "Peak average consumption hour", "Lowest average consumption hour",
            "Total estimated energy (kWh)"
        ],
        "Result": [
            round(average_power, 3), round(highest_power, 3),
            f"{peak_hour:02d}:00", f"{off_peak_hour:02d}:00", round(total_energy, 2)
        ]
    })
    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.download_button(
        "Download analysis summary (CSV)",
        data=summary.to_csv(index=False).encode("utf-8"),
        file_name="energy_analysis_summary.csv",
        mime="text/csv"
    )

st.subheader("Energy-saving suggestions")
st.markdown(
    "- Switch off lights and devices when they are not needed.\n"
    "- Review the hours with higher average power consumption.\n"
    "- Compare monthly estimates to spot changes in electricity use.\n"
    "- Consider energy-efficient appliances where practical."
)
st.caption("The dataset represents one household in France, so results should not be treated as representative of every household.")
