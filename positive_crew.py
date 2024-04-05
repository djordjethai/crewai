import io
import json
import os
import PyPDF2
import re
import streamlit as st

from crewai import Agent, Crew, Process, Task
from crewai_tools import BaseTool
from openai import OpenAI
from typing import Union, List, Tuple, Dict

from langchain_community.document_loaders import UnstructuredFileLoader
from langchain.schema import AgentFinish

from myfunc.mojafunkcija import positive_login

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

agent_finishes  = []
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


class PositiveAnalysisTool(BaseTool):
    name: str = "Relevant info extraction tool"
    description: str = "Analyzez the provided string and extracts the requested information in a structured format (dictionary)."

    def _run(self, doc_content: str) -> str:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            temperature=0,
            messages=[
                {"role": "system", "content": self.description},
                {"role": "user", "content": st.session_state.requested_data + doc_content}
            ]
        )
        return response.choices[0].message.content
    

def main():
    if "uploaded_file_content" not in st.session_state:
        st.session_state.uploaded_file_content = None
    if "requested_data" not in st.session_state:
        st.session_state.requested_data = "Extract the following information: potrebni office paketi, cloud servisi"
    if "positive_analysis_tool" not in st.session_state:
        st.session_state.positive_analysis_tool = PositiveAnalysisTool()

    st.title("Positive AI Crew 👯")
    with st.sidebar:
        st.markdown("ver 0.1")

        ponuda = st.file_uploader(
            "Uploadujte ponudu",
            key="upload_file",
            type=["txt", "docx", "pdf"])

        if ponuda is not None:
            with io.open(ponuda.name, "wb") as file:
                file.write(ponuda.getbuffer())

            if ".pdf" in ponuda.name:
                pdf_reader = PyPDF2.PdfReader(ponuda)
                num_pages = len(pdf_reader.pages)
                text_content = ""

                for page in range(num_pages):
                    page_obj = pdf_reader.pages[page]
                    text_content += page_obj.extract_text()

                text_content = re.sub(r"(?<=\b\w) (?=\w\b)", "", text_content.replace("•", ""))
                with io.open("temp.txt", "w", encoding="utf-8-sig") as f:
                    f.write(text_content)

                loader = UnstructuredFileLoader("temp.txt", encoding="utf-8-sig")
            else:
                loader = UnstructuredFileLoader(file_path=ponuda.name, encoding="utf-8-sig")

            st.session_state.uploaded_file_content = loader.load()[0].page_content

    if st.session_state.uploaded_file_content:
        st.write(st.session_state.uploaded_file_content)

    data_extractor = Agent(
        role="Data Extraction Specialist",
        goal="Extract all the relevant data from the text",
        backstory="Your one and only job is to go through the text and extract all the relevant data from it.",
        verbose=True,
        allow_delegation=False,
        # step_callback=lambda x: print_agent_output(x, "Data Extraction Specialist"),
        max_iter=5,
        memory=True,
        tools=[st.session_state.positive_analysis_tool],
    )
    
    extract_data = Task(
        description="Analyze the provided document content and extract all relevant data about required office packages and cloud services.",
        expected_output="A dictionary containing extracted information about office packages and cloud services mentioned in the document.",
        agent=data_extractor,
    )
    
    result = Crew(
        agents=[data_extractor],
        tasks=[extract_data],
        verbose=1,
        ).kickoff()
    st.write(result)


deployment_environment = os.environ.get("DEPLOYMENT_ENVIRONMENT")

if deployment_environment == "Streamlit":
    name, authentication_status, username = positive_login(main, " ")
else:
    if __name__ == "__main__":
        main()
