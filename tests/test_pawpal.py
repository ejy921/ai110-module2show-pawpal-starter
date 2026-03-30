from datetime import date, time, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# === Existing tests ===

def test_mark_complete():
    task = Task(name="Morning walk", category="walk", duration=25, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_count():
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(name="Breakfast", category="feeding", duration=10, priority="high"))
    assert len(pet.get_tasks()) == 1
    pet.add_task(Task(name="Brush coat", category="grooming", duration=15, priority="low"))
    assert len(pet.get_tasks()) == 2


# === Scheduling / Budget ===

def test_zero_available_time():
    owner = Owner(name="Jordan", available_time=0)
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    pet.add_task(Task(name="Walk", category="walk", duration=10, priority="high"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    assert scheduler.generate_plan() == []


def test_single_task_exceeds_budget():
    owner = Owner(name="Jordan", available_time=30)
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    pet.add_task(Task(name="Long walk", category="walk", duration=90, priority="high"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    assert scheduler.generate_plan() == []


def test_exact_fit():
    owner = Owner(name="Jordan", available_time=30)
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    pet.add_task(Task(name="Walk", category="walk", duration=20, priority="high"))
    pet.add_task(Task(name="Feed", category="feeding", duration=10, priority="high"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    total = sum(t.duration for t in plan)
    assert total == 30
    assert len(plan) == 2


def test_all_tasks_completed():
    owner = Owner(name="Jordan", available_time=60)
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    t1 = Task(name="Walk", category="walk", duration=20, priority="high", completed=True)
    t2 = Task(name="Feed", category="feeding", duration=10, priority="high", completed=True)
    pet.add_task(t1)
    pet.add_task(t2)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    assert scheduler.generate_plan() == []


# === Sorting ===

def test_tied_priority_sorts_by_duration():
    owner = Owner(name="Jordan", available_time=120)
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    pet.add_task(Task(name="Long walk", category="walk", duration=30, priority="high"))
    pet.add_task(Task(name="Quick feed", category="feeding", duration=5, priority="high"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    assert plan[0].name == "Quick feed"
    assert plan[1].name == "Long walk"


def test_sort_single_task():
    scheduler = Scheduler(Owner(name="Jordan", available_time=60))
    task = Task(name="Walk", category="walk", duration=20, priority="high")
    result = scheduler.sort_tasks([task])
    assert len(result) == 1
    assert result[0].name == "Walk"


# === Recurring Tasks ===

def test_daily_recurrence_due_date():
    task = Task(name="Walk", category="walk", duration=20, priority="high", frequency="daily")
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.completed is False


def test_weekly_recurrence_due_date():
    task = Task(name="Flea meds", category="meds", duration=5, priority="high", frequency="weekly")
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=7)


def test_unrecognized_frequency_no_recurrence():
    task = Task(name="Vet visit", category="meds", duration=60, priority="high", frequency="once")
    next_task = task.mark_complete()
    assert next_task is None


def test_complete_same_task_twice():
    owner = Owner(name="Jordan", available_time=60)
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    task = Task(name="Walk", category="walk", duration=20, priority="high", frequency="daily")
    pet.add_task(task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    next1 = scheduler.mark_task_complete(task)
    assert next1 is not None
    assert len(pet.tasks) == 2
    next2 = scheduler.mark_task_complete(next1)
    assert next2 is not None
    assert len(pet.tasks) == 3


# === Fairness ===

def test_one_pet_has_no_tasks():
    owner = Owner(name="Jordan", available_time=60)
    mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    mochi.add_task(Task(name="Walk", category="walk", duration=20, priority="high"))
    empty_pet = Pet(name="Ghost", species="cat", breed="Tabby", age=2)
    owner.add_pet(mochi)
    owner.add_pet(empty_pet)
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    assert len(plan) == 1
    assert plan[0].name == "Walk"


def test_three_pets_fairness():
    owner = Owner(name="Jordan", available_time=60)
    pets = []
    for name in ["Mochi", "Whiskers", "Bubbles"]:
        pet = Pet(name=name, species="dog", breed="Mix", age=3)
        pet.add_task(Task(name=f"{name} walk", category="walk", duration=15, priority="high"))
        pet.add_task(Task(name=f"{name} feed", category="feeding", duration=5, priority="high"))
        owner.add_pet(pet)
        pets.append(pet)
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    # Each pet should have at least one task in the plan
    pets_in_plan = set()
    for task in plan:
        for pet in pets:
            if task in pet.tasks:
                pets_in_plan.add(pet.name)
    assert pets_in_plan == {"Mochi", "Whiskers", "Bubbles"}


# === Special Needs ===

def test_duplicate_special_need():
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    pet.add_special_need("joint supplement")
    pet.add_special_need("joint supplement")
    assert len(pet.get_special_needs()) == 1


def test_generate_needs_tasks_no_duplicate():
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    pet.add_special_need("joint supplement")
    pet.add_task(Task(name="joint supplement", category="meds", duration=5, priority="high"))
    pet.generate_needs_tasks()
    matching = [t for t in pet.tasks if t.name == "joint supplement"]
    assert len(matching) == 1


# === Sorting Chronological Order ===

def test_plan_sorted_chronologically():
    owner = Owner(name="Jordan", available_time=60)
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    pet.add_task(Task(name="Grooming", category="grooming", duration=15, priority="low"))
    pet.add_task(Task(name="Walk", category="walk", duration=25, priority="high"))
    pet.add_task(Task(name="Feed", category="feeding", duration=10, priority="medium"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    # Every task should have a scheduled_time and they should be in ascending order
    times = [t.scheduled_time for t in plan]
    assert all(t is not None for t in times)
    assert times == sorted(times)
    # First task should start at 8:00 AM
    assert plan[0].scheduled_time == time(8, 0)


# === Recurrence Logic (targeted) ===

def test_daily_recurrence_creates_next_day_task():
    owner = Owner(name="Jordan", available_time=60)
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    task = Task(name="Walk", category="walk", duration=20, priority="high", frequency="daily")
    pet.add_task(task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(task)
    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.name == task.name
    assert next_task in pet.tasks


# === Conflict Detection ===

def test_no_conflicts_in_generated_plan():
    owner = Owner(name="Jordan", available_time=60)
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    pet.add_task(Task(name="Walk", category="walk", duration=20, priority="high"))
    pet.add_task(Task(name="Feed", category="feeding", duration=10, priority="high"))
    pet.add_task(Task(name="Play", category="enrichment", duration=15, priority="medium"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    assert scheduler.detect_conflicts() == []


def test_detects_manually_overlapping_tasks():
    owner = Owner(name="Jordan", available_time=60)
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    # Manually create two tasks that overlap: both start at 8:00
    task_a = Task(name="Walk", category="walk", duration=30, priority="high", scheduled_time=time(8, 0))
    task_b = Task(name="Feed", category="feeding", duration=10, priority="high", scheduled_time=time(8, 15))
    scheduler.plan = [task_a, task_b]
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert conflicts[0] == (task_a, task_b)
