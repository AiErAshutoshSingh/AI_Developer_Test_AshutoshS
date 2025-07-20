from flask import Flask, request, jsonify
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from datetime import datetime, date
import os
from uuid import uuid4
from typing import List, Dict
import re

app = Flask(__name__)

# In-memory task storage
tasks: List[Dict] = []

# Initialize Groq LLM with LangChain
llm = ChatGroq(api_key="############API##################", model="mixtral-8x7b-32768")
prompt_template = PromptTemplate(
    input_variables=["query", "tasks"],
    template="""
    You are a task management assistant. Given a natural language query and a list of tasks, return a JSON response with the filtered tasks that match the query. If no tasks match, return an empty list.

    Query: {query}
    Tasks: {tasks}

    Return format:
    {
        "tasks": [
            {"id": "task_id", "title": "task_title", "description": "task_description", "status": "task_status", "due_date": "YYYY-MM-DD"}
        ]
    }
    """
)

llm_chain = LLMChain(llm=llm, prompt=prompt_template)

# Helper function to validate date format
def is_valid_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# POST /tasks - Create a new task
@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()

    # Validate input
    if not data or not all(key in data for key in ["title", "description", "status"]):
        return jsonify({"error": "Missing required fields: title, description, status"}), 400

    if not isinstance(data["title"], str) or not isinstance(data["description"], str) or not isinstance(data["status"], str):
        return jsonify({"error": "Invalid field types"}), 400

    if data["status"] not in ["pending", "in-progress", "completed"]:
        return jsonify({"error": "Invalid status. Must be pending, in-progress, or completed"}), 400

    # Validate due_date if provided
    due_date = data.get("due_date")
    if due_date and not is_valid_date(due_date):
        return jsonify({"error": "Invalid due_date format. Use YYYY-MM-DD"}), 400

    task = {
        "id": str(uuid4()),
        "title": data["title"],
        "description": data["description"],
        "status": data["status"],
        "due_date": due_date or None
    }

    tasks.append(task)
    return jsonify({"message": "Task created", "task": task}), 201

# GET /tasks - Fetch all tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify({"tasks": tasks}), 200

# POST /query - Process natural language query
@app.route("/query", methods=["POST"])
def query_tasks():
    data = request.get_json()

    if not data or "query" not in data:
        return jsonify({"error": "Missing query field"}), 400

    query = data["query"]
    if not isinstance(query, str) or not query.strip():
        return jsonify({"error": "Query must be a non-empty string"}), 400

    try:
        # Prepare tasks for LLM
        tasks_str = "\n".join([f"ID: {task['id']}, Title: {task['title']}, Description: {task['description']}, Status: {task['status']}, Due Date: {task['due_date'] or 'None'}" for task in tasks])

        # Run LangChain with the query
        response = llm_chain.run(query=query, tasks=tasks_str)

        # Parse LLM response (assuming it returns JSON-like string)
        try:
            result = eval(response.strip()) if response.strip() else {"tasks": []}
            if not isinstance(result, dict) or "tasks" not in result:
                raise ValueError("Invalid response format")
        except Exception as e:
            return jsonify({"error": "Failed to parse AI response", "details": str(e)}), 500

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "Error processing query", "details": str(e)}), 500

# Error handling for unexpected errors
@app.errorhandler(Exception)
def handle_error(error):
    return jsonify({"error": "Internal server error", "details": str(error)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
