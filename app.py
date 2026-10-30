
import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(
    page_title="Energy Consumption Dashboard",
    page_icon="⚡",
    layout="wide"
)

st.title("Energy Consumption and Sustainability Analytics")
st.write("An interactive dashboard to understand household electricity consumption patterns.")

uploaded_file = st.sidebar.file_uploader(
    "Upload Household Electricity Dataset",
    type=["zip", "txt", "csv"]
)

if uploaded_file is not None:

    try:
        file_bytes = uploaded_file.getvalue()

        if uploaded_file.name.lower().endswith(".zip"):
            data = pd.read_csv(
                io.BytesIO(file_bytes),
                sep=";",
                na_values=["?"],
                low_memory=False,
                compression="zip"
            )
        else:
            data = pd.read_csv(
                io.BytesIO(file_bytes),
                sep=";",
                na_values=["?"],
                low_memory=False
            )

        required_columns = [
            "Date", "Time", "Global_active_power",
            "Global_reactive_power", "Voltage",
            "Global_intensity", "Sub_metering_1",
            "Sub_metering_2", "Sub_metering_3"
        ]

        missing_columns = [
            col for col in required_columns if col not in data.columns
        ]

        if missing_columns:
            st.error("The uploaded dataset does not contain all required columns.")
            st.stop()

        data["Date"] = pd.to_datetime(
            data["Date"],
            format="%d/%m/%Y",
            errors="coerce"
        )

        numeric_columns = [
            "Global_active_power",
            "Global_reactive_power",
            "Voltage",
            "Global_intensity",
            "Sub_metering_1",
            "Sub_metering_2",
            "Sub_metering_3"
        ]

        for col in numeric_columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

        data["DateTime"] = pd.to_datetime(
            data["Date"].dt.strftime("%Y-%m-%d") + " " + data["Time"],
            errors="coerce"
        )

        data = data[
            (data["DateTime"] >= "2009-12-01") &
            (data["DateTime"] < "2010-11-27")
        ].copy()

        data = data.dropna(subset=["DateTime"])
        data = data.drop_duplicates(subset=["DateTime"])
        data = data.sort_values("DateTime")
        data = data.set_index("DateTime")

        if data.empty:
            st.error("No records found for the selected project period.")
            st.stop()

        missing_before = data[numeric_columns].isnull().sum()

        data[numeric_columns] = data[numeric_columns].interpolate(
            method="time",
            limit=5,
            limit_area="inside"
        )

        st.success("Dataset uploaded and processed successfully!")

        st.sidebar.subheader("Dataset Information")
        st.sidebar.write("Total Records:", f"{len(data):,}")
        st.sidebar.write(
            "Period:",
            f"{data.index.min().date()} to {data.index.max().date()}"
        )

        average_power = data["Global_active_power"].mean()
        highest_power = data["Global_active_power"].max()

        monthly_energy = (
            data["Global_active_power"].resample("MS").sum(min_count=1) / 60
        )

        hourly_pattern = data.groupby(
            data.index.hour
        )["Global_active_power"].mean()

        weekday_order = [
            "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"
        ]

        weekday_usage = data.groupby(
            data.index.day_name()
        )["Global_active_power"].mean().reindex(weekday_order)

        st.header("Electricity Consumption Overview")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Average Power", f"{average_power:.2f} kW")
        col2.metric("Highest Power", f"{highest_power:.2f} kW")
        col3.metric("Total Records", f"{len(data):,}")
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
            data[submeter_columns].resample("MS").sum(min_count=1) / 1000
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

        correlation_data = data[numeric_columns].corr()

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
            st.dataframe(
                missing_before.to_frame("Missing Values")
            )

        with quality_col2:
            st.write("Remaining Missing Values")
            st.dataframe(
                data[numeric_columns].isnull().sum().to_frame(
                    "Missing Values"
                )
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

        cleaned_csv = data.to_csv().encode("utf-8")

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
        st.error(f"Unable to process the uploaded file: {e}")

else:
    st.info("Please upload the household_power_consumption.txt.zip dataset using the sidebar.")
