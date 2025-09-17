
#  AI Projects with OpenAI Agents SDK, Chainlit & Gemini API

This repository contains **three AI-powered projects** built using **OpenAI Agents SDK**, **Chainlit**, and **Gemini API**.
All projects are developed by **Haseeb Ur Rehman**.


##  Project 1: Math Quiz & Homework Assistant

* **Purpose:** Generates math quizzes or solves math homework problems.
* **Features:**

  * Creates **3 multiple-choice math quiz questions** with 4 options and correct answer.
  * Provides **step-by-step solutions** for homework problems.
  * Topics: Algebra, Arithmetic, Geometry.
* **Tech Used:** Python, Chainlit, OpenAI Agents SDK, Gemini API

---

##  Project 2: Math Homework Detector (with Guardrails)

* **Purpose:** Detects math homework queries and prevents automatic solutions.
* **Features:**

  * **Input Guardrail:** Detects if user is asking for homework help.
  * **Output Guardrail:** Prevents leaking direct solutions ("solve", "answer").
  * Provides safe, guided responses.
* **Tech Used:** Python, Pydantic, Chainlit, OpenAI Agents SDK, Gemini API

---

##  Project 3: Multi-Agent Collaboration AI

* **Purpose:** Demonstrates collaboration between multiple specialized agents.
* **Features:**

  * **Research Agent:** Finds factual information.
  * **Summarizer Agent:** Condenses research into short summary.
  * **Planner Agent:** Builds a simple actionable plan.
  * Produces **research → summary → plan** pipeline.
* **Tech Used:** Python, Chainlit, OpenAI Agents SDK, Gemini API

---

## How to Run

1. Clone this repo:

   ```bash
   git clone https://github.com/haseeburrehman7/OpenAI-Agents-Projects.git
   cd OpenAI-Agents-Projects
   ```
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env`:

   ```env
   GOOGLE_API_KEY=your_api_key
   ```
4. Run a project:

   ```bash
   chainlit run generate_quiz.py -w
   chainlit run math_hw_detection.py -w
   chainlit run multi_agent_collab.py -w
   ```

---

##  Tech Stack

* **Language:** Python
* **Framework:** Chainlit
* **AI SDK:** OpenAI Agents SDK
* **LLM Provider:** Gemini API
* **Extras:** Pydantic, Guardrails

---

## Author

**Haseeb Ur Rehman**

*  Agentic AI & Robotic Engineer
*  [LinkedIn](https://www.linkedin.com/in/haseeb-ur-rehman-bb64021b9) | [haseeburrehman7978@gmail.com](mailto:haseeburrehman7978@gmail.com)

---

