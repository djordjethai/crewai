import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI


os.environ["OPENAI_MODEL_NAME"] ='gpt-4-turbo-preview'  # Adjust based on available model
search_tool = SerperDevTool()

# Define your agents with roles and goals
researcher = Agent(
  role='Senior Research Analyst',
  goal='Uncover cutting-edge developments in Digital transformation, especially in the Serbian market',
  backstory="""You work at a leading tech think tank.
  Your expertise lies in identifying emerging trends.
  You have a knack for dissecting complex data and presenting actionable insights.""",
  verbose=True,
  allow_delegation=False,
  tools=[search_tool]

)

writer = Agent(
  role='Tech Content Strategist',
  goal='Craft compelling content on Digital Transformation advancements',
  backstory="""You are a renowned Content Strategist, known for your insightful and engaging articles.
  You transform complex concepts into compelling narratives.""",
  verbose=True,
  allow_delegation=True
)

# Create tasks for your agents
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
  expected_output="Full blog post of at least 4 paragraphs",
  agent=writer
)

# Creating a crew with a hierarchical process
crew = Crew(
    agents=[researcher, writer],
    tasks=[task1, task2],
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


