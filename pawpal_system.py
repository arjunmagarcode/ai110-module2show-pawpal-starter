"""Core backend models and scheduler implementation for PawPal+."""

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional


def _normalize_text(value: str) -> str:
    """Trim surrounding whitespace from a string."""
    return value.strip()


def _normalize_lower(value: str, fallback: str) -> str:
    """Trim a string, lowercase it, and return a fallback if empty."""
    normalized = value.strip().lower()
    return normalized if normalized else fallback


def _normalize_time(value: str) -> str:
    """Normalize a HH:MM string to a zero-padded 24-hour time."""
    text = value.strip()
    if not text:
        return "09:00"

    parts = text.split(":")
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        return "09:00"

    hour = max(0, min(23, int(parts[0])))
    minute = max(0, min(59, int(parts[1])))
    return f"{hour:02d}:{minute:02d}"


def _time_to_minutes(value: str) -> int:
    """Convert a HH:MM string into total minutes since midnight."""
    hour, minute = value.split(":")
    return int(hour) * 60 + int(minute)


def _minutes_to_time(value: int) -> str:
    """Convert total minutes since midnight into HH:MM format."""
    hour = value // 60
    minute = value % 60
    return f"{hour:02d}:{minute:02d}"


def _advance_due_date(current_due_date: date, frequency: str) -> date:
    """Return the next due date for a recurring task."""
    if frequency == "daily":
        return current_due_date + timedelta(days=1)
    if frequency == "weekly":
        return current_due_date + timedelta(days=7)
    return current_due_date


@dataclass
class Task:
    description: str
    time_minutes: int
    scheduled_time: str = "09:00"
    frequency: str = "once"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    priority: str = "medium"
    category: str = "general"
    pet_name: Optional[str] = None

    def __post_init__(self) -> None:
        """Normalize task fields after initialization."""
        self.description = _normalize_text(self.description)
        self.time_minutes = max(0, int(self.time_minutes))
        self.scheduled_time = _normalize_time(self.scheduled_time)
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
        return self.frequency in {"daily", "weekly"}

    def next_occurrence_date(self) -> date:
        """Return the next due date for a recurring task."""
        return _advance_due_date(self.due_date, self.frequency)

    def create_follow_up_instance(self) -> Optional["Task"]:
        """Create the next recurring instance for this task."""
        if not self.recurring:
            return None

        return Task(
            description=self.description,
            time_minutes=self.time_minutes,
            scheduled_time=self.scheduled_time,
            frequency=self.frequency,
            due_date=self.next_occurrence_date(),
            completed=False,
            priority=self.priority,
            category=self.category,
            pet_name=self.pet_name,
        )

    def to_dict(self) -> dict:
        """Serialize the task into a JSON-safe dictionary."""
        return {
            "description": self.description,
            "time_minutes": self.time_minutes,
            "scheduled_time": self.scheduled_time,
            "frequency": self.frequency,
            "due_date": self.due_date.isoformat(),
            "completed": self.completed,
            "priority": self.priority,
            "category": self.category,
            "pet_name": self.pet_name,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "Task":
        """Create a task from a JSON dictionary payload."""
        due_date_text = payload.get("due_date") or date.today().isoformat()
        return cls(
            description=payload.get("description", ""),
            time_minutes=int(payload.get("time_minutes", 0)),
            scheduled_time=payload.get("scheduled_time", "09:00"),
            frequency=payload.get("frequency", "once"),
            due_date=date.fromisoformat(due_date_text),
            completed=bool(payload.get("completed", False)),
            priority=payload.get("priority", "medium"),
            category=payload.get("category", "general"),
            pet_name=payload.get("pet_name"),
        )

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
            f"{self.description}{pet_label} on {self.due_date.isoformat()} at {self.scheduled_time} "
            f"({self.time_minutes} min, {self.frequency}, priority: {self.priority}, {status})"
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

    def to_dict(self) -> dict:
        """Serialize the pet and its tasks into a JSON-safe dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "care_notes": self.care_notes,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "Pet":
        """Create a pet object from a JSON dictionary payload."""
        pet = cls(
            name=payload.get("name", ""),
            species=payload.get("species", "other"),
            breed=payload.get("breed", ""),
            care_notes=payload.get("care_notes", ""),
        )

        for task_payload in payload.get("tasks", []):
            pet.add_task(Task.from_dict(task_payload))

        return pet

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

    def to_dict(self) -> dict:
        """Serialize the owner and all pets into a JSON-safe dictionary."""
        return {
            "name": self.name,
            "available_minutes": self.available_minutes,
            "preferences": self.preferences,
            "pets": [pet.to_dict() for pet in self.pets],
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "Owner":
        """Create an owner object from a JSON dictionary payload."""
        owner = cls(
            name=payload.get("name", "Jordan"),
            available_minutes=int(payload.get("available_minutes", 0)),
            preferences=payload.get("preferences", ""),
        )
        for pet_payload in payload.get("pets", []):
            owner.add_pet(Pet.from_dict(pet_payload))
        return owner

    def save_to_json(self, file_path: str = "data.json") -> None:
        """Persist owner, pets, and tasks to a JSON file."""
        target_path = Path(file_path)
        target_path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load_from_json(
        cls,
        file_path: str = "data.json",
        default_owner_name: str = "Jordan",
    ) -> "Owner":
        """Load owner, pets, and tasks from a JSON file when available."""
        target_path = Path(file_path)
        if not target_path.exists():
            return cls(default_owner_name)

        payload = json.loads(target_path.read_text(encoding="utf-8"))
        return cls.from_dict(payload)

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

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks by priority first, then by time, date, and pet."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        tasks_to_sort = self.collect_tasks() if tasks is None else list(tasks)
        return sorted(
            tasks_to_sort,
            key=lambda task: (
                priority_order.get(task.priority, 3),
                _time_to_minutes(task.scheduled_time),
                task.due_date,
                task.pet_name or "",
                task.description.lower(),
            ),
        )

    def sort_tasks(self) -> List[Task]:
        """Provide a compatibility alias for the prioritized time sorter."""
        return self.sort_by_time()

    def find_next_available_slot(
        self,
        as_of: date,
        duration_minutes: int,
        start_hour: int = 6,
        end_hour: int = 22,
        step_minutes: int = 15,
    ) -> Optional[str]:
        """Find the next available non-overlapping slot for the given date."""
        if duration_minutes <= 0:
            return None

        day_tasks = [
            task
            for task in self.collect_tasks()
            if task.due_date == as_of and not task.completed
        ]

        occupied = []
        for task in day_tasks:
            start = _time_to_minutes(task.scheduled_time)
            occupied.append((start, start + task.time_minutes))

        occupied.sort()

        candidate = start_hour * 60
        latest_start = max(candidate, end_hour * 60 - duration_minutes)

        while candidate <= latest_start:
            candidate_end = candidate + duration_minutes
            overlap = False

            for start, end in occupied:
                if candidate < end and candidate_end > start:
                    overlap = True
                    break

            if not overlap:
                return _minutes_to_time(candidate)

            candidate += step_minutes

        return None

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
        as_of: Optional[date] = None,
        tasks: Optional[List[Task]] = None,
    ) -> List[Task]:
        """Filter tasks by pet, completion status, and due date."""
        filtered_tasks = self.collect_tasks() if tasks is None else list(tasks)

        if pet_name is not None:
            normalized_pet_name = _normalize_text(pet_name)
            filtered_tasks = [
                task for task in filtered_tasks if task.pet_name == normalized_pet_name
            ]

        if completed is not None:
            filtered_tasks = [task for task in filtered_tasks if task.completed == completed]

        if as_of is not None:
            filtered_tasks = [task for task in filtered_tasks if task.due_date <= as_of]

        return self.sort_by_time(filtered_tasks)

    def generate_schedule(self, as_of: Optional[date] = None) -> List[Task]:
        """Generate the day's scheduled tasks."""
        return self.filter_tasks(completed=False, as_of=as_of)

    def explain_choice(self, as_of: Optional[date] = None) -> str:
        """Explain why the scheduler chose the current plan."""
        planned_tasks = self.generate_schedule(as_of=as_of)

        if not planned_tasks:
            return f"No pending tasks fit into the available time for {self.owner.name}."

        task_names = ", ".join(task.get_summary() for task in planned_tasks)
        return (
            f"Tasks were chosen for {self.owner.name} by priority, time, due date, and filters: "
            f"{task_names}."
        )

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Mark a task complete and queue the next recurring instance if needed."""
        task.mark_complete()

        if not task.recurring:
            return None

        pet = self.owner.get_pet(task.pet_name or "")
        if pet is None:
            return None

        next_task = task.create_follow_up_instance()
        if next_task is None:
            return None

        pet.add_task(next_task)
        return next_task

    def get_tasks_by_pet(self, pet_name: str) -> List[Task]:
        """Return tasks that belong to the named pet."""
        return self.filter_tasks(pet_name=pet_name)

    def get_tasks_by_status(self, completed: bool) -> List[Task]:
        """Return tasks by completion state."""
        return self.filter_tasks(completed=completed)

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """Return warnings for tasks that share the same date and time."""
        tasks_to_check = self.collect_tasks() if tasks is None else list(tasks)
        grouped_tasks = defaultdict(list)

        for task in tasks_to_check:
            grouped_tasks[(task.due_date.isoformat(), task.scheduled_time)].append(task)

        warnings: List[str] = []
        for (due_date_text, scheduled_time), conflict_tasks in grouped_tasks.items():
            if len(conflict_tasks) < 2:
                continue

            pet_names = sorted({task.pet_name or "Unknown pet" for task in conflict_tasks})
            task_names = ", ".join(task.description for task in conflict_tasks)
            warnings.append(
                f"Conflict on {due_date_text} at {scheduled_time} for {', '.join(pet_names)}: {task_names}"
            )

        return warnings

    def save_to_json(self, file_path: str = "data.json") -> None:
        """Persist scheduler owner data to disk through the owner serializer."""
        self.owner.save_to_json(file_path)

    @classmethod
    def load_from_json(cls, file_path: str = "data.json") -> "Scheduler":
        """Create a scheduler by loading owner and pet data from disk."""
        return cls(owner=Owner.load_from_json(file_path))
