import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# Set environment variables
# os.environ["SERPER_API_KEY"] = "Your_Serper_API_Key"
# os.environ["OPENAI_API_KEY"] = "Your_OpenAI_API_Key"

# Initialize Streamlit application
st.title('CrewAI Agent Thought Process')

# Create SerperDevTool
search_tool = SerperDevTool()

# Define agents
researcher = Agent(
    role='Senior Researcher',
    goal='Uncover groundbreaking technologies in {topic}',
    verbose=True,
    memory=True,
    backstory=(
        "Driven by curiosity, you're at the forefront of innovation, eager to explore and share knowledge that could change the world."
    ),
    tools=[search_tool],
    allow_delegation=True
)

writer = Agent(
    role='Writer',
    goal='Narrate compelling tech stories about {topic}',
    verbose=True,
    memory=True,
    backstory=(
        "With a flair for simplifying complex topics, you craft engaging narratives that captivate and educate, bringing new discoveries to light in an accessible manner."
    ),
    tools=[search_tool],
    allow_delegation=False
)

# Define tasks
research_task = Task(
    description=(
        "Identify the next big trend in {topic}. "
        "Focus on identifying pros and cons and the overall narrative. "
        "Your final report should clearly articulate the key points, market opportunities, and potential risks."
    ),
    expected_output='A comprehensive 3 paragraphs long report on the latest AI trends.',
    tools=[search_tool],
    agent=researcher,
)

write_task = Task(
    description=(
        "Compose an insightful article on {topic}. "
        "Focus on the latest trends and how it s impacting the industry. "
        "This article should be easy to understand, engaging, and positive."
    ),
    expected_output='A 4 paragraph article on {topic} advancements formatted as markdown.',
    tools=[search_tool],
    agent=writer,
    async_execution=False,
    output_file='new-blog-post.md'
)

# Form the crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential
)

# Capture the thought process
thought_process = []

# Mock logging function (replace with actual logging if available)
def log_thoughts(thought):
    thought_process.append(thought)
    st.text_area("Agent Thought Process", "\n".join(thought_process), height=300)

# Override the built-in print function to capture thought process
import builtins
original_print = builtins.print

def custom_print(*args, **kwargs):
    log_thoughts(" ".join(map(str, args)))
    original_print(*args, **kwargs)

builtins.print = custom_print

# Start the crew and display the thought process
if st.button('Start Crew'):
    crew.kickoff(inputs={'topic': 'AI in healthcare'})

# Restore the original print function after kickoff
builtins.print = original_print
