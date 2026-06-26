"""Core backend models and scheduler skeleton for PawPal+."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Owner:
    name: str
    available_minutes: int = 0
    preferences: str = ""

    def update_preferences(self, preferences: str) -> None:
        pass

    def set_availability(self, available_minutes: int) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    care_notes: str = ""

    def update_profile(self) -> None:
        pass

    def get_care_needs(self) -> str:
        pass


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    category: str = "general"
    recurring: bool = False

    def get_summary(self) -> str:
        pass

    def is_high_priority(self) -> bool:
        pass


@dataclass
class Scheduler:
    owner: Owner
    pet: Pet
    tasks: List[Task] = field(default_factory=list)

    def generate_schedule(self) -> List[Task]:
        pass

    def sort_tasks(self) -> List[Task]:
        pass

    def filter_tasks(self) -> List[Task]:
        pass

    def explain_choice(self) -> str:
        pass
