# feedback_service.py

from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# --- LLM Output Validation ---

class CompetencyFeedback(BaseModel):
    competency_name: str = Field(..., description="The name of the competency.")
    user_strengths: str = Field(..., description="Summary of user's strengths for this competency.")
    improvement_areas: str = Field(..., description="Specific suggestions on how the user can improve in this competency.")

class CompetencyAreaFeedback(BaseModel):
    competency_area: str = Field(..., description="The competency area being assessed.")
    feedbacks: list[CompetencyFeedback] = Field(..., description="List of feedback entries for each competency within the area.")

    def to_json(self):
        return self.dict()

# --- LLM Initialization ---

def init_llm():
    """Initialize OpenAI LLM (not Azure)"""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    return ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=api_key,
        temperature=0
    )

# --- Feedback Chain Creation ---

def create_feedback_chain(llm):
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a helpful assistant specializing in providing detailed feedback for Systems Engineering Competency Assessments.\n"
            "You will receive information about the user's current competency levels and the indicator for this level in various areas of systems engineering, "
            "as well as the required levels of competency on the indicator for this level each area. Your role is to analyze this information and provide constructive, "
            "personalized feedback.\n\n"
            "The feedback should:\n"
            "1. Summarize the user's strengths, highlighting areas where they meet or exceed expectations.\n"
            "2. Identify gaps where the user's current level does not meet the required level.\n"
            "3. Offer specific, actionable suggestions on how the user can improve their competency in each area, but only if the user's "
            "recorded level is below the required level.\n"
            "4. Use a supportive tone that encourages growth, emphasizing practical methods to close knowledge gaps, such as additional training, "
            "hands-on practice, mentorship, or specific resources.\n\n"
            "Your primary focus is to help the user advance their skills in systems engineering and ensure they feel empowered to grow professionally.\n"
            "5. Do not explicitly specify to the user their competency levels like 'kennen' or 'verstehen'; instead, use the terms 'Awareness' for 'kennen', 'Understanding' for 'verstehen', 'Applying' for 'anwenden' and 'Mastering' for 'Beherrschen'  and "
            "'required level' or something similar.\n"
            "6. For competencies where the user's recorded level meets or exceeds the required level, do not provide any improvement suggestions.\n"
        )),
        ("user", """
        Competency Area: {competency_area}

        Below are the user's competency levels and required competency levels for each competency within this area:

        {competency_details}

        Provide an overall feedback for each competency in this area, highlighting strengths and areas for improvement.
        """)
    ])
    structured_llm = llm.with_structured_output(CompetencyAreaFeedback)
    return prompt | structured_llm

# --- Feedback Generation Function ---

def generate_feedback_with_llm(competency_area, competencies):
    llm = init_llm()
    feedback_chain = create_feedback_chain(llm)

    # Prepare competency details for LLM input
    competency_details = ""
    for competency in competencies:
        competency_details += (
            f"- Competency Name: {competency['competency_name']}\n"
            f"- User Level: {competency['user_level']}\n"
            f"- User Recorded Level Indicator: {competency['user_indicator']}\n"
            f"- Required Level: {competency['required_level']}\n\n"
            f"- User Required Level Indicator: {competency['required_indicator']}\n\n"
        )

    inputs = {
        "competency_area": competency_area,
        "competency_details": competency_details
    }
    structured_feedback = feedback_chain.invoke(inputs)
    return structured_feedback.to_json()
