"""Core backend models and scheduler implementation for PawPal+."""

from dataclasses import dataclass, field
from typing import List, Optional


def _normalize_text(value: str) -> str:
    """Trim surrounding whitespace from a string."""
    return value.strip()


def _normalize_lower(value: str, fallback: str) -> str:
    """Trim a string, lowercase it, and return a fallback if empty."""
    normalized = value.strip().lower()
    return normalized if normalized else fallback


@dataclass
class Task:
    description: str
    time_minutes: int
    frequency: str = "once"
    completed: bool = False
    priority: str = "medium"
    category: str = "general"
    pet_name: Optional[str] = None

    def __post_init__(self) -> None:
        """Normalize task fields after initialization."""
        self.description = _normalize_text(self.description)
        self.time_minutes = max(0, int(self.time_minutes))
        self.frequency = _normalize_lower(self.frequency, "once")
        self.priority = _normalize_lower(self.priority, "medium")
        self.category = _normalize_lower(self.category, "general")

    @property
    def title(self) -> str:
        """Provide a compatibility alias for the task description."""
        return self.description

    @property
    def duration_minutes(self) -> int:
        """Provide a compatibility alias for the task duration."""
        return self.time_minutes

    @property
    def recurring(self) -> bool:
        """Return whether the task repeats on a schedule."""
        return self.frequency not in {"once", "one-time", "single"}

    def mark_complete(self) -> None:
        """Mark the task as complete."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark the task as incomplete."""
        self.completed = False

    def toggle_complete(self) -> None:
        """Flip the task completion state."""
        self.completed = not self.completed

    def get_summary(self) -> str:
        """Return a human-readable task summary."""
        status = "done" if self.completed else "pending"
        pet_label = f" for {self.pet_name}" if self.pet_name else ""
        return (
            f"{self.description}{pet_label} ({self.time_minutes} min, {self.frequency}, "
            f"priority: {self.priority}, {status})"
        )

    def is_high_priority(self) -> bool:
        """Return True when the task is marked high priority."""
        return self.priority == "high"


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    care_notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalize pet profile fields after initialization."""
        self.name = _normalize_text(self.name)
        self.species = _normalize_text(self.species)
        self.breed = _normalize_text(self.breed)
        self.care_notes = _normalize_text(self.care_notes)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and record the pet name on it."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from the pet's task list."""
        self.tasks.remove(task)

    def get_tasks(self) -> List[Task]:
        """Return a copy of all tasks assigned to this pet."""
        return list(self.tasks)

    def get_pending_tasks(self) -> List[Task]:
        """Return the pet's incomplete tasks."""
        return [task for task in self.tasks if not task.completed]

    def update_profile(
        self,
        name: Optional[str] = None,
        species: Optional[str] = None,
        breed: Optional[str] = None,
        care_notes: Optional[str] = None,
    ) -> None:
        """Update any provided pet profile fields."""
        if name is not None:
            self.name = _normalize_text(name)
        if species is not None:
            self.species = _normalize_text(species)
        if breed is not None:
            self.breed = _normalize_text(breed)
        if care_notes is not None:
            self.care_notes = _normalize_text(care_notes)
        for task in self.tasks:
            task.pet_name = self.name

    def get_care_needs(self) -> str:
        """Return the pet's care notes."""
        return self.care_notes


@dataclass
class Owner:
    name: str
    available_minutes: int = 0
    preferences: str = ""
    pets: List[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalize owner fields after initialization."""
        self.name = _normalize_text(self.name)
        self.available_minutes = max(0, int(self.available_minutes))
        self.preferences = _normalize_text(self.preferences)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's collection."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name from the owner's collection."""
        normalized_name = _normalize_text(pet_name)
        self.pets = [pet for pet in self.pets if pet.name != normalized_name]

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Return a pet with the matching name if one exists."""
        normalized_name = _normalize_text(pet_name)
        for pet in self.pets:
            if pet.name == normalized_name:
                return pet
        return None

    def get_all_tasks(self) -> List[Task]:
        """Flatten and return tasks from every pet."""
        all_tasks: List[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def get_pending_tasks(self) -> List[Task]:
        """Return all incomplete tasks across all pets."""
        return [task for task in self.get_all_tasks() if not task.completed]

    def update_preferences(self, preferences: str) -> None:
        """Update the owner's preferences text."""
        self.preferences = _normalize_text(preferences)

    def set_availability(self, available_minutes: int) -> None:
        """Update the owner's available time in minutes."""
        self.available_minutes = max(0, int(available_minutes))


@dataclass
class Scheduler:
    owner: Owner
    pet: Optional[Pet] = None
    tasks: List[Task] = field(default_factory=list)

    def collect_tasks(self) -> List[Task]:
        """Collect tasks from the owner, fallback pet, and local list."""
        collected_tasks = list(self.owner.get_all_tasks())

        if not collected_tasks and self.pet is not None:
            collected_tasks.extend(self.pet.get_tasks())

        if self.tasks:
            collected_tasks.extend(self.tasks)

        return collected_tasks

    def generate_schedule(self) -> List[Task]:
        """Generate the day's scheduled tasks."""
        return self.filter_tasks()

    def sort_tasks(self) -> List[Task]:
        """Sort tasks by completion, priority, frequency, and duration."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        frequency_order = {"once": 0, "daily": 1, "weekly": 2}

        tasks = self.collect_tasks()

        return sorted(
            tasks,
            key=lambda task: (
                task.completed,
                priority_order.get(task.priority, 3),
                frequency_order.get(task.frequency, 3),
                task.time_minutes,
                task.description.lower(),
                task.pet_name or "",
            ),
        )

    def filter_tasks(self) -> List[Task]:
        """Keep the highest-value tasks that fit into the owner's time."""
        remaining_minutes = self.owner.available_minutes
        planned_tasks: List[Task] = []

        for task in self.sort_tasks():
            if task.completed:
                continue

            if task.time_minutes <= remaining_minutes:
                planned_tasks.append(task)
                remaining_minutes -= task.time_minutes

        return planned_tasks

    def explain_choice(self) -> str:
        """Explain why the scheduler chose the current plan."""
        planned_tasks = self.filter_tasks()

        if not planned_tasks:
            return f"No pending tasks fit into the available time for {self.owner.name}."

        task_names = ", ".join(task.get_summary() for task in planned_tasks)
        return (
            f"Tasks were chosen for {self.owner.name} by priority, frequency, and available time: "
            f"{task_names}."
        )

    def mark_task_complete(self, task: Task) -> None:
        """Mark a task as complete through the scheduler."""
        task.mark_complete()

    def get_tasks_by_pet(self, pet_name: str) -> List[Task]:
        """Return tasks that belong to the named pet."""
        normalized_name = _normalize_text(pet_name)
        return [task for task in self.collect_tasks() if task.pet_name == normalized_name]
