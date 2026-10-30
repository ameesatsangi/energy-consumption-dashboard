
import streamlit as st
import pandas as pd
import plotly.express as px
import gdown
import os

st.set_page_config(
    page_title="Energy Consumption Dashboard",
    page_icon="⚡",
    layout="wide"
)

st.title("Energy Consumption and Sustainability Analytics")
st.write("An interactive dashboard to understand household electricity consumption patterns.")

FILE_ID = "1YGdqhGe5BrxIh8fe4Caj3n1svsSBL61C"
DATASET_PATH = "household_power_consumption.txt.zip"

@st.cache_data
def load_dataset():
    if not os.path.exists(DATASET_PATH):
        downloaded_file = gdown.download(
            id=FILE_ID,
            output=DATASET_PATH,
            quiet=False
        )

        if downloaded_file is None:
            raise Exception("Unable to download the dataset from Google Drive.")

    data = pd.read_csv(
        DATASET_PATH,
        sep=";",
        na_values=["?"],
        low_memory=False,
        compression="zip"
    )

    return data

try:
    with st.spinner("Loading household electricity dataset..."):
        df = load_dataset()

    st.success("Dataset loaded successfully from Google Drive!")

    numeric_columns = [
        "Global_active_power",
        "Global_reactive_power",
        "Voltage",
        "Global_intensity",
        "Sub_metering_1",
        "Sub_metering_2",
        "Sub_metering_3"
    ]

    df["Date"] = pd.to_datetime(
        df["Date"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["DateTime"] = pd.to_datetime(
        df["Date"].dt.strftime("%Y-%m-%d") + " " + df["Time"],
        errors="coerce"
    )

    df = df[
        (df["DateTime"] >= "2009-12-01") &
        (df["DateTime"] < "2010-11-27")
    ].copy()

    df = df.dropna(subset=["DateTime"])
    df = df.drop_duplicates(subset=["DateTime"])
    df = df.sort_values("DateTime")
    df = df.set_index("DateTime")

    if df.empty:
        st.error("No records found for the selected project period.")
        st.stop()

    missing_before = df[numeric_columns].isnull().sum()

    df[numeric_columns] = df[numeric_columns].interpolate(
        method="time",
        limit=5,
        limit_area="inside"
    )

    average_power = df["Global_active_power"].mean()
    highest_power = df["Global_active_power"].max()

    monthly_energy = (
        df["Global_active_power"].resample("MS").sum(min_count=1) / 60
    )

    hourly_pattern = df.groupby(
        df.index.hour
    )["Global_active_power"].mean()

    weekday_order = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    weekday_usage = df.groupby(
        df.index.day_name()
    )["Global_active_power"].mean().reindex(weekday_order)

    st.sidebar.header("Dataset Information")
    st.sidebar.write("Total Records:", f"{len(df):,}")
    st.sidebar.write(
        "Period:",
        f"{df.index.min().date()} to {df.index.max().date()}"
    )

    st.header("Electricity Consumption Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Average Power", f"{average_power:.2f} kW")
    col2.metric("Highest Power", f"{highest_power:.2f} kW")
    col3.metric("Total Records", f"{len(df):,}")
    col4.metric("Estimated Energy", f"{monthly_energy.sum():,.2f} kWh")

    st.divider()

    st.header("Monthly Energy Consumption")

    monthly_chart = px.bar(
        x=monthly_energy.index.strftime("%b %Y"),
        y=monthly_energy.values,
        labels={
            "x": "Month",
            "y": "Estimated Energy (kWh)"
        },
        title="Estimated Monthly Electricity Consumption"
    )

    st.plotly_chart(monthly_chart, use_container_width=True)

    st.header("Hourly Electricity Usage")

    hourly_chart = px.line(
        x=hourly_pattern.index,
        y=hourly_pattern.values,
        labels={
            "x": "Hour of Day",
            "y": "Average Power (kW)"
        },
        title="Average Electricity Consumption by Hour"
    )

    st.plotly_chart(hourly_chart, use_container_width=True)

    st.header("Weekday Consumption")

    weekday_chart = px.bar(
        x=weekday_usage.index,
        y=weekday_usage.values,
        labels={
            "x": "Weekday",
            "y": "Average Power (kW)"
        },
        title="Average Electricity Consumption by Weekday"
    )

    st.plotly_chart(weekday_chart, use_container_width=True)

    st.header("Sub-metering Analysis")

    submeter_columns = [
        "Sub_metering_1",
        "Sub_metering_2",
        "Sub_metering_3"
    ]

    submeter_data = (
        df[submeter_columns].resample("MS").sum(min_count=1) / 1000
    )

    submeter_data.columns = [
        "Sub-metering 1",
        "Sub-metering 2",
        "Sub-metering 3"
    ]

    submeter_plot_data = submeter_data.reset_index()

    submeter_chart = px.bar(
        submeter_plot_data,
        x="DateTime",
        y=[
            "Sub-metering 1",
            "Sub-metering 2",
            "Sub-metering 3"
        ],
        barmode="group",
        labels={
            "value": "Recorded Energy (kWh)",
            "variable": "Sub-metering Group",
            "DateTime": "Month"
        },
        title="Monthly Sub-metering Comparison"
    )

    st.plotly_chart(submeter_chart, use_container_width=True)

    st.header("Correlation Heatmap")

    correlation_data = df[numeric_columns].corr()

    heatmap = px.imshow(
        correlation_data,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        title="Correlation Between Electricity Measurements"
    )

    st.plotly_chart(heatmap, use_container_width=True)

    st.header("Data Quality Information")

    quality_col1, quality_col2 = st.columns(2)

    with quality_col1:
        st.write("Missing Values Before Interpolation")
        st.dataframe(missing_before.to_frame("Missing Values"))

    with quality_col2:
        st.write("Remaining Missing Values")
        st.dataframe(
            df[numeric_columns].isnull().sum().to_frame("Missing Values")
        )

    st.header("Energy-Saving Recommendations")

    recommendations = [
        "Switch off lights and electrical devices when not needed.",
        "Avoid using high-power appliances unnecessarily.",
        "Check which hours show higher average electricity consumption.",
        "Use energy-efficient appliances.",
        "Monitor electricity consumption regularly."
    ]

    for recommendation in recommendations:
        st.write("• " + recommendation)

    st.header("Download Analysis Results")

    cleaned_csv = df.to_csv().encode("utf-8")

    st.download_button(
        "Download Cleaned Dataset",
        data=cleaned_csv,
        file_name="cleaned_household_power_2010.csv",
        mime="text/csv"
    )

    monthly_csv = monthly_energy.to_csv(
        header=["Estimated_Energy_kWh"]
    ).encode("utf-8")

    st.download_button(
        "Download Monthly Energy Report",
        data=monthly_csv,
        file_name="monthly_energy_consumption.csv",
        mime="text/csv"
    )

    st.success("Explore the charts and download the results!")

except Exception as e:
    st.error(f"Unable to load or process the dataset: {e}")
