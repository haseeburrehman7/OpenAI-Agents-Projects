# multi_agent_collaboration_ai.py
import os
import chainlit as cl
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    AsyncOpenAI,
    Runner,
    RunConfig,
)

# -----------------------------
# 1️⃣ Load Gemini API key
# -----------------------------
load_dotenv(find_dotenv())
gemini_api_key = os.getenv("GOOGLE_API_KEY")

# -----------------------------
# 2️⃣ Provider – Gemini connection
# -----------------------------
provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# -----------------------------
# 3️⃣ Model – Gemini Chat Completion
# -----------------------------
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=provider,
)

# -----------------------------
# 4️⃣ RunConfig
# -----------------------------
run_config = RunConfig(
    model=model,
    model_provider=provider,
    tracing_disabled=True
)

# -----------------------------
# 5️⃣ Output model for agents
# -----------------------------
class AgentOutput(BaseModel):
    response: str

# -----------------------------
# 6️⃣ Agents – Multi-Agent Collaboration
# -----------------------------
class ResearchAgent(Agent):
    async def run(self, query: str, **kwargs):
        # Add role-specific instruction
        prompt = f"You are a research assistant. Find factual information about:\n{query}"
        result = await Runner.run(self, prompt)
        if isinstance(result.final_output, str):
            return result.final_output
        return result.final_output.response

class SummarizerAgent(Agent):
    async def run(self, info: str, **kwargs):
        prompt = f"You are a summarizer. Condense the following information into a short summary:\n{info}"
        result = await Runner.run(self, prompt)
        if isinstance(result.final_output, str):
            return result.final_output
        return result.final_output.response

class PlannerAgent(Agent):
    async def run(self, summary: str, **kwargs):
        prompt = f"You are a planner. Create a simple actionable plan based on the following summary:\n{summary}"
        result = await Runner.run(self, prompt)
        if isinstance(result.final_output, str):
            return result.final_output
        return result.final_output.response


# Instantiate agents with the Gemini model and output_type
research_agent = ResearchAgent(name="ResearchAgent", model=model, output_type=AgentOutput)
summarizer_agent = SummarizerAgent(name="SummarizerAgent", model=model, output_type=AgentOutput)
planner_agent = PlannerAgent(name="PlannerAgent", model=model, output_type=AgentOutput)

# -----------------------------
# 7️⃣ Chainlit interface
# -----------------------------
@cl.on_chat_start
async def chat_start():
    if cl.user_session.get("greeted"):
        return
    cl.user_session.set("greeted", True)
    cl.user_session.set("history", [])
    await cl.Message(
        content="🤖 **Welcome!** I am a Multi-Agent Collaboration AI using Gemini API.\n\n"
                "Send a query, and I will research, summarize, and create a plan step-by-step."
    ).send()

@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history")

    # Save user input
    history.append({"role": "user", "content": message.content})

    # Step 1: Research
    research_out = await research_agent.run(message.content)

    # Step 2: Summarize
    summary_out = await summarizer_agent.run(research_out)

    # Step 3: Plan
    plan_out = await planner_agent.run(summary_out)

    # Combine output
    final_response = (
        f"**Research:** {research_out}\n\n"
        f"**Summary:** {summary_out}\n\n"
        f"**Plan:** {plan_out}"
    )
    await cl.Message(content=final_response).send()

    # Update session history
    cl.user_session.set("history", history)
