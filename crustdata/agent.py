import warnings
import streamlit as st
from crewai import Agent, Task, Crew
import os

# Suppress warnings
warnings.filterwarnings('ignore')

# Set OpenAI model
###os.environ["OPENAI_API_KEY"] = "Your api keys"

os.environ["OPENAI_MODEL_NAME"] = "gpt-4-turbo"

# Streamlit Page Configuration
st.set_page_config(page_title="Crustdata Support Workflow", layout="centered")

st.title("Crustdata Customer Support Workflow")
st.write("This app simulates a support workflow for customer inquiries using CrewAI.")

# Initialize CrewAI Agents
support_agent = Agent(
    role="Senior Support Representative",
	goal="Be the most friendly and helpful "
        "support representative in your team",
	backstory=(
		"You work at Crustdata and "
        " are now working on providing "
		"support to {customer}, a super important customer "
        " for your company."
		"You need to make sure that you provide the best support!"
		"Make sure to provide full complete answers, and also provide with multiple code exapmle if possible "
        " and make no assumptions."
	),
	allow_delegation=False,
	verbose=True
)

support_quality_assurance_agent = Agent(
	role="Support Quality Assurance Specialist",
	goal="Get recognition for providing the "
    "best support quality assurance in your team",
	backstory=(
		"You work at Crustdata and "
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
from crewai_tools import SerperDevTool, \
                         ScrapeWebsiteTool, \
                         WebsiteSearchTool

docs_scrape_tool = ScrapeWebsiteTool(
    website_url="https://crustdata.notion.site/Crustdata-Dataset-API-Detailed-Examples-b83bd0f1ec09452bb0c2cac811bba88c#b64f2bcf91b347d3b577e914bf816222"
)
# Define Tasks
inquiry_resolution = Task(
    description=(
        "{customer} just reached out with a super important ask:\n"
	    "{inquiry}\n\n"
        "{person} from {customer} is the one that reached out. "
		"Make sure to use everything you know "
        "to provide the best support possible."
		"You must strive to provide a complete "
        "and accurate response to the customer's inquiry and also provide code examples for the usage or the issur faced by the {customer}."
    ),
    expected_output=(
	    "A detailed, informative response to the "
        "customer's inquiry that addresses "
        "all aspects of their question.\n"
        "The response should include references "
        "to everything you used to find the answer, "
        "including external data or solutions. "
        "Ensure the answer is complete, "
		"leaving no questions unanswered and also provide code examples for the usage or the issur faced by the {customer}, and maintain a helpful and friendly "
		"tone throughout."
    ),
	tools=[docs_scrape_tool],
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
    agent=support_quality_assurance_agent,
)


# Create Crew
crew = Crew(
  agents=[support_agent, support_quality_assurance_agent],
  tasks=[inquiry_resolution, quality_assurance_review],
  verbose=True,
  memory=True
)
# Streamlit Form for Input
st.write("### Enter Inquiry Details")
with st.form("customer_inquiry_form"):
    customer = st.text_input("Customer Name", placeholder="Enter customer name")
    person = st.text_input("Person's Name", placeholder="Enter the person's name")
    inquiry = st.text_area("Inquiry", placeholder="Enter the inquiry details")
    submitted = st.form_submit_button("Submit Inquiry")

    if submitted:
        if not customer or not inquiry:
            st.warning("Please provide both the Customer Name and Inquiry.")
        else:
            # Inputs for CrewAI
            inputs = {
                "customer": customer,
                "person": person,
                "inquiry": inquiry
            }

            # Run CrewAI Workflow
            st.write("### Processing Inquiry...")
            try:
                result = crew.kickoff(inputs=inputs)

                # Retrieve task outputs
                #inquiry_response = result["inquiry_resolution"]
                #quality_review = result["quality_assurance_review"]

                # Display the results
                st.write("### Inquiry Resolution Response")
                st.markdown(result)

                #st.write("### Quality Assurance Review")
                #st.markdown(quality_review)
            except KeyError as e:
                st.error(f"Task output missing: {e}")
            except Exception as e:
                st.error(f"Error processing the inquiry: {e}")
