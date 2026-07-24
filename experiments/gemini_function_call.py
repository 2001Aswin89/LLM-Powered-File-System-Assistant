import os
import sys


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.insert(0, PROJECT_ROOT)

from src.fs_tools import list_files

from dotenv import load_dotenv
from google import genai
print(list_files("samples"))
print(list_files("samples/resumes"))

def list_sample_files(directory: str):
    """List all files in the resume folder in the samples directory."""
    return list_files(directory)

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def say_hello(name: str):
    return f"Hello {name}!"


response = client.models.generate_content(
    model="gemini-flash-latest",
    contents="List all files in the resume folder in the samples directory.",
    config={
        "tools": [say_hello, list_sample_files],
    },
)

print(response.text)