# app.py

# Import required libraries
import streamlit as st
import pandas as pd
import plotly.express as px


# Configure the Streamlit page
st.set_page_config(
    page_title="Student Academic Risk Intelligence System",
    layout="wide",
    page_icon="🎓"
)


# -------------------------------
# Load and Prepare Data
# -------------------------------

# Load the Maths dataset from the data folder
df = pd.read_csv("data/Maths.csv")

# Create Result based on the final grade G3
# G3 = 0       -> Dropout
# G3 = 1 to 9  -> Fail
# G3 = 10 to 20 -> Pass
df["Result"] = df["G3"].apply(
    lambda x: "Dropout" if x == 0 else ("Fail" if x <= 9 else "Pass")
)

# Convert final grade into percentage
df["Percentage"] = (df["G3"] / 20) * 100

# Calculate average alcohol consumption
df["avg_alcohol"] = (df["Dalc"] + df["Walc"]) / 2

# Calculate average parent education level
df["parent_edu_avg"] = (df["Medu"] + df["Fedu"]) / 2

# Calculate grade trend from G1 to G3
df["grade_trend"] = df["G3"] - df["G1"]

# Count "yes" values across support-related columns
support_columns = ["schoolsup", "famsup", "paid"]
df["total_support"] = df[support_columns].eq("yes").sum(axis=1)

# Calculate the academic risk score
df["risk_score"] = (
    (df["failures"] * 2)
    + (df["absences"] / 10)
    + df["avg_alcohol"]
    - df["studytime"]
)

# Calculate average of G1 and G2
df["g1_g2_avg"] = (df["G1"] + df["G2"]) / 2


# -------------------------------
# Main Dashboard Title
# -------------------------------

st.title("🎓 Student Academic Risk Intelligence System")


# -------------------------------
# Calculate KPI Values
# -------------------------------

# Exclude dropouts for academic performance calculations
non_dropout = df[df["G3"] != 0]

# Calculate total number of students
total_students = len(df)

# Calculate average G3 excluding dropouts
class_average_g3 = round(non_dropout["G3"].mean(), 2)

# Calculate number of passing students
pass_count = (non_dropout["G3"] >= 10).sum()

# Calculate pass rate among non-dropout students
pass_rate = round((pass_count / len(non_dropout)) * 100, 1)

# Calculate number of at-risk students (G3 between 1 and 9)
at_risk_count = ((df["G3"] >= 1) & (df["G3"] <= 9)).sum()


# -------------------------------
# Display KPI Cards in One Row
# -------------------------------

# Create four columns for the KPI cards
col1, col2, col3, col4 = st.columns(4)

# Card 1: Total Students
with col1:
    st.metric(
        label="Total Students",
        value=total_students
    )

# Card 2: Class Average G3
with col2:
    st.metric(
        label="Class Average G3",
        value=f"{class_average_g3:.2f}"
    )

# Card 3: Pass Rate
with col3:
    st.metric(
        label="Pass Rate %",
        value=f"{pass_rate:.1f}%"
    )

# Card 4: At-Risk Count
with col4:
    st.metric(
        label="At-Risk Count",
        value=at_risk_count
    )

# -------------------------------
# Performance Charts
# -------------------------------

# Display the Performance Charts section heading
st.subheader("📊 Performance Charts")

# Create two columns to display the charts side by side
chart_col1, chart_col2 = st.columns(2)


# -------------------------------
# Left Chart: Study Time vs Final Grade
# -------------------------------

with chart_col1:
    # Define colors for each student result category
    result_colors = {
        "Pass": "green",
        "Fail": "red",
        "Dropout": "grey"
    }

    # Create the interactive scatter plot
    fig_scatter = px.scatter(
        df,
        x="studytime",
        y="G3",
        color="Result",
        color_discrete_map=result_colors,
        hover_data=["absences", "G1", "G2"],
        title="Study Time vs Final Grade"
    )

    # Display the scatter plot using the full column width
    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )


# -------------------------------
# Right Chart: Average G3 by Internet Access
# -------------------------------

with chart_col2:
    # Calculate average G3 for each internet access group
    avg_g3_by_internet = (
        df.groupby("internet", as_index=False)["G3"]
        .mean()
        .rename(columns={"G3": "average_G3"})
    )

    # Create the interactive bar chart
    fig_bar = px.bar(
        avg_g3_by_internet,
        x="internet",
        y="average_G3",
        color="internet",
        title="Average G3 by Internet Access"
    )

    # Display the bar chart using the full column width
    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )
# -------------------------------
# Student Analysis Table
# -------------------------------

# Display the Student Analysis Table section heading
st.subheader("🚨 Student Analysis Table")

# Create a dropdown to filter students by their result
result_filter = st.selectbox(
    "Filter by Result",
    ["All", "Pass", "Fail", "Dropout"]
)

# Filter the DataFrame based on the selected result
if result_filter == "All":
    filtered_df = df
else:
    filtered_df = df[df["Result"] == result_filter]

# Select only the required columns for the student analysis table
analysis_columns = [
    "G1",
    "G2",
    "G3",
    "Result",
    "Percentage",
    "absences",
    "studytime",
    "failures",
    "risk_score"
]

# Display the filtered student DataFrame
st.dataframe(
    filtered_df[analysis_columns],
    use_container_width=True
)


# -------------------------------
# At-Risk Students
# -------------------------------

# Display the At-Risk Students section heading
st.subheader("⚠️ At-Risk Students")

# Filter students whose G3 is between 1 and 9
at_risk_df = df[
    (df["G3"] >= 1) &
    (df["G3"] <= 9)
].copy()

# Sort at-risk students by G3 in ascending order
# Lowest G3 appears first
at_risk_df = at_risk_df.sort_values(
    by="G3",
    ascending=True
)

# Select only the required columns for the at-risk table
at_risk_columns = [
    "G1",
    "G2",
    "G3",
    "absences",
    "studytime",
    "failures"
]

# Display the total number of at-risk students
st.write(f"Total at-risk students: {len(at_risk_df)}")

# Display the sorted at-risk students table
st.dataframe(
    at_risk_df[at_risk_columns],
    use_container_width=True
)