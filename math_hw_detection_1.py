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
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    TResponseInputItem,
    input_guardrail,
    output_guardrail,
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
async def math_input_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_input_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math_homework,
    )

# -----------------------------
# 6️⃣ Output Guardrail – Prevent Automatic Solutions
# -----------------------------
class MessageOutput(BaseModel):
    response: str

@output_guardrail
async def math_output_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    output: MessageOutput
) -> GuardrailFunctionOutput:
    # Simple rule: tripwire if response contains "solution" or "answer"
    is_solving = any(word in output.response.lower() for word in ["solution", "answer", "solve"])
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=is_solving,
    )

# -----------------------------
# 7️⃣ Main Agent – Homework Detection + Output Guardrail
# -----------------------------
agent_homework: Agent = Agent(
    name="Math Homework Detector",
    instructions="Detect if the user is asking for math homework help. If not, answer normally.",
    model=model,
    input_guardrails=[math_input_guardrail],
    output_guardrails=[math_output_guardrail],
    output_type=MessageOutput,
)

# -----------------------------
# 8️⃣ Greeting
# -----------------------------
@cl.on_chat_start
async def handle_chat_start():
    if cl.user_session.get("greeted"):
        return
    cl.user_session.set("greeted", True)
    cl.user_session.set("history", [])
    await cl.Message(
        content="📐 **Welcome!** I am a Math Homework Detector 🤖 built by **Haseeb Ur Rehman**.\n\n"
                "Send me a message, and I will detect if it is a math homework question and respond safely."
    ).send()

# -----------------------------
# 9️⃣ Handling user messages
# -----------------------------
@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history")
    msg = cl.Message(content="")
    await msg.send()

    # Save user input to history
    history.append({"role": "user", "content": message.content})

    try:
        # Run the agent
        result = await Runner.run(agent_homework, message.content)
        await cl.Message(content="✅ This is not detected as math homework.").send()
        await cl.Message(content=result.final_output.response).send()

    except InputGuardrailTripwireTriggered:
        await cl.Message(content="⚠️ Input guardrail triggered: Math homework detected!").send()

    except OutputGuardrailTripwireTriggered:
        await cl.Message(content="⚠️ Output guardrail triggered: Agent tried to provide solution!").send()

    # Update history
    cl.user_session.set("history", history)
