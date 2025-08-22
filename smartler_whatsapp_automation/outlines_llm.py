import os
from dotenv import load_dotenv
from google.auth import default
import outlines
import google.auth.transport.requests
import openai

load_dotenv()

GCLOUD_PROJECT_ID = os.environ.get("GCLOUD_PROJECT_ID")
GCLOUD_LOCATION = os.environ.get("GCLOUD_LOCATION")

credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
credentials.refresh(google.auth.transport.requests.Request())

def get_outlines_llm():
    """Gets the outlines language model.

    This function initializes and returns an outlines language model that is
    configured to use Google's Gemini model through the Vertex AI API.

    It handles authentication with Google Cloud and configures the OpenAI
    client to connect to the Vertex AI endpoint.

    Returns:
        outlines.models.openai.OpenAI: The outlines language model.
    """
    openai_handshake = openai.OpenAI(
        base_url=f"https://{GCLOUD_LOCATION}-aiplatform.googleapis.com/v1/projects/{GCLOUD_PROJECT_ID}/locations/{GCLOUD_LOCATION}/endpoints/openapi",
        api_key=credentials.token
    )
    outlines_llm=outlines.from_openai(openai_handshake, "google/gemini-2.0-flash-001")
    return outlines_llm

def test():
    outlines_llm = get_outlines_llm()
    print(outlines_llm("why is the sky blue?"))

    from pydantic import BaseModel
    class Phone(BaseModel):
        country_code: str
        number: str
    contact = outlines_llm("extract the contact details from the following text: 'John Doe, his number is +14044832145'", Phone)
    print(contact)


if __name__ == "__main__":
    test()
    
