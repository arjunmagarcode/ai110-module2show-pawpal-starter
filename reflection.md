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
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
-> The scheduler only flags conflicts when two tasks share the exact same date and start time. It does not yet detect overlapping durations, which keeps the logic lightweight and easy to explain while still catching obvious schedule collisions for a first version.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
