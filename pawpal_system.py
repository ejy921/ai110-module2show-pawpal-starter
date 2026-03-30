from dataclasses import dataclass, field

@dataclass
class Owner:
    name: str
    available_time: int  # minutes per day
    preferences: list[str] = field(default_factory=list)

    def set_availability(self, minutes: int):
        pass

    def get_availability(self) -> int:
        pass

    def add_preference(self, preference: str):
        pass

    def get_preferences(self) -> list[str]:
        pass


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    special_needs: list[str] = field(default_factory=list)

    def get_info(self) -> str:
        pass

    def add_special_need(self, need: str):
        pass

    def get_special_needs(self) -> list[str]:
        pass


@dataclass
class Task:
    name: str
    category: str  # walk, feeding, grooming, meds, enrichment
    duration: int  # minutes
    priority: str  # high, medium, low
    frequency: str = "daily"  # daily, weekly, etc.
    completed: bool = False

    def edit_task(self, **kwargs):
        pass

    def get_task(self) -> dict:
        pass

    def mark_complete(self):
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task] = None):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks or []
        self.total_time_budget = owner.available_time

    def add_task(self, task: Task):
        pass

    def generate_plan(self) -> list[Task]:
        pass

    def get_plan_summary(self) -> str:
        pass

    def explain_plan(self) -> str:
        pass
