from dataclasses import Field
from operator import itemgetter
from typing import Annotated

from chainlit.types import ThreadDict
import chainlit as cl
from pydantic import TypeAdapter
from pydantic_ai import Agent
from pydantic_ai.messages import Message, MessagesTypeAdapter, ModelTextResponse, UserPrompt


@cl.password_auth_callback
def auth():
    return cl.User(identifier="test")

@cl.on_chat_start
async def on_chat_start():
    # Initialize the agent with Gemini model
    agent = Agent(
        "gemini-1.5-flash",
        system_prompt="You are a helpful chatbot. Be concise and friendly in your responses.",
    )
    cl.user_session.set("agent", agent)

    # res = await cl.AskUserMessage(content="How can I help you?", timeout=30).send()
    # if res is None:
    #     await cl.Message(content="No response received. Please try again.").send()
    #     return

    # result = agent.run_sync(res["output"])
    # await cl.Message(content=result.data).send()

@cl.on_message
async def on_message(message: cl.Message):
    agent = cl.user_session.get("agent")  # type: Agent

    prompt = UserPrompt(content=message.content).content
    
    await cl.Message(content=UserPrompt(content=prompt)).send()
    async with agent.run_stream(prompt, message_history=[]) as result:
            async for text in result.stream(debounce_by=0.01):
                # text here is a `str` and the frontend wants
                # JSON encoded ModelTextResponse, so we create one
                m = ModelTextResponse(content=text, timestamp=result.timestamp())
                await cl.Message(content=m.content).send()

    # # Get previous messages to maintain context
    # previous_messages = []
    # if hasattr(agent, "last_run_messages") and agent.last_run_messages:
    #     previous_messages = agent.last_run_messages
    #     print("Previous messages:")
    #     print(previous_messages)
    # else:
    #     print("No previous messages")

    # # Create response message placeholder
    # result = agent.run_sync(message.content)
    # res = cl.Message(content=result.data)
    # await res.send()
