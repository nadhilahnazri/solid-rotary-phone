import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
from datetime import datetime, timedelta
import pygame
from PIL import Image

# ----------------------- MongoDB Configuration -----------------------
MONGO_URI = "mongodb+srv://sc22mmbh:gtd7grQKEf7M9SkL@cluster0.8gz5z.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["tracker"]  # Database name
tasks_collection = db["tasks"]  # Tasks collection
forest_collection = db["forest"]  # Forest collection

# ----------------------- Helper Functions -----------------------
# Fetch tasks from MongoDB
def fetch_tasks():
    tasks = list(tasks_collection.find())
    if tasks:
        for task in tasks:
            task["_id"] = str(task["_id"])  # Convert ObjectId to string for compatibility
        return pd.DataFrame(tasks)
    else:
        return pd.DataFrame(columns=["_id", "Category", "Task", "Estimated Time", "Elapsed Time", "Completed", "Due Date"])

# Add task to MongoDB
def add_task(category, task, estimated_time, due_date):
    task_doc = {
        "Category": category,
        "Task": task,
        "Estimated Time": estimated_time,
        "Elapsed Time": 0,
        "Completed": False,
        "Due Date": due_date.isoformat(),
    }
    tasks_collection.insert_one(task_doc)

# Update task in MongoDB
def update_task(task_id, updates):
    tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": updates})

# Delete task from MongoDB
def delete_task(task_id):
    tasks_collection.delete_one({"_id": ObjectId(task_id)})

# Fetch forest from MongoDB
def fetch_forest():
    forest = forest_collection.find_one()
    if forest:
        del forest["_id"]  # Remove the MongoDB ObjectId field
    return forest if forest else {}

# Save forest to MongoDB
def save_forest(forest):
    # Ensure topics are lists
    for subject, topics in forest.items():
        if not isinstance(topics, list):
            forest[subject] = []  # Default to an empty list
    forest_collection.delete_many({})  # Clear old forest
    forest_collection.insert_one(forest)

# ----------------------- Forest Visualization Functions -----------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
TREE_TRUNK = (139, 69, 19)
LEAF_GREEN = (50, 205, 50)
DARK_GREEN = (0, 128, 0)

def draw_tree(surface, x, y, trunk_width, trunk_height, foliage_radius, subject_name):
    trunk_rect = pygame.Rect(x, y - trunk_height, trunk_width, trunk_height)
    pygame.draw.rect(surface, TREE_TRUNK, trunk_rect)
    pygame.draw.circle(surface, LEAF_GREEN, (x + trunk_width // 2, y - trunk_height), foliage_radius)
    pygame.draw.circle(surface, DARK_GREEN, (x + trunk_width // 2 - foliage_radius // 2, y - trunk_height + foliage_radius // 2), foliage_radius)
    pygame.draw.circle(surface, DARK_GREEN, (x + trunk_width // 2 + foliage_radius // 2, y - trunk_height + foliage_radius // 2), foliage_radius)
    font = pygame.font.Font(None, 24)
    text_surface = font.render(subject_name, True, (0, 0, 0))
    surface.blit(text_surface, (x + trunk_width // 2 - text_surface.get_width() // 2, y + 10))

def draw_forest(subjects):
    pygame.init()
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surface.fill(SKY_BLUE)
    pygame.draw.rect(surface, GRASS_GREEN, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))

    tree_spacing = SCREEN_WIDTH // (len(subjects) + 1)
    x_positions = [tree_spacing * (i + 1) for i in range(len(subjects))]
    for i, (subject, topics) in enumerate(subjects.items()):
        x = x_positions[i]
        y = SCREEN_HEIGHT // 2
        trunk_width = 30
        trunk_height = 50 + len(topics) * 20 if isinstance(topics, list) else 50
        foliage_radius = 40
        draw_tree(surface, x, y, trunk_width, trunk_height, foliage_radius, subject)

    return surface

def pygame_to_image(surface):
    img_str = pygame.image.tostring(surface, "RGB")
    img = Image.frombytes("RGB", (surface.get_width(), surface.get_height()), img_str)
    return img

# ----------------------- Main App -----------------------
st.title("🌳 Unified Productivity and Knowledge Forest App 🌳")

# Load data
tasks_df = fetch_tasks()
forest = fetch_forest()

# Sidebar for Task Management
st.sidebar.header("Task Management")
category = st.sidebar.selectbox("Category", ["Distributed Systems", "AI", "Reading", "Careers", "Machine Learning"])
task_name = st.sidebar.text_input("Task Name")
estimated_time = st.sidebar.number_input("Estimated Time (hours)", min_value=0.0, step=0.5)
due_date = st.sidebar.date_input("Due Date")

if st.sidebar.button("Add Task"):
    if task_name and estimated_time > 0:
        add_task(category, task_name, estimated_time, due_date)
        st.sidebar.success("Task added successfully!")
    else:
        st.sidebar.error("Please fill in all fields.")

# Sidebar for Knowledge Forest
st.sidebar.header("Knowledge Forest")
new_subject = st.sidebar.text_input("Add a New Subject:")
if st.sidebar.button("Add Subject"):
    if new_subject and new_subject not in forest:
        forest[new_subject] = []
        save_forest(forest)
        st.sidebar.success(f"Added subject: {new_subject}")
    elif new_subject in forest:
        st.sidebar.warning(f"Subject '{new_subject}' already exists!")
    else:
        st.sidebar.warning("Subject name cannot be empty!")

subject_choice = st.sidebar.selectbox("Select Subject to Add Topics:", [""] + list(forest.keys()))
if subject_choice:
    new_topic = st.sidebar.text_input("Add a New Topic:")
    if st.sidebar.button("Add Topic"):
        if new_topic and new_topic not in forest[subject_choice]:
            forest[subject_choice].append(new_topic)
            save_forest(forest)
            st.sidebar.success(f"Added topic '{new_topic}' to subject '{subject_choice}'")
        elif new_topic in forest[subject_choice]:
            st.sidebar.warning(f"Topic '{new_topic}' already exists in '{subject_choice}'!")
        else:
            st.sidebar.warning("Topic name cannot be empty!")

# Display Tasks
st.header("Task Management")
for _, row in tasks_df.iterrows():
    col1, col2, col3 = st.columns([5, 3, 2])
    col1.write(f"**{row['Task']}** ({row['Category']})")
    col2.write(f"Due: {row['Due Date']}")
    col3.write(f"Estimated: {row['Estimated Time']} hrs")
    if row["Completed"]:
        col1.write(":white_check_mark: Completed")
    else:
        if col1.button("Start Timer", key=f"start_{row['_id']}"):
            st.session_state.timer_running = True
            st.session_state.current_task = row["_id"]
            st.session_state.start_time = datetime.now()
        if col2.button("Mark as Done", key=f"done_{row['_id']}"):
            update_task(row["_id"], {"Completed": True})
        if col3.button("Delete Task", key=f"delete_{row['_id']}"):
            delete_task(row["_id"])

# Knowledge Forest Visualization
st.header("Knowledge Forest")
if forest:
    forest_surface = draw_forest(forest)
    forest_image = pygame_to_image(forest_surface)
    st.image(forest_image, caption="Knowledge Forest", use_container_width=True)
else:
    st.write("🌱 No subjects added yet. Add a subject to start growing your knowledge forest!")
