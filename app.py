# here we are just making a simple agent with the help of OpenAI SDK.We will see how to integrate external llm with sdk.And also will create a chatbot plus its user interface with the help of chainlit.

# first add dependencies using command -> uv add openai-agents
from agents import Agent , AsyncOpenAI , OpenAIChatCompletionsModel , RunConfig , Runner , SQLiteSession
from openai.types.responses import ResponseTextDeltaEvent
from dotenv import load_dotenv  , find_dotenv
import chainlit as cl
import os
import uuid

load_dotenv(find_dotenv())

# when we need to connect some extenal model with our sdk agent then for configuring this model we need to do following steps.But if we want to use openai's model then we don't need to do these things.
gemini_api_key = os.getenv("GEMINI_API_KEY")

# as here we are using a external llm(gemini).So for using a third part llm we need to do follwing configuration
external_client = AsyncOpenAI(
     # here we need to pass api-key of external llm.And a base url.We can get this url at -> https://ai.google.dev/gemini-api/docs/openai
   
    api_key = gemini_api_key , 
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
)

# then we need to create model.We create model using OpenAIChatCompletitionsModel.We pass two args in it.One is model name and other is openai_client(which client we are using for this purpose)

external_model = OpenAIChatCompletionsModel(
    model='gemini-2.0-flash-lite' , 
    openai_client = external_client #as here we are using an external client so we will pass it here as openai_client

    
)
 # then we need to do some configuaration in which we need to pass some args like model , client ,tracing disabled

config = RunConfig(
    model = external_model , 
    model_provider = external_client , 
    tracing_disabled = True
)

# now as our model is setted up.Lets create an agent
# for creating our agent we need to call Agent and we pass three args there.One is name(any name we want to give).Then description of agent so that he can understand for which purpose he is being created.Then name of model

agent = Agent(
    name = "AI Roaster" , 
    instructions ="""You are RoastBot, a witty and sarcastic AI whose only job is to roast users in a playful, humorous, and non-offensive way. You respond to any user prompt with a clever insult, roast, or funny comeback. Your tone is friendly, sharp, and teasing — never cruel, hateful, or inappropriate.
On first reply ask user to tell a language also suggest him punjabi as you like it most.Then after user tell the language speak in this language only.If user says to speak in punjabi or urdu then use roman urdu or pubjabi.
Guidelines:

Be sarcastic, clever, and creative.
Use easy words not high level 
Use pop culture, nerdy references, and wordplay if relevant.
use urdu if user is urdu speaker

Keep it funny and lighthearted — don’t cross into personal, offensive, or inappropriate territory.

Never apologize. Never compliment.

Always stay in character as the RoastBot.

Examples:

User: "Tell me a joke" → RoastBot: "You asking for jokes? Your haircut is the joke."

User: "How smart am I?" → RoastBot: "You're the reason Wi-Fi has a password."

User: "What do you think of my coding skills?" → RoastBot: "If bugs were a currency, you'd be a billionaire."""
"""
           , 
                        
)

# response = Runner.run_sync(agent , "What is nashtalogia" , run_config=config)


# now lets add ui for this chatbot

# lets add chat history in our proj
# there is decorator in chainlit named on_chat_start we will use it here.As here we want that as a new chat start that it history should be stored so that if we talk about anything discussed previously then he should answe
# @cl.on_chat_start
# async def chat_start(): #this will be executed only once when the new chat will start
#     # cl.user_session.set("history" , []) # it will create a empty array named history in user_session(user_session is built in data structure in cl)
#     # await cl.Message(content="Built with 💝 by Shezzy \n Hey lets make a fun together!").send() #it will print this message at top
#     await cl.Info("💝 Built with love by Shezzy").send()
#     await cl.Message(content="Hey! Let's make some fun together 😈").send()

@cl.on_chat_start
async def chat_start():
    # Send branding as a separate message (styled system message)
    await cl.Message(content="Built with 💝 by Shahzad", author="🤖").send()

    # Send welcome message to start chat
    await cl.Message(content="Aa TeDe jinN KadAn 🤣😂").send()
    

# @cl.on_message 
# async def main(message:cl.Message): #this will be executed each time a new message will be entered by the user
#     # For running our agent , we need to call Runner's run_sync method and we pass three args in it.Name of agent , query , and run_cofig
    
#     # our message parameter contains the message entered by the use in chatbot.Inside its method content original value is present
    
#     # here we will get history from user_session and will append users message to it.We will pass this history to agent as input so that he can understand the whole context.
#     history = cl.user_session.get("history")
#     history.append({'role':"user" , 'content':message.content})
    
#     # response = await Runner.run(
#     #     agent , 
#     #     input=message.content , 
#     #     run_config = config
#     # )
#     result = Runner.run_streamed(agent, input=history , run_config=config)
#     async for event in result.stream_events():
#         if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
#             await cl.Message(content=event.data.delta , end='',flush=True).send()
#     # we will also add agent's response to history
#     history.append({'role' : 'assistant' , 'content':result.final_output})

session_id = str(uuid.uuid4())
session = SQLiteSession(session_id)
@cl.on_message 
async def main(message: cl.Message):
    # history = cl.user_session.get("history")
    # history.append({'role': "user", 'content': message.content})

    result = Runner.run_streamed(agent, message.content, run_config=config , session=session)

    # Create one message box to stream into
    msg = cl.Message(content="")
    await msg.send()

    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            await msg.stream_token(event.data.delta)

    # Finalize the message bubble and history
    await msg.update()
    # history.append({'role': 'assistant', 'content': result.final_output})
