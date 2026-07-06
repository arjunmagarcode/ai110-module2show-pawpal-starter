from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_mark_complete_changes_status():
    task = Task("Morning feeding", 10)

    task.mark_complete()

    assert task.completed is True


def test_adding_task_to_pet_increases_task_count():
    pet = Pet("Mochi", "cat")
    starting_count = len(pet.get_tasks())

    pet.add_task(Task("Morning feeding", 10))

    assert len(pet.get_tasks()) == starting_count + 1


def test_scheduler_sorts_tasks_by_time():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "cat")
    pet.add_task(Task("Late task", 10, scheduled_time="18:30"))
    pet.add_task(Task("Early task", 10, scheduled_time="06:30"))
    pet.add_task(Task("Middle task", 10, scheduled_time="12:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)

    assert [task.description for task in scheduler.sort_by_time()] == [
        "Early task",
        "Middle task",
        "Late task",
    ]


def test_filter_tasks_by_pet_and_status():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "cat")
    pip = Pet("Pip", "dog")

    pending_mochi = Task("Brush coat", 10, scheduled_time="09:00")
    completed_mochi = Task("Morning feeding", 10, scheduled_time="07:00")
    completed_mochi.mark_complete()
    pip_task = Task("Walk", 30, scheduled_time="06:30")

    mochi.add_task(pending_mochi)
    mochi.add_task(completed_mochi)
    pip.add_task(pip_task)
    owner.add_pet(mochi)
    owner.add_pet(pip)

    scheduler = Scheduler(owner)

    filtered = scheduler.filter_tasks(pet_name="Mochi", completed=False, as_of=date.today())

    assert [task.description for task in filtered] == ["Brush coat"]


def test_recurring_task_completion_creates_follow_up_instance():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "cat")
    task = Task(
        "Morning feeding",
        10,
        scheduled_time="07:00",
        frequency="daily",
        due_date=date.today(),
    )
    pet.add_task(task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(task)

    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.completed is False


def test_detect_conflicts_reports_same_time_warning():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "cat")
    pip = Pet("Pip", "dog")

    mochi.add_task(Task("Morning feeding", 10, scheduled_time="07:15", due_date=date.today()))
    pip.add_task(Task("Medication", 5, scheduled_time="07:15", due_date=date.today()))
    owner.add_pet(mochi)
    owner.add_pet(pip)

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert warnings
    assert "Conflict on" in warnings[0]


def test_scheduler_handles_owner_with_no_tasks():
    owner = Owner("Jordan")
    scheduler = Scheduler(owner)

    assert scheduler.generate_schedule() == []
    assert scheduler.detect_conflicts() == []