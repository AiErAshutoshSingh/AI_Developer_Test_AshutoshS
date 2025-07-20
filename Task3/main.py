from flask import Flask, jsonify

app = Flask(__name__)

# Sample task data
tasks = [
    {"id": 1, "title": "Complete Report", "status": "In Progress", "due_date": "2025-07-25"},
    {"id": 2, "title": "Team Meeting", "status": "Completed", "due_date": "2025-07-18"},
    {"id": 3, "title": "Submit Code", "status": "Pending", "due_date": "2025-07-22"},
    {"id": 4, "title": "Review PR", "status": "In Progress", "due_date": "2025-07-19"},
    {"id": 5, "title": "Update Docs", "status": "Completed", "due_date": "2025-07-15"},
    {"id": 6, "title": "Fix Bug", "status": "", "due_date": None},  # invalid row
]

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

if __name__ == '__main__':
    app.run(debug=True)
