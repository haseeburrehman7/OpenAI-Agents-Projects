import os
import chainlit as cl
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
from dotenv import load_dotenv, find_dotenv
from openai.types.responses import ResponseTextDeltaEvent

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
# 5️⃣ Agent – Math Quiz & Homework Generator
# -----------------------------
agent_quiz: Agent = Agent(
    name="Math Quiz & Homework Generator",
    instructions=(
        "You are a math assistant. You can generate math quizzes or help with math homework. "
        "If the user asks for a quiz, create 3 multiple-choice math questions with 4 options each and mark the correct answer. "
        "If the user asks for homework help, solve the problem step by step clearly. "
        "Topics include algebra, arithmetic, and geometry."
    ),
    model=model,
)

# -----------------------------
# 6️⃣ Greeting when chat starts
# -----------------------------
@cl.on_chat_start
async def handle_chat_start():
    if cl.user_session.get("greeted"):
        return
    cl.user_session.set("greeted", True)
    cl.user_session.set("history", [])
    await cl.Message(
        content="📐 **Welcome!** I am a Math Quiz & Homework Assistant 🤖 built by **Haseeb Ur Rehman**.\n\n"
                "You can ask me to generate math quizzes or solve math homework problems!"
    ).send()

# -----------------------------
# 7️⃣ Handling user messages
# -----------------------------
@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history")
    msg = cl.Message(content="")
    await msg.send()

    # Save user input to history
    history.append({"role": "user", "content": message.content})

    # Run the math quiz/homework agent
    result = Runner.run_streamed(
        agent_quiz,
        input=history,
        run_config=run_config,
    )

    # Stream the assistant response token by token
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            await msg.stream_token(event.data.delta)

    # Save assistant output to history
    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)
