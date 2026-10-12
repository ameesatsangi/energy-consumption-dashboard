# Energy Consumption and Sustainability Analytics ⚡

## About the Project

Energy Consumption and Sustainability Analytics is my Data Analytics PBL project for B.Tech Computer Science and Engineering (AIML).

The main aim of this project is to understand how electricity is used in a household, identify periods of high and low consumption, and explore simple ways to save energy.

I have developed an interactive dashboard using Python and Streamlit so that users can upload the electricity dataset and explore the results through charts and summary statistics.

## Project Objectives

- Understand household electricity consumption patterns.
- Analyze electricity usage by hour, day, and month.
- Identify the hours with higher average electricity usage.
- Compare consumption patterns across weekdays.
- Explore relationships between different electrical measurements.
- Suggest practical energy-saving habits.

## Dataset Used

**Dataset:** Household Electric Power Consumption

**Source:** [Kaggle Dataset](https://www.kaggle.com/datasets/uciml/electric-power-consumption-data-set)

The dataset contains minute-level electricity measurements from one household in Sceaux, France, collected between December 2006 and November 2010.

For this project, I selected the period from December 2009 to November 2010. The dataset ends on November 26, 2010, so the data for November 2010 is incomplete.

Missing readings marked with `?` are handled during data preprocessing.

## Tools and Technologies

- Python
- Pandas and NumPy
- Matplotlib and Seaborn
- Plotly
- Streamlit
- GitHub

## Live Dashboard

You can access my deployed dashboard here:

**[Energy Consumption and Sustainability Analytics](https://energy-consumption-dashboard-crrdzv2qcrhh9puwb68rhg.streamlit.app/)**

## Dashboard Features

The dashboard includes:

- Dataset upload for ZIP, TXT, and CSV files
- Summary cards showing important statistics
- Monthly estimated energy consumption
- Hourly electricity usage patterns
- Weekday consumption comparisons
- Correlation heatmap for electrical measurements
- Data quality information
- Downloadable CSV files
- Energy-saving recommendations

## Key Findings

The current dashboard reports these results for the selected analysis period:

- Average active power: approximately 1.09 kW
- Highest recorded active power: approximately 9.72 kW
- Estimated energy consumption: approximately 9,104 kWh
- Peak average usage hour: 8:00 PM (20:00)

These values describe the selected dataset and should be checked against the final analysis output before submission.

## Energy-Saving Suggestions

Based on the analysis, some practical ways to reduce electricity consumption include:

- Switching off lights and electrical devices when they are not being used.
- Using energy-efficient appliances and LED lighting.
- Shifting flexible electricity usage away from peak-demand periods where practical.
- Monitoring electricity usage regularly.
- Reviewing monthly consumption to identify opportunities for saving energy.

## Limitations

- The dataset represents one household in France, so the results may not apply to every household.
- November 2010 contains only partial-month data.
- Monthly energy consumption values are estimates.
- The sub-metering measurements are not directly linked to specific appliance names.
- The findings describe observed patterns and do not prove that the same patterns occur in all households.

## How to Run the Project Locally

1. Install Python on your computer.

2. Clone this repository:

   ```bash
   git clone https://github.com/ameesatsangi/energy-consumption-dashboard.git
   ```

3. Open the project folder:

   ```bash
   cd energy-consumption-dashboard
   ```

4. Install the required packages:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Start the Streamlit application:

   ```bash
   python -m streamlit run app.py
   ```

6. Open the local URL shown in your terminal and upload the original dataset to explore the dashboard.

## Conclusion

This project helped me understand how data analytics can be used to study electricity consumption, identify usage patterns, and support more sustainable energy habits.

It combines data preprocessing, exploratory data analysis, visualization, and interactive dashboard development in one practical application.

---

**Project Title:** Energy Consumption and Sustainability Analytics  
**Course:** B.Tech Computer Science and Engineering (AIML)  
**Project Type:** Data Analytics PBL
