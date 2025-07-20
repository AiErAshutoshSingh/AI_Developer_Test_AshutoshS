
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# Flask API URL (your local server)
url = "http://127.0.0.1:5000/tasks"

# Fetch data
response = requests.get(url)

# Check for error
if response.status_code != 200:
    raise Exception("Failed to fetch task data")

tasks = response.json()

# Convert to DataFrame
df = pd.DataFrame(tasks)

# Drop missing status or due_date
df.dropna(subset=["status", "due_date"], inplace=True)

# Convert due_date to datetime
df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce")

# Drop invalid date rows
df = df.dropna(subset=["due_date"])

# Count tasks by status
status_counts = df["status"].value_counts().reset_index()
status_counts.columns = ["status", "count"]

# Plot bar chart
fig = px.bar(status_counts, x="status", y="count",
             title="Task Count by Status",
             labels={"status": "Status", "count": "Number of Tasks"},
             color="status")

# Save chart
fig.write_html("task_chart.html")
print("✅ Chart saved as task_chart.html")
