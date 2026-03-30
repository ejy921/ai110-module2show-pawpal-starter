from pawpal_system import Pet, Task


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
