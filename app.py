import streamlit as st
from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")


def initialize_session_state() -> None:
    """Create the persistent owner object the first time the app loads."""
    if "owner" not in st.session_state:
        st.session_state.owner = Owner("Jordan", available_minutes=60)

    if "selected_pet_name" not in st.session_state:
        st.session_state.selected_pet_name = ""


def get_owner() -> Owner:
    """Return the current owner stored in session state."""
    return st.session_state.owner


def get_pet_options(owner: Owner) -> list[str]:
    """Return the owner's pet names for selection widgets."""
    return [pet.name for pet in owner.pets]


def format_task_rows(tasks: list[Task]) -> list[dict[str, object]]:
    """Convert tasks into table-friendly rows."""
    rows: list[dict[str, object]] = []
    for task in tasks:
        rows.append(
            {
                "Pet": task.pet_name or "Unknown",
                "Task": task.description,
                "Date": task.due_date.isoformat(),
                "Start": task.scheduled_time,
                "Minutes": task.time_minutes,
                "Frequency": task.frequency,
                "Priority": task.priority,
                "Completed": task.completed,
            }
        )
    return rows


initialize_session_state()
owner = get_owner()

st.title("🐾 PawPal+")
st.markdown(
    """
PawPal+ helps a pet owner keep track of pets, tasks, and a daily schedule.

Use the forms below to add pets and tasks, then generate a schedule from the data stored
in your session.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

st.subheader("Owner Settings")
with st.form("owner_form", clear_on_submit=False):
    owner_name = st.text_input("Owner name", value=owner.name)
    available_minutes = st.number_input(
        "Available minutes today",
        min_value=0,
        max_value=1440,
        value=int(owner.available_minutes),
        step=5,
    )
    preferences = st.text_input("Preferences", value=owner.preferences)
    save_owner = st.form_submit_button("Save owner settings")

if save_owner:
    owner.name = owner_name.strip() or owner.name
    owner.set_availability(int(available_minutes))
    owner.update_preferences(preferences)
    st.success("Owner settings saved.")

st.divider()

st.subheader("Add a Pet")
with st.form("pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    breed = st.text_input("Breed", value="")
    care_notes = st.text_area("Care notes", value="")
    add_pet = st.form_submit_button("Add pet")

if add_pet:
    clean_pet_name = pet_name.strip()
    if not clean_pet_name:
        st.error("Please enter a pet name.")
    elif owner.get_pet(clean_pet_name) is not None:
        st.warning(f"{clean_pet_name} is already in your pet list.")
    else:
        owner.add_pet(Pet(clean_pet_name, species, breed=breed, care_notes=care_notes))
        st.session_state.selected_pet_name = clean_pet_name
        st.success(f"Added {clean_pet_name}.")

pet_options = get_pet_options(owner)

if pet_options:
    st.subheader("Add a Task")
    default_pet_index = 0
    if st.session_state.selected_pet_name in pet_options:
        default_pet_index = pet_options.index(st.session_state.selected_pet_name)

    with st.form("task_form", clear_on_submit=True):
        selected_pet_name = st.selectbox(
            "Choose a pet",
            pet_options,
            index=default_pet_index,
        )
        task_description = st.text_input("Task description", value="Morning feeding")
        task_date = st.date_input("Due date", value=date.today())
        task_time = st.time_input("Start time", value=time(9, 0))
        task_minutes = st.number_input(
            "Duration (minutes)",
            min_value=1,
            max_value=240,
            value=15,
            step=5,
        )
        task_frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=1)
        task_priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        task_category = st.text_input("Category", value="general")
        add_task = st.form_submit_button("Add task")

    if add_task:
        selected_pet = owner.get_pet(selected_pet_name)
        if selected_pet is None:
            st.error("Please choose a valid pet before adding a task.")
        else:
            selected_pet.add_task(
                Task(
                    task_description,
                    int(task_minutes),
                    scheduled_time=task_time.strftime("%H:%M"),
                    frequency=task_frequency,
                    due_date=task_date,
                    priority=task_priority,
                    category=task_category,
                )
            )
            st.session_state.selected_pet_name = selected_pet_name
            st.success(f"Added task to {selected_pet_name}.")
else:
    st.info("Add a pet first to start assigning tasks.")

st.divider()

st.subheader("Current Pets")
if owner.pets:
    for pet in owner.pets:
        with st.expander(f"{pet.name} ({pet.species})", expanded=False):
            if pet.breed:
                st.caption(f"Breed: {pet.breed}")
            if pet.care_notes:
                st.write(pet.care_notes)

            pet_tasks = pet.get_tasks()
            if pet_tasks:
                st.table(format_task_rows(pet_tasks))
            else:
                st.info("No tasks assigned yet.")
else:
    st.info("No pets added yet.")

st.divider()

st.subheader("Today's Schedule")
st.caption("The scheduler reads from the owner's pets stored in session state.")

scheduler = Scheduler(owner)

selected_date = st.date_input("Schedule date", value=date.today())
filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    pet_filter_options = ["All pets", *pet_options] if pet_options else ["All pets"]
    selected_pet_filter = st.selectbox("Filter by pet", pet_filter_options)
with filter_col2:
    selected_status_filter = st.selectbox("Filter by status", ["pending", "completed", "all"])

completed_filter = None
if selected_status_filter == "pending":
    completed_filter = False
elif selected_status_filter == "completed":
    completed_filter = True

pet_filter = None if selected_pet_filter == "All pets" else selected_pet_filter

schedule = scheduler.filter_tasks(
    pet_name=pet_filter,
    completed=completed_filter,
    as_of=selected_date,
)

conflicts = scheduler.detect_conflicts(schedule)
if conflicts:
    st.warning("Task conflicts detected for this view:")
    for warning in conflicts:
        st.warning(warning)
else:
    st.success("No time conflicts found for the selected schedule view.")

if schedule:
    st.table(format_task_rows(schedule))
    st.write(scheduler.explain_choice(as_of=selected_date))
else:
    st.info("No tasks match this date/filter combination yet. Add pets and tasks above.")
