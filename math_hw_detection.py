import os
import chainlit as cl
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
from agents import (
    Agent,
    RunConfig,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    Runner,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    TResponseInputItem,
    input_guardrail,
)

# -----------------------------
# 1️⃣ Load API key
# -----------------------------
load_dotenv(find_dotenv())
gemini_api_key = os.getenv("GOOGLE_API_KEY")

# -----------------------------
# 2️⃣ Provider – connection to Gemini API
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
# 4️⃣ RunConfig – run settings
# -----------------------------
run_config = RunConfig(
    model=model,
    model_provider=provider,
    tracing_disabled=True
)

# -----------------------------
# 5️⃣ Input Guardrail – Math Homework Detection
# -----------------------------
class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

guardrail_input_agent = Agent(
    name="Math Homework Guardrail Agent",
    instructions="Check if the user is asking for math homework help. Return is_math_homework True/False.",
    output_type=MathHomeworkOutput,
    model=model,
)

@input_guardrail
async def math_input_guardrail( ctx: RunContextWrapper[None], agent: Agent,input: str | list[TResponseInputItem]) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_input_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math_homework,
    )

# -----------------------------
# 6️⃣ Main Agent – Only Homework Detection
# -----------------------------
agent_homework: Agent = Agent(
    name="Math Homework Detector",
    instructions="You are an assistant that only detects if the user is asking for math homework help.",
    model=model,
    input_guardrails=[math_input_guardrail],
)

# -----------------------------
# 7️⃣ Greeting
# -----------------------------
@cl.on_chat_start
async def handle_chat_start():
    if cl.user_session.get("greeted"):
        return
    cl.user_session.set("greeted", True)
    cl.user_session.set("history", [])
    await cl.Message(
        content="📐 **Welcome!** I am a Math Homework Detector 🤖 built by **Haseeb Ur Rehman**.\n\n"
                "Send me a message, and I will detect if it is a math homework question."
    ).send()

# -----------------------------
# 8️⃣ Handling user messages
# -----------------------------
@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history")
    msg = cl.Message(content="")
    await msg.send()

    # Save user input to history
    history.append({"role": "user", "content": message.content})

    try:
         # Run agent to check homework
        await Runner.run(agent_homework, message.content)
        # If no guardrail triggered, give a normal answer
        result = await Runner.run(agent_homework, message.content)
        await cl.Message(content="✅ This is not detected as math homework.").send()
        await cl.Message(content=result.final_output).send()

    except InputGuardrailTripwireTriggered:
        await cl.Message(content="⚠️ Input guardrail triggered: Math homework detected!").send()

    # Update history
    cl.user_session.set("history", history)

        # await cl.Message(content="✅ This is not detected as math homework.").send()
