import os
from dotenv import load_dotenv
import google.auth
import vertexai
from google.cloud import aiplatform

print("--- Initializing Core Authentication ---")

# Load environment variables from a .env file
load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def detect_approach():
    """
    Detect which approach to use based on available credentials.
    
    Returns:
        str: "VERTEXAI" if PROJECT_ID and LOCATION are available, 
             "API" if GOOGLE_API_KEY is available,
             raises Exception if no valid credentials found
    """
    if PROJECT_ID and LOCATION:
        return "VERTEXAI"
    elif GOOGLE_API_KEY:
        return "API"
    else:
        raise Exception("No valid credentials found. Need either PROJECT_ID + LOCATION for VertexAI or GOOGLE_API_KEY for API approach")

try:
    if PROJECT_ID and LOCATION:
        CREDENTIALS, discovered_project_id = google.auth.default()
        if not PROJECT_ID and discovered_project_id:
            PROJECT_ID = discovered_project_id

        if PROJECT_ID and LOCATION:
            vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=CREDENTIALS)
            print("✅ NanoBanana with Vertex AI (Legacy SDK) Initialized.")

            aiplatform.init(project=PROJECT_ID, location=LOCATION, credentials=CREDENTIALS)
            print("✅ NanoBanana with AI Platform SDK Initialized.")
        else:
            print("\033[93mNanoBanana Config Warning: PROJECT_ID or LOCATION not found. Nodes will fail.\033[0m")
    else:
        print("\033[93mNanoBanana Config Warning: PROJECT_ID or LOCATION not set. Using API approach.\033[0m")

except Exception as e:
    print(f"\033[91mAn unexpected error occurred during NanoBanana initialization: {e}\033[0m")