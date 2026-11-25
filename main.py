# main.py

# Import required libraries
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
import uvicorn
from pydantic import BaseModel, Field


# Create the FastAPI application
app = FastAPI(
    title="Student Academic Risk Intelligence System API",
    description="API for analyzing student performance data",
    version="1.0.0"
)


def load_data():
    """
    Load and prepare the Maths.csv dataset with the same
    feature engineering used in analysis.py.
    """

    # Load the Maths dataset from the data folder
    df = pd.read_csv("data/Maths.csv")

    # Create Result based on the final grade G3
    # G3 = 0       -> Dropout
    # G3 = 1 to 9  -> Fail
    # G3 = 10 to 20 -> Pass
    df["Result"] = df["G3"].apply(
        lambda x: "Dropout" if x == 0 else ("Fail" if x <= 9 else "Pass")
    )

    # Convert G3 into percentage
    df["Percentage"] = (df["G3"] / 20) * 100

    # Calculate average alcohol consumption
    df["avg_alcohol"] = (df["Dalc"] + df["Walc"]) / 2

    # Calculate average parent education level
    df["parent_edu_avg"] = (df["Medu"] + df["Fedu"]) / 2

    # Calculate the change in grade from G1 to G3
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

    # Calculate the average of G1 and G2
    df["g1_g2_avg"] = (df["G1"] + df["G2"]) / 2

    # Return the completely prepared DataFrame
    return df


# Load the dataset when the application starts
df = load_data()

# Endpoint 1: Return overall academic performance summary
@app.get("/summary")
def get_summary():
    # Exclude dropouts (G3 = 0) for performance calculations
    non_dropout = df[df["G3"] != 0]

    # Calculate total number of students
    total_students = len(df)

    # Calculate average G3 using non-dropout students only
    class_average_g3 = non_dropout["G3"].mean()

    # Calculate the number of passing students (G3 >= 10)
    pass_count = (non_dropout["G3"] >= 10).sum()

    # Calculate pass rate among non-dropout students only
    pass_rate_percent = (pass_count / len(non_dropout)) * 100

    # Count students with G3 between 1 and 9 (at-risk/fail)
    at_risk_count = ((df["G3"] >= 1) & (df["G3"] <= 9)).sum()

    # Count students with G3 equal to 0 (dropouts)
    dropout_count = (df["G3"] == 0).sum()

    # Return the summary as JSON
    return {
        "total_students": int(total_students),
        "class_average_g3": round(float(class_average_g3), 2),
        "pass_rate_percent": round(float(pass_rate_percent), 2),
        "at_risk_count": int(at_risk_count),
        "dropout_count": int(dropout_count)
    }


# Endpoint 2: Return students who are at academic risk
@app.get("/at-risk")
def get_at_risk_students():
    # Filter students whose G3 is between 1 and 9
    at_risk = df[(df["G3"] >= 1) & (df["G3"] <= 9)].copy()

    # Sort by G3 in ascending order so the lowest grades appear first
    at_risk = at_risk.sort_values(by="G3", ascending=True)

    # Convert the required columns into a list of dictionaries
    students = []

    for index, row in at_risk.iterrows():
        students.append({
            "student_index": int(index),
            "G1": int(row["G1"]),
            "G2": int(row["G2"]),
            "G3": int(row["G3"]),
            "absences": int(row["absences"])
        })

    # Return the list of at-risk students
    return students


# Endpoint 3: Return the top 5 students by final grade
@app.get("/top-students")
def get_top_students():
    # Exclude dropouts and sort students by G3 in descending order
    top_students = (
        df[df["G3"] != 0]
        .sort_values(by="G3", ascending=False)
        .head(5)
    )

    # Convert the required columns into a list of dictionaries
    students = []

    for index, row in top_students.iterrows():
        students.append({
            "student_index": int(index),
            "G1": int(row["G1"]),
            "G2": int(row["G2"]),
            "G3": int(row["G3"])
        })

    # Return the top 5 students
    return students
# Pydantic model for validating student input data
class StudentInput(BaseModel):
    # First-period grade: must be between 0 and 20
    G1: float = Field(
        ...,
        ge=0,
        le=20,
        description="G1 grade must be between 0 and 20"
    )

    # Second-period grade: must be between 0 and 20
    G2: float = Field(
        ...,
        ge=0,
        le=20,
        description="G2 grade must be between 0 and 20"
    )

    # Study time level: must be between 1 and 4
    studytime: int = Field(
        ...,
        ge=1,
        le=4,
        description="Study time must be between 1 and 4"
    )

    # Number of absences: must be between 0 and 100
    absences: int = Field(
        ...,
        ge=0,
        le=100,
        description="Absences must be between 0 and 100"
    )

    # Number of previous failures: must be between 0 and 4
    failures: int = Field(
        ...,
        ge=0,
        le=4,
        description="Failures must be between 0 and 4"
    )


# POST endpoint for predicting the student's academic result
@app.post("/predict-result")
def predict_result(student: StudentInput):
    # Calculate the estimated final grade using the given formula
    estimated_g3 = (
        (student.G1 * 0.3)
        + (student.G2 * 0.6)
        + (student.studytime * 0.3)
        - (student.failures * 1.5)
        - (student.absences * 0.05)
    )

    # Clamp the estimated grade between 0 and 20
    estimated_g3 = max(0, min(20, estimated_g3))

    # Determine the predicted academic result
    if estimated_g3 == 0:
        prediction = "Dropout Risk"
    elif estimated_g3 < 10:
        prediction = "Fail"
    else:
        prediction = "Pass"

    # Determine prediction confidence based on G1 and G2
    if (student.G1 > 12 and student.G2 > 12) or (
        student.G1 < 8 and student.G2 < 8
    ):
        confidence = "High"
    else:
        confidence = "Medium"

    # Return the prediction details as JSON
    return {
        "estimated_g3": round(estimated_g3, 2),
        "prediction": prediction,
        "confidence": confidence
    }
# Root endpoint: provides basic API information
@app.get("/")
def root():
    return {
        "message": "Student Academic Risk Intelligence System API",
        "docs": "Visit /docs for full API documentation",
        "version": "1.0.0"
    }


# Run the FastAPI application directly with Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )