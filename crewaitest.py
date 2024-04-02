import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI
from langchain.agents import load_tools


os.environ["OPENAI_MODEL_NAME"] ='gpt-4-turbo-preview'  # Adjust based on available model
search_tool = SerperDevTool()
human_tools = load_tools(["human"])
# Define your agents with roles and goals

import json  # Import the JSON module to parse JSON strings
from langchain_core.agents import AgentFinish

agent_finishes  = []

import json
from typing import Union, List, Tuple, Dict
from langchain.schema import AgentFinish


call_number = 0

def print_agent_output(agent_output: Union[str, List[Tuple[Dict, str]], AgentFinish], agent_name: str = 'Generic call'):
    global call_number  # Declare call_number as a global variable
    call_number += 1
    with open("crew_callback_logs.txt", "a", encoding = "utf-8") as log_file:
        # Try to parse the output if it is a JSON string
        if isinstance(agent_output, str):
            try:
                agent_output = json.loads(agent_output)  # Attempt to parse the JSON string
            except json.JSONDecodeError:
                pass  # If there's an error, leave agent_output as is

        # Check if the output is a list of tuples as in the first case
        if isinstance(agent_output, list) and all(isinstance(item, tuple) for item in agent_output):
            print(f"-{call_number}----Dict------------------------------------------", file=log_file)
            for action, description in agent_output:
                # Print attributes based on assumed structure
                print(f"Agent Name: {agent_name}", file=log_file)
                print(f"Tool used: {getattr(action, 'tool', 'Unknown')}", file=log_file)
                print(f"Tool input: {getattr(action, 'tool_input', 'Unknown')}", file=log_file)
                print(f"Action log: {getattr(action, 'log', 'Unknown')}", file=log_file)
                print(f"Description: {description}", file=log_file)
                print("--------------------------------------------------", file=log_file)

        # Check if the output is a dictionary as in the second case
        elif isinstance(agent_output, AgentFinish):
            print(f"-{call_number}----AgentFinish---------------------------------------", file=log_file)
            print(f"Agent Name: {agent_name}", file=log_file)
            agent_finishes.append(agent_output)
            # Extracting 'output' and 'log' from the nested 'return_values' if they exist
            output = agent_output.return_values
            # log = agent_output.get('log', 'No log available')
            print(f"AgentFinish Output: {output['output']}", file=log_file)
            # print(f"Log: {log}", file=log_file)
            # print(f"AgentFinish: {agent_output}", file=log_file)
            print("--------------------------------------------------", file=log_file)

        # Handle unexpected formats
        else:
            # If the format is unknown, print out the input directly
            print(f"-{call_number}-Unknown format of agent_output:", file=log_file)
            print(type(agent_output), file=log_file)
            print(agent_output, file=log_file)





topic_getter = Agent(
    role='A Senior customer communicator',
    goal='consult with the human customer to get the topic and areas of interest for doing the research',
    backstory="""As a top customer communicator at a renowned technology you have honed your skills
    in consulting with a customer to understand their needs and goals for what research is needed.""",
    verbose=True,
    allow_delegation=False,
    step_callback=lambda x: print_agent_output(x,"Senior Customer Agent"),
    max_iter=5,
    memory=True,
    tools= human_tools, # Passing human tools to the agent,
)

researcher = Agent(
  role='Senior Research Analyst',
  goal='Uncover cutting-edge developments in Digital transformation, especially in the Serbian market',
  backstory="""You work at a leading tech think tank.
  Your expertise lies in identifying emerging trends.
  You have a knack for dissecting complex data and presenting actionable insights. You have the ability to take a topic suggested by a human and
    rewrite multiple searches for that topic to get the best results overall.""",
  verbose=True,
  allow_delegation=False,
  step_callback=lambda x: print_agent_output(x,"Senior Research Analyst Agent"),
  memory = True,
  tools=[search_tool]

)

writer = Agent(
  role='Tech Content Strategist',
  goal='Craft compelling content on Digital Transformation advancements',
  backstory="""You are a renowned Content Strategist, known for your insightful and engaging articles.
  You transform complex concepts into compelling narratives.""",
  verbose=True,
  memory=True,
  step_callback=lambda x: print_agent_output(x,"Content Writer Agent"),
  allow_delegation=True
)

# Create tasks for your agents

get_human_topic = Task(
  description=f"""ASK THE HUMAN for the topic and area of interest.

  Compile you results into a clear topic that can be used for doing research going forward""",
  expected_output="""Clearly state the topic that the human wants you to research.\n\n
   eg. HUMAN_TOPIC_FOR_RESEARCH = 'AI_TOPIC' """,
  agent=topic_getter
)

task1 = Task(
  description="""Conduct a comprehensive analysis of the latest advancements in Digital transformation, especially in the Serbian market.
  Identify key trends, breakthrough technologies, and potential industry impacts.""",
  expected_output="Full analysis report in bullet points",
  agent=researcher
)

task2 = Task(
  description="""Using the insights provided, develop an engaging blog
  post that highlights the most significant advancements in Digital transformation, especially in the Serbian market.
  Your post should be informative yet accessible, catering to a tech-savvy audience.
  Make it sound cool, avoid complex words so it doesn't sound like AI. Write only in the Serbian Language""",
  expected_output="Full blog post of at least 4 paragraphs in markdown format",
  agent=writer
)



# Creating a crew with a hierarchical process
crew = Crew(
    agents=[topic_getter, researcher, writer],
    tasks=[get_human_topic, task1, task2],
    verbose=2, # You can set it to 1 or 2 to different logging levels
    process=Process.hierarchical,
    manager_llm=ChatOpenAI(model="gpt-4-turbo-preview")
)

# Get your crew to work!
result = crew.kickoff()


print("######################")
print(result)
with open('crewaitest.txt', 'w', encoding='utf-8') as file:
     file.write(result)


