from pawpal_system import Owner, Pet, Scheduler, Task


def format_schedule(owner: Owner, schedule: list[Task]) -> str:
    lines = [f"Today's Schedule for {owner.name}"]

    if not schedule:
        lines.append("No tasks fit into today's available time.")
        return "\n".join(lines)

    total_minutes = 0
    for index, task in enumerate(schedule, start=1):
        pet_name = task.pet_name or "Unknown pet"
        lines.append(
            f"{index}. {pet_name} - {task.description} "
            f"({task.time_minutes} min, {task.frequency}, priority: {task.priority})"
        )
        total_minutes += task.time_minutes

    lines.append(f"Total planned time: {total_minutes} minutes")
    return "\n".join(lines)


def main() -> None:
    owner = Owner("Jordan", available_minutes=60)

    mochi = Pet("Mochi", "cat", breed="Siamese")
    pip = Pet("Pip", "dog", breed="Beagle")

    mochi.add_task(Task("Morning feeding", 10, frequency="daily", priority="high"))
    mochi.add_task(Task("Litter box clean", 15, frequency="daily", priority="medium"))
    pip.add_task(Task("Walk", 30, frequency="daily", priority="high"))

    owner.add_pet(mochi)
    owner.add_pet(pip)

    scheduler = Scheduler(owner)
    schedule = scheduler.generate_schedule()

    print(format_schedule(owner, schedule))
    print()
    print(scheduler.explain_choice())


if __name__ == "__main__":
    main()
