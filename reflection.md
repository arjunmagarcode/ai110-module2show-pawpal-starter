# PawPal+ Project Reflection

## 1. System Design

Actions that user should be able to perform are:
- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities


**a. Initial design**

- Briefly describe your initial UML design.
-> My initial UML design was built around four main classes: Owner, Pet, Task, and Scheduler. I kept it simple so the system would focus on the most important parts of pet care planning.

- What classes did you include, and what responsibilities did you assign to each?
-> Owner stores the user’s basic info and preferences, Pet holds the pet’s details and care notes, Task represents each care activity with its time and priority, and Scheduler puts everything together to build the daily plan.

**b. Design changes**

- Did your design change during implementation?
-> Yes

- If yes, describe at least one change and why you made it.
->My design changed a little during implementation. I kept the same four core classes, but I realized the first version was too simple for updating pet information, so I adjusted the Pet class to make it easier to edit profile details. I also saw that the scheduler would need more time-related data later if I want to handle conflicts more accurately.


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
-> The scheduler considers scheduled start time, due date, completion status, pet-based filtering, and recurrence frequency. Owner availability and preferences are stored and available for future weighting, but this version mainly optimizes chronological clarity and task-state relevance.
- How did you decide which constraints mattered most?
-> I prioritized constraints that directly impact day-to-day usability: when tasks happen, whether they are due now, and whether they are already done. These gave the clearest impact with minimal complexity.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
-> The scheduler only flags conflicts when two tasks share the exact same date and start time. It does not yet detect overlapping durations, which keeps the logic lightweight and easy to explain while still catching obvious schedule collisions for a first version.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
-> I used AI for design-to-code translation, test planning, edge-case brainstorming, and debugging when integration patches introduced malformed files. AI was most effective for quickly proposing method boundaries and then iterating with validation.
- What kinds of prompts or questions were most helpful?
-> The most useful prompts were targeted and context-aware, like: "Based on my final implementation, what UML updates are needed?" and "What edge cases matter most for recurring task schedulers with time sorting?"

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
-> I rejected a broad refactor that would have split scheduling logic across more files because it added architectural overhead for a small project. I kept the four-class structure and integrated only the methods that fit the current codebase.
- How did you evaluate or verify what the AI suggested?
-> I verified each change using `python -m pytest`, `python main.py`, and targeted file reads to confirm the behavior matched requirements (sorting, filtering, conflict warnings, and recurrence).

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
-> I tested task completion, task addition, chronological sorting, filtering by pet/status, recurring task rollover, conflict detection, and the empty-owner edge case.
- Why were these tests important?
-> These tests cover both happy paths and failure-prone boundaries, ensuring the core scheduler behavior is trustworthy for daily use.

**b. Confidence**

- How confident are you that your scheduler works correctly?
-> I am at about 4/5 confidence because all automated tests pass and CLI/UI behavior matches expected outcomes.
- What edge cases would you test next if you had more time?
-> I would test overlapping-duration conflicts (not just exact start-time conflicts), timezone/date-boundary behavior, and very large task lists for performance stability.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
-> I am most satisfied with turning the scheduler into a coherent system where backend intelligence is visible in both CLI and Streamlit UI.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
-> I would add duration-overlap conflict detection, explicit owner-availability pruning in `generate_schedule`, and UI controls for marking tasks complete to trigger recurrence from the browser.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
-> The key lesson is that AI is strongest as a fast collaborator, but I still need to act as lead architect by setting boundaries, verifying outputs, and choosing simpler designs when maintainability matters.
