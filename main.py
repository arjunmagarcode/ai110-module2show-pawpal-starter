from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def format_task(task: Task) -> str:
    """Format a task for terminal output."""
    pet_name = task.pet_name or "Unknown pet"
    return (
        f"{pet_name} - {task.description} @ {task.scheduled_time} "
        f"({task.time_minutes} min, due {task.due_date.isoformat()}, {task.frequency}, priority: {task.priority}, "
        f"{'done' if task.completed else 'pending'})"
    )


def format_task_list(title: str, tasks: list[Task]) -> str:
    """Format a list of tasks for a readable terminal block."""
    lines = [title]

    if not tasks:
        lines.append("No tasks found.")
        return "\n".join(lines)

    total_minutes = 0
    for index, task in enumerate(tasks, start=1):
        lines.append(f"{index}. {format_task(task)}")
        total_minutes += task.time_minutes

    lines.append(f"Total planned time: {total_minutes} minutes")
    return "\n".join(lines)


def main() -> None:
    today = date.today()
    owner = Owner("Jordan", available_minutes=90)

    mochi = Pet("Mochi", "cat", breed="Siamese")
    pip = Pet("Pip", "dog", breed="Beagle")

    mochi.add_task(
        Task(
            "Brush coat",
            15,
            scheduled_time="18:30",
            frequency="weekly",
            priority="medium",
            due_date=today,
        )
    )
    mochi.add_task(
        Task(
            "Morning feeding",
            10,
            scheduled_time="07:15",
            frequency="daily",
            priority="high",
            due_date=today,
        )
    )
    pip.add_task(
        Task(
            "Walk",
            30,
            scheduled_time="06:30",
            frequency="daily",
            priority="high",
            due_date=today,
        )
    )
    pip.add_task(
        Task(
            "Medication",
            5,
            scheduled_time="07:15",
            frequency="daily",
            priority="high",
            due_date=today,
        )
    )

    owner.add_pet(mochi)
    owner.add_pet(pip)

    scheduler = Scheduler(owner)
    schedule = scheduler.generate_schedule(as_of=today)

    print(format_task_list("Today's Schedule (sorted by time)", schedule))
    print()
    print(format_task_list("Mochi's pending tasks", scheduler.filter_tasks(pet_name="Mochi", completed=False, as_of=today)))
    print()

    conflict_warnings = scheduler.detect_conflicts(schedule)
    print("Conflict check")
    if conflict_warnings:
        for warning in conflict_warnings:
            print(f"- {warning}")
    else:
        print("No conflicts found.")

    print()

    recurring_source = owner.get_pet("Mochi").get_tasks()[1]
    next_occurrence = scheduler.mark_task_complete(recurring_source)

    print("Recurring task rollover")
    print(f"Completed: {format_task(recurring_source)}")
    if next_occurrence is not None:
        print(f"Queued next instance: {format_task(next_occurrence)}")
    else:
        print("No recurring follow-up was created.")

    print()
    print(format_task_list("All tasks after rollover", scheduler.sort_by_time()))
    print()
    print(scheduler.explain_choice(as_of=today))


if __name__ == "__main__":
    main()
