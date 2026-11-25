def load_and_prepare_data(filepath):
    import pandas as pd

    # Load the CSV file into a Pandas DataFrame
    df = pd.read_csv(filepath)

    # Create Result based on the final grade (G3)
    # G3 = 0      -> Dropout
    # G3 = 1 to 9 -> Fail
    # G3 = 10 to 20 -> Pass
    df["Result"] = df["G3"].apply(
        lambda x: "Dropout" if x == 0 else ("Fail" if x <= 9 else "Pass")
    )

    # Convert final grade into percentage
    df["Percentage"] = (df["G3"] / 20) * 100

    # Calculate average alcohol consumption
    df["avg_alcohol"] = (df["Dalc"] + df["Walc"]) / 2

    # Calculate average education level of parents
    df["parent_edu_avg"] = (df["Medu"] + df["Fedu"]) / 2

    # Calculate the grade trend from first grade to final grade
    df["grade_trend"] = df["G3"] - df["G1"]

    # Count the number of "yes" values across support-related columns
    support_columns = ["schoolsup", "famsup", "paid"]
    df["total_support"] = (
        df[support_columns].eq("yes").sum(axis=1)
    )

    # Calculate the academic risk score
    df["risk_score"] = (
        (df["failures"] * 2)
        + (df["absences"] / 10)
        + df["avg_alcohol"]
        - df["studytime"]
    )

    # Calculate the average of G1 and G2
    df["g1_g2_avg"] = (df["G1"] + df["G2"]) / 2

    # Return the complete prepared DataFrame
    return df

def calculate_statistics(df):
    import numpy as np

    # Exclude dropouts (G3 = 0) for academic performance statistics
    non_dropout = df[df["G3"] != 0]

    # Calculate the average final grade (G3) among non-dropout students
    class_avg_g3 = np.mean(non_dropout["G3"].values)

    # Calculate the number of non-dropout students who passed (G3 >= 10)
    pass_count = np.sum(non_dropout["G3"].values >= 10)

    # Calculate pass rate as a percentage of non-dropout students
    pass_rate = (pass_count / len(non_dropout)) * 100

    # Count students who dropped out (G3 = 0)
    dropout_count = np.sum(df["G3"].values == 0)

    # Count students who are at risk (G3 between 1 and 9)
    at_risk_count = np.sum(
        (df["G3"].values >= 1) & (df["G3"].values <= 9)
    )

    # Extract G1, G2, and G3 for non-dropout students
    grades = non_dropout[["G1", "G2", "G3"]].values

    # Calculate the correlation matrix using NumPy
    correlation_matrix = np.corrcoef(grades, rowvar=False)

    # Return all calculated statistics as a dictionary
    return {
        "class_avg_g3": class_avg_g3,
        "pass_rate": pass_rate,
        "dropout_count": dropout_count,
        "at_risk_count": at_risk_count,
        "correlation_matrix": correlation_matrix
    }
def generate_static_charts(df):
    import os
    import matplotlib.pyplot as plt

    # Create the output folder if it does not already exist
    os.makedirs("output", exist_ok=True)

    # -------------------------------
    # Chart 1: Average G3 by Study Time
    # -------------------------------

    # Calculate the average G3 for each studytime level
    avg_g3_by_studytime = df.groupby("studytime")["G3"].mean()

    # Ensure all studytime levels 1, 2, 3, and 4 are included
    studytime_levels = [1, 2, 3, 4]
    avg_g3_values = [
        avg_g3_by_studytime.get(level, 0)
        for level in studytime_levels
    ]

    # Create the bar chart
    plt.figure(figsize=(8, 5))
    plt.bar(studytime_levels, avg_g3_values)

    # Add chart title and axis labels
    plt.title("Average G3 by Study Time")
    plt.xlabel("Study Time (1=<2hrs, 2=2-5hrs, 3=5-10hrs, 4=>10hrs)")
    plt.ylabel("Average G3")

    # Set the X-axis ticks to studytime levels
    plt.xticks(studytime_levels)

    # Adjust layout to prevent label overlap
    plt.tight_layout()

    # Save the chart
    plt.savefig("output/avg_g3_by_studytime.png")

    # Close the chart to free memory
    plt.close()

    # -------------------------------
    # Chart 2: Student Result Distribution
    # -------------------------------

    # Count students in each result category
    result_counts = df["Result"].value_counts()

    # Ensure the categories appear in the required order
    result_labels = ["Pass", "Fail", "Dropout"]
    result_values = [
        result_counts.get(label, 0)
        for label in result_labels
    ]

    # Create the pie chart
    plt.figure(figsize=(7, 7))
    plt.pie(
        result_values,
        labels=result_labels,
        autopct="%1.1f%%"
    )

    # Add chart title
    plt.title("Student Result Distribution")

    # Adjust layout
    plt.tight_layout()

    # Save the chart
    plt.savefig("output/pass_fail_dropout_pie.png")

    # Close the chart to free memory
    plt.close()
def generate_interactive_charts(df):
    import plotly.express as px

    # -------------------------------
    # Chart 1: Study Time vs Final Grade
    # -------------------------------

    # Define colors for each student result category
    result_colors = {
        "Pass": "green",
        "Fail": "red",
        "Dropout": "grey"
    }

    # Create an interactive scatter plot
    fig1 = px.scatter(
        df,
        x="studytime",
        y="G3",
        color="Result",
        color_discrete_map=result_colors,
        hover_data=["absences", "G1", "G2"],
        title="Study Time vs Final Grade (G3)"
    )

    # Display the interactive scatter plot
    fig1.show()

    # -------------------------------
    # Chart 2: Average G3 by Internet Access
    # -------------------------------

    # Calculate the average G3 for students with and without internet access
    avg_g3_by_internet = (
        df.groupby("internet", as_index=False)["G3"]
        .mean()
        .rename(columns={"G3": "average_G3"})
    )

    # Create an interactive bar chart
    fig2 = px.bar(
        avg_g3_by_internet,
        x="internet",
        y="average_G3",
        color="internet",
        title="Average G3 by Internet Access"
    )

    # Display the interactive bar chart
    fig2.show()
def print_summary(stats):
    # Print a clean formatted heading
    print("=" * 48)
    print("STUDENT ACADEMIC RISK INTELLIGENCE SYSTEM")
    print("ANALYSIS SUMMARY")
    print("=" * 48)

    # Print the calculated statistics in a formatted table
    # Note: Total students is calculated from dropout + at-risk + pass students
    total_students = (
        stats["dropout_count"]
        + stats["at_risk_count"]
        + round(
            (stats["pass_rate"] / 100)
            * (stats["dropout_count"] + stats["at_risk_count"])
            / (1 - stats["pass_rate"] / 100)
        )
    )

    print(f"Total Students        : {total_students}")
    print(f"Class Average G3      : {stats['class_avg_g3']:.2f}")
    print(f"Pass Rate             : {stats['pass_rate']:.2f}%")
    print(f"At-Risk Count         : {stats['at_risk_count']}")
    print(f"Dropout Count         : {stats['dropout_count']}")

    # Print the closing separator
    print("=" * 48)


if __name__ == "__main__":
    # Load and prepare the student dataset
    df = load_and_prepare_data("data/Maths.csv")

    # Calculate academic statistics
    stats = calculate_statistics(df)

    # Generate and save static Matplotlib charts
    generate_static_charts(df)

    # Generate and display interactive Plotly charts
    generate_interactive_charts(df)

    # Print the analysis summary
    print_summary(stats)

    # Confirm that the analysis has completed
    print("Analysis complete. Charts saved to output/ folder")
