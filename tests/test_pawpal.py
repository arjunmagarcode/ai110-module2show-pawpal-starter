from pawpal_system import Pet, Task


def test_task_mark_complete_changes_status():
    task = Task("Morning feeding", 10)

    task.mark_complete()

    assert task.completed is True


def test_adding_task_to_pet_increases_task_count():
    pet = Pet("Mochi", "cat")
    starting_count = len(pet.get_tasks())

    pet.add_task(Task("Morning feeding", 10))

    assert len(pet.get_tasks()) == starting_count + 1