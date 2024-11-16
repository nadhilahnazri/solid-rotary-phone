import pygame
import streamlit as st
from io import BytesIO
from PIL import Image

# Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
TREE_TRUNK = (139, 69, 19)
LEAF_GREEN = (50, 205, 50)
DARK_GREEN = (0, 128, 0)

# Function to draw a single tree
def draw_tree(surface, x, y, trunk_width, trunk_height, foliage_radius, subject_name):
    # Draw trunk
    trunk_rect = pygame.Rect(x, y - trunk_height, trunk_width, trunk_height)
    pygame.draw.rect(surface, TREE_TRUNK, trunk_rect)

    # Draw foliage (overlapping circles for a stylized look)
    pygame.draw.circle(surface, LEAF_GREEN, (x + trunk_width // 2, y - trunk_height), foliage_radius)
    pygame.draw.circle(surface, DARK_GREEN, (x + trunk_width // 2 - foliage_radius // 2, y - trunk_height + foliage_radius // 2), foliage_radius)
    pygame.draw.circle(surface, DARK_GREEN, (x + trunk_width // 2 + foliage_radius // 2, y - trunk_height + foliage_radius // 2), foliage_radius)

    # Add the subject name below the tree
    font = pygame.font.Font(None, 24)
    text_surface = font.render(subject_name, True, (0, 0, 0))
    surface.blit(text_surface, (x + trunk_width // 2 - text_surface.get_width() // 2, y + 10))

# Function to draw the entire forest
def draw_forest(subjects):
    pygame.init()
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surface.fill(SKY_BLUE)
    pygame.draw.rect(surface, GRASS_GREEN, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))

    # Determine tree placement
    tree_spacing = SCREEN_WIDTH // (len(subjects) + 1)
    x_positions = [tree_spacing * (i + 1) for i in range(len(subjects))]

    # Draw each tree (subject)
    for i, (subject, topics) in enumerate(subjects.items()):
        x = x_positions[i]
        y = SCREEN_HEIGHT // 2
        trunk_width = 30
        trunk_height = 50 + len(topics) * 20  # Dynamic trunk height based on number of topics
        foliage_radius = 40
        draw_tree(surface, x, y, trunk_width, trunk_height, foliage_radius, subject)

    return surface

# Convert Pygame surface to an image for Streamlit
def pygame_to_image(surface):
    img_str = pygame.image.tostring(surface, "RGB")
    img = Image.frombytes("RGB", (surface.get_width(), surface.get_height()), img_str)
    return img

# Streamlit app
st.title("🌳 Learning Tracker - Knowledge Forest 🌳")

# Initialize session state for subjects and topics
if "forest" not in st.session_state:
    st.session_state.forest = {}

# Add a new subject
new_subject = st.text_input("Add a New Subject:")
if st.button("Add Subject"):
    if new_subject and new_subject not in st.session_state.forest:
        st.session_state.forest[new_subject] = []
        st.success(f"Added subject: {new_subject}")
    elif new_subject in st.session_state.forest:
        st.warning(f"Subject '{new_subject}' already exists!")
    else:
        st.warning("Subject name cannot be empty!")

# Add topics to an existing subject
subject_choice = st.selectbox("Select a Subject to Add Topics:", [""] + list(st.session_state.forest.keys()))
if subject_choice:
    new_topic = st.text_input("Add a New Topic:")
    if st.button("Add Topic"):
        if new_topic and new_topic not in st.session_state.forest[subject_choice]:
            st.session_state.forest[subject_choice].append(new_topic)
            st.success(f"Added topic '{new_topic}' to subject '{subject_choice}'")
        elif new_topic in st.session_state.forest[subject_choice]:
            st.warning(f"Topic '{new_topic}' already exists in '{subject_choice}'!")
        else:
            st.warning("Topic name cannot be empty!")

# Display the forest
if st.session_state.forest:
    forest_surface = draw_forest(st.session_state.forest)  # Draw the forest
    forest_image = pygame_to_image(forest_surface)  # Convert to PIL image
    st.image(forest_image, caption="Knowledge Forest", use_column_width=True)
else:
    st.write("🌱 No subjects added yet. Add a subject to start growing your knowledge forest!")
