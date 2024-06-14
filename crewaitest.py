# L3: Multi-agent Customer Support Automation
from unittest.mock import Base
import warnings
import streamlit as st
warnings.filterwarnings('ignore')
from crewai import Agent, Task, Crew, Process
### Tools
from pydantic import BaseModel, PrivateAttr
from crewai_tools import BaseTool
from myfunc.retrievers import HybridQueryProcessor
import os
import re

os.environ["OPENAI_MODEL_NAME"] = 'gpt-4o'
class HybridQueryProcessorTool(BaseTool):
    name: str = "Hybrid Query Processor"
    description: str = "A tool that processes hybrid queries for enhanced search results."

    _processor: 'HybridQueryProcessor' = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._processor = HybridQueryProcessor(**kwargs)

    def _run(self, query: str) -> str:
        return self._processor.process_query_results(query, dict=False)[0]

 
hybrid_query_tool = HybridQueryProcessorTool(namespace="embedding-za-sajt")
## Role Playing, Focus and Cooperation

support_agent = Agent(
    role="Senior Support Representative",
	goal="Be the most friendly and helpful "
        "support representative in your team",
	backstory=(
		"You work at Positive doo (https://positive.rs) and "
        " are now working on providing "
		"support to {customer}, a super important customer "
        " for your company."
		"You need to make sure that you provide the best support!"
		"Make sure to provide full complete answers, "
        " and make no assumptions."
	),
	allow_delegation=False,
	verbose=True
)

#- By not setting `allow_delegation=False`, `allow_delegation` takes its default value of being `True`.
#- This means the agent _can_ delegate its work to another agent which is better suited to do a particular task. 

support_quality_assurance_agent = Agent(
	role="Support Quality Assurance Specialist",
	goal="Get recognition for providing the "
    "best support quality assurance in your team",
	backstory=(
		"You work at Positive doo (https://positive.rs) and "
        "are now working with your team "
		"on a request from {customer} ensuring that "
        "the support representative is "
		"providing the best support possible.\n"
		"You need to make sure that the support representative "
        "is providing full"
		"complete answers, and make no assumptions."
	),
	verbose=True
)

### Possible Custom Tools
hybrid_query_tool = HybridQueryProcessorTool()
# search_tool = SerperDevTool()
# scrape_tool = ScrapeWebsiteTool()
# docs_scrape_tool = ScrapeWebsiteTool(
#     website_url="https://positive.rs/usluge/poslovni-konsalting/upravljanje-promenama/"
# )

##### Different Ways to Give Agents Tools
#- Agent Level: The Agent can use the Tool(s) on any Task it performs.
#- Task Level: The Agent will only use the Tool(s) when performing that specific Task.
#**Note**: Task Tools override the Agent Tools.

### Creating Tasks
inquiry_resolution = Task(
    description=(
        "{customer} just reached out with a super important ask:\n"
	    "{inquiry}\n\n"
        "{person} from {customer} is the one that reached out. "
		"Make sure to use everything you know "
        "to provide the best support possible."
		"You must strive to provide a complete "
        "and accurate response to the customer's inquiry."
    ),
    expected_output=(
	    "A detailed, informative response to the "
        "customer's inquiry that addresses "
        "all aspects of their question.\n"
        "The response should include references "
        "to everything you used to find the answer, "
        "including external data or solutions. "
        "Ensure the answer is complete, "
		"leaving no questions unanswered, and maintain a helpful and friendly "
		"tone throughout."
    ),
	tools=[hybrid_query_tool],
    agent=support_agent,
)

quality_assurance_review = Task(
    description=(
        "Review the response drafted by the Senior Support Representative for {customer}'s inquiry. "
        "Ensure that the answer is comprehensive, accurate, and adheres to the "
		"high-quality standards expected for customer support.\n"
        "Verify that all parts of the customer's inquiry "
        "have been addressed "
		"thoroughly, with a helpful and friendly tone.\n"
        "Check for references and sources used to "
        " find the information, "
		"ensuring the response is well-supported and "
        "leaves no questions unanswered."
    ),
    expected_output=(
        "A final, detailed, and informative response "
        "ready to be sent to the customer.\n"
        "This response should fully address the "
        "customer's inquiry, incorporating all "
		"relevant feedback and improvements.\n"
		"Don't be too formal, we are a chill and cool company "
	    "but maintain a professional and friendly tone throughout."
    ),
    tools=[hybrid_query_tool],
    agent=support_quality_assurance_agent,
)

### Creating the Crew
#### Memory
#- Setting `memory=True` when putting the crew together enables Memory.

crew = Crew(
  agents=[support_agent, support_quality_assurance_agent],
  tasks=[inquiry_resolution, quality_assurance_review],
  process=Process.sequential
)

### Running the Crew
upit = ""
inputs = {
    "customer": "DeepLearningAI",
    "person": "Andrew Ng",
    "inquiry": f"{upit}"
}

thought_process = []

# Regular expression pattern to match ANSI escape codes
ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')

# Mock logging function (replace with actual logging if available)
def log_thoughts(thought, placeholder):
    # Remove ANSI escape codes
    cleaned_thought = ansi_escape.sub('', thought)
    thought_process.append(cleaned_thought)
    # Update the placeholder with the latest thought process
    with placeholder:
        st.write(thought_process)

# Override the built-in print function to capture thought process
import builtins
original_print = builtins.print

def custom_print(*args, **kwargs):
    log_thoughts(" ".join(map(str, args)), log_placeholder)
    original_print(*args, **kwargs)

st.subheader("Positive doo support")
st.caption("Ver.14.06.2024.")
with st.form(key='my_form'):
    st.text_area("Postavite pitanje:")
    radi = st.form_submit_button('Postavi pitanje')
    if radi:
        st.caption("Positive doo Agent Thought Process:")
    log_placeholder = st.empty() # placeholder for thought process
# Start the crew and display the thought process
if radi:
    builtins.print = custom_print
    result = crew.kickoff(inputs=inputs)
    with st.sidebar:
        st.info("Konacan odgovor:") 
        st.write(result)   

# Restore the original print function after kickoff
builtins.print = original_print