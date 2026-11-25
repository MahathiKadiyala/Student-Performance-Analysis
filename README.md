# Student Performance Analysis

A Python project for exploring student academic data, summarizing performance, and visualizing student results. It includes a Streamlit dashboard, a command-line analysis script, and a FastAPI service.

## Features

- Prepare student data and derive performance indicators
- Calculate summary statistics, including class average, pass rate, at-risk count, and dropout count
- Generate static charts and interactive Plotly visualizations
- Explore student results and at-risk students in a Streamlit dashboard
- Serve summary, student-listing, and estimated-result endpoints through FastAPI

## Technologies

- Python
- Pandas and NumPy
- Matplotlib and Plotly
- Streamlit
- FastAPI, Pydantic, and Uvicorn

## Setup

Use Python 3. Install the dependencies from the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The scripts expect the dataset at `data/Maths.csv`. The supplied file is named `data/maths.csv`; Windows treats these names as equivalent, but case-sensitive systems do not. For those systems, rename the file to `Maths.csv` or update the path in the Python scripts.

## Run

Start the Streamlit dashboard:

```powershell
streamlit run app.py
```

Run the analysis script:

```powershell
python analysis.py
```

Start the API locally:

```powershell
uvicorn main:app --reload
```

The API documentation is available at `http://127.0.0.1:8000/docs` while the API is running. The analysis script also opens interactive charts, which may require a graphical or browser-capable environment.
