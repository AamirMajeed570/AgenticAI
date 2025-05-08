from google.adk.agents import Agent

root_agent = Agent(
    name = "greeting_agent",
    model = "gemini-2.0-flash",
    description= "Greeting Agent  ",
    instruction= """
    You are helpful assistant that greets the user.
    Ask for the user name and greet with them  by name
    """
)