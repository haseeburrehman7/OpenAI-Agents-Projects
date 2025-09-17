# import os
# import chainlit as cl
# from pydantic import BaseModel
# from dotenv import load_dotenv, find_dotenv
# from openai.types.responses import ResponseTextDeltaEvent
# from agents import (
#     Agent,
#     RunConfig,
#     AsyncOpenAI,
#     OpenAIChatCompletionsModel,
#     Runner,
#     GuardrailFunctionOutput,
#     InputGuardrailTripwireTriggered,
#     OutputGuardrailTripwireTriggered,
#     RunContextWrapper,
#     TResponseInputItem,
#     input_guardrail,
#     output_guardrail,
# )

# # -----------------------------
# # 1️⃣ Load API key
# # -----------------------------
# load_dotenv(find_dotenv())
# gemini_api_key = os.getenv("GOOGLE_API_KEY")

# # -----------------------------
# # 2️⃣ Provider – connection to Gemini API
# # -----------------------------
# provider = AsyncOpenAI(
#     api_key=gemini_api_key,
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
# )

# # -----------------------------
# # 3️⃣ Model – Gemini Chat Completion
# # -----------------------------
# model = OpenAIChatCompletionsModel(
#     model="gemini-2.5-flash",
#     openai_client=provider,
# )

# # -----------------------------
# # 4️⃣ RunConfig – run settings
# # -----------------------------
# run_config = RunConfig(
#     model=model,
#     model_provider=provider,
#     tracing_disabled=True
# )

# # -----------------------------
# # 5️⃣ Input Guardrail – Math Homework Detection
# # -----------------------------
# class MathHomeworkOutput(BaseModel):
#     is_math_homework: bool
#     reasoning: str

# guardrail_input_agent = Agent(
#     name="Input Guardrail Agent",
#     instructions="Check if the user is asking you to do their math homework.",
#     output_type=MathHomeworkOutput,
#     model=model,
# )

# @input_guardrail
# async def math_input_guardrail(
#     ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
# ) -> GuardrailFunctionOutput:
#     result = await Runner.run(guardrail_input_agent, input, context=ctx.context)
#     return GuardrailFunctionOutput(
#         output_info=result.final_output,
#         tripwire_triggered=result.final_output.is_math_homework,
#     )

# # -----------------------------
# # 6️⃣ Output Guardrail – Math Content Detection
# # -----------------------------
# class MessageOutput(BaseModel):
#     response: str

# class MathOutput(BaseModel):
#     reasoning: str
#     is_math: bool

# guardrail_output_agent = Agent(
#     name="Output Guardrail Agent",
#     instructions="Check if the output includes any math.",
#     output_type=MathOutput,
#     model=model,
# )

# @output_guardrail
# async def math_output_guardrail(
#     ctx: RunContextWrapper, agent: Agent, output: MessageOutput
# ) -> GuardrailFunctionOutput:
#     result = await Runner.run(guardrail_output_agent, output.response, context=ctx.context)
#     return GuardrailFunctionOutput(
#         output_info=result.final_output,
#         tripwire_triggered=result.final_output.is_math,
#     )

# # -----------------------------
# # 7️⃣ Agent – Math Quiz & Homework Generator
# # -----------------------------
# agent_quiz: Agent = Agent(
#     name="Math Quiz & Homework Generator",
#     instructions=(
#         "You are a math assistant. You can generate math quizzes or help with math homework. "
#         "If the user asks for a quiz, create 3 multiple-choice math questions with 4 options each and mark the correct answer. "
#         "If the user asks for homework help, solve the problem step by step clearly. "
#         "Topics include algebra, arithmetic, and geometry."
#     ),
#     model=model,
#     input_guardrails=[math_input_guardrail],
#     output_guardrails=[math_output_guardrail],
#     output_type=MessageOutput
# )

# # -----------------------------
# # 8️⃣ Greeting and Guardrail Test
# # -----------------------------
# @cl.on_chat_start
# async def handle_chat_start():
#     if cl.user_session.get("greeted"):
#         return
#     cl.user_session.set("greeted", True)
#     cl.user_session.set("history", [])
#     await cl.Message(
#         content="📐 **Welcome!** I am a Math Quiz & Homework Assistant 🤖 built by **Haseeb Ur Rehman**.\n\n"
#                 "You can ask me to generate math quizzes or solve math homework problems!"
#     ).send()

#     # Optional: test input guardrail immediately
#     try:
#         await Runner.run(agent_quiz, "Hello, can you help me solve for x: 2x + 3 = 11?")
#         print("Guardrail didn't trip - this is unexpected")
#     except InputGuardrailTripwireTriggered:
#         print("Input guardrail tripped: Math homework detected")

# # -----------------------------
# # 9️⃣ Handling user messages
# # -----------------------------
# @cl.on_message
# async def handle_message(message: cl.Message):
#     history = cl.user_session.get("history")
#     msg = cl.Message(content="")
#     await msg.send()

#     # Save user input to history
#     history.append({"role": "user", "content": message.content})

#     try:
#         # Run the math quiz/homework agent
#         result = Runner.run_streamed(
#             agent_quiz,
#             input=history,
#             run_config=run_config,
#         )

#         # Stream the assistant response token by token
#         async for event in result.stream_events():
#             if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
#                 await msg.stream_token(event.data.delta)

#         # Save assistant output to history
#         history.append({"role": "assistant", "content": result.final_output})
#         cl.user_session.set("history", history)

#     except InputGuardrailTripwireTriggered as e:
#         await cl.Message(content=f"⚠️ Input guardrail triggered: {str(e)}").send()

#     except OutputGuardrailTripwireTriggered:
#         await cl.Message(content="⚠️ Output guardrail triggered: Math content detected!").send()

# ===============================================================================================================================================
# ===============================================================================================================================================
# ===============================================================================================================================================
# ===============================================================================================================================================


import os
import chainlit as cl
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
from openai.types.responses import ResponseTextDeltaEvent
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
    name="Input Guardrail Agent",
    instructions="Check if the user is asking you to do their math homework. Return is_math_homework True/False.",
    output_type=MathHomeworkOutput,
    model=model,
)

@input_guardrail
async def math_input_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    # Run helper agent to detect math homework
    result = await Runner.run(guardrail_input_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math_homework,
    )

# -----------------------------
# 6️⃣ Output Guardrail – Math Content Detection
# -----------------------------
class MessageOutput(BaseModel):
    response: str

class MathOutput(BaseModel):
    reasoning: str
    is_math: bool

guardrail_output_agent = Agent(
    name="Output Guardrail Agent",
    instructions="Check if the output includes any math content. Return is_math True/False.",
    output_type=MathOutput,
    model=model,
)

@output_guardrail
async def math_output_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    output: MessageOutput
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_output_agent, output.response, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math,
    )

# -----------------------------
# 7️⃣ Agent – Math Quiz & Homework Generator
# -----------------------------
agent_quiz: Agent = Agent(
    name="Math Quiz & Homework Generator",
    instructions=(
        "You are a math assistant. You can generate math quizzes or help with math homework. "
        "If the user asks for a quiz, create 3 multiple-choice math questions with 4 options each and mark the correct answer. "
        "If the user asks for homework help, solve the problem step by step clearly. "
        "Always return your answer in JSON as: {\"response\": \"your answer here\"}"
    ),
    model=model,
    input_guardrails=[math_input_guardrail],
    output_guardrails=[math_output_guardrail],
    output_type=MessageOutput
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
        content="📐 **Welcome!** I am a Math Quiz & Homework Assistant 🤖 built by **Haseeb Ur Rehman**.\n\n"
                "You can ask me to generate math quizzes or solve math homework problems!"
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
        history.append({"role": "assistant", "content": result.final_output.response})
        cl.user_session.set("history", history)

    except InputGuardrailTripwireTriggered as e:
        await cl.Message(content=f"⚠️ Input guardrail triggered: {str(e)}").send()

    except OutputGuardrailTripwireTriggered:
        await cl.Message(content="⚠️ Output guardrail triggered: Math content detected!").send()
