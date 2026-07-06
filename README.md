# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

- Time-first scheduling: tasks are sorted chronologically by `scheduled_time`, then stabilized by due date and pet.
- Smart filtering: schedules can be filtered by pet, completion status, and due date cutoff.
- Conflict warnings: the scheduler flags tasks that share the same date and start time.
- Recurring rollover: completing daily/weekly tasks automatically queues the next instance.
- Streamlit integration: owner/pet/task data persists in `st.session_state` while users interact with forms.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output from running `python main.py`:

```
Today's Schedule (sorted by time)
1. Pip - Walk @ 06:30 (30 min, due 2026-07-05, daily, priority: high, pending)
2. Mochi - Morning feeding @ 07:15 (10 min, due 2026-07-05, daily, priority: high, pending)
3. Pip - Medication @ 07:15 (5 min, due 2026-07-05, daily, priority: high, pending)
4. Mochi - Brush coat @ 18:30 (15 min, due 2026-07-05, weekly, priority: medium, pending)
Total planned time: 60 minutes

Mochi's pending tasks
1. Mochi - Morning feeding @ 07:15 (10 min, due 2026-07-05, daily, priority: high, pending)
2. Mochi - Brush coat @ 18:30 (15 min, due 2026-07-05, weekly, priority: medium, pending)
Total planned time: 25 minutes

Conflict check
- Conflict on 2026-07-05 at 07:15 for Mochi, Pip: Morning feeding, Medication

Recurring task rollover
Completed: Mochi - Morning feeding @ 07:15 (10 min, due 2026-07-05, daily, priority: high, done)
Queued next instance: Mochi - Morning feeding @ 07:15 (10 min, due 2026-07-06, daily, priority: high, pending)

All tasks after rollover
1. Pip - Walk @ 06:30 (30 min, due 2026-07-05, daily, priority: high, pending)
2. Mochi - Morning feeding @ 07:15 (10 min, due 2026-07-05, daily, priority: high, done)
3. Pip - Medication @ 07:15 (5 min, due 2026-07-05, daily, priority: high, pending)
4. Mochi - Morning feeding @ 07:15 (10 min, due 2026-07-06, daily, priority: high, pending)
5. Mochi - Brush coat @ 18:30 (15 min, due 2026-07-05, weekly, priority: medium, pending)
Total planned time: 70 minutes

Tasks were chosen for Jordan by time, due date, and filters: Walk for Pip on 2026-07-05 at 06:30 (30 min, daily, priority: high, pending), Medication for Pip on 2026-07-05 at 07:15 (5 min, daily, priority: high, pending), Brush coat for Mochi on 2026-07-05 at 18:30 (15 min, weekly, priority: medium, pending).
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

The automated tests cover task completion, pet task addition, time sorting, filtering,
recurring task rollover, conflict detection, and the empty-owner edge case.

Confidence Level: ⭐⭐⭐⭐☆

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/w10182531/Desktop/ai110-module2show-pawpal-starter
collected 7 items

tests/test_pawpal.py .......                                             [100%]

============================== 7 passed in 0.02s ===============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks by `scheduled_time`, then due date and pet name. |
| Filtering | `Scheduler.filter_tasks()`, `Scheduler.get_tasks_by_pet()`, `Scheduler.get_tasks_by_status()` | Filters by pet name, completion status, and due date. |
| Conflict handling | `Scheduler.detect_conflicts()` | Warns when two tasks share the same date and start time. |
| Recurring tasks | `Scheduler.mark_task_complete()`, `Task.create_follow_up_instance()` | Automatically queues the next daily or weekly instance. |

## 📸 Demo Walkthrough

1. Open the app and set owner preferences in **Owner Settings** (name + available minutes).
2. Add one or more pets in **Add a Pet** and confirm each appears under **Current Pets**.
3. Add tasks with date/time, duration, frequency, and priority in **Add a Task**.
4. Use **Today's Schedule** controls to filter by date, pet, and status, and view the sorted schedule table.
5. Review scheduler output:
	- Time-sorted rows in the schedule table
	- Conflict warnings via Streamlit `st.warning` when two tasks share the same date/time
	- Natural-language explanation text from `Scheduler.explain_choice()`

CLI demo output (`python main.py`):

```text
Today's Schedule (sorted by time)
1. Pip - Walk @ 06:30 (30 min, due 2026-07-05, daily, priority: high, pending)
2. Mochi - Morning feeding @ 07:15 (10 min, due 2026-07-05, daily, priority: high, pending)
3. Pip - Medication @ 07:15 (5 min, due 2026-07-05, daily, priority: high, pending)
4. Mochi - Brush coat @ 18:30 (15 min, due 2026-07-05, weekly, priority: medium, pending)
Total planned time: 60 minutes
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
