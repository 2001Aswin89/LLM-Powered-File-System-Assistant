import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from google.genai import types


from fs_tools import (
    list_files,
    read_file,
    search_in_file,
    write_file,
)


load_dotenv()
LLM_PROVIDER = "gemini"      # openai | gemini
# LLM_PROVIDER = "openai"     # openai | gemini
# MODEL_NAME = "gpt-4o-mini"
MODEL_NAME =  "gemini-3.1-flash-lite" #"gemini-flash-latest"


def get_llm_client():
    """
    Returns the configured LLM client.
    """

    if LLM_PROVIDER == "openai":
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY not found."
            )

        return OpenAI(api_key=api_key)

    elif LLM_PROVIDER == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY not found."
            )

        return genai.Client(api_key=api_key)

    raise ValueError(
        f"Unsupported provider: {LLM_PROVIDER}"
    )



TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a TXT, PDF, or DOCX file and return its content and metadata.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file."
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory. Optionally filter by extension.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string"
                    },
                    "extension": {
                        "type": "string"
                    }
                },
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text to a file. Creates missing directories automatically.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string"
                    },
                    "content": {
                        "type": "string"
                    }
                },
                "required": [
                    "filepath",
                    "content"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_in_file",
            "description": "Search for a keyword in a supported file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string"
                    },
                    "keyword": {
                        "type": "string"
                    }
                },
                "required": [
                    "filepath",
                    "keyword"
                ]
            }
        }
    },
]

GEMINI_TOOLS = [
    read_file,
    list_files,
    write_file,
    search_in_file,
]

def execute_tool(tool_name: str, arguments: dict) -> dict:
    """
    Execute the requested tool from fs_tools.py.

    Args:
        tool_name: Name of the tool requested by the LLM.
        arguments: Dictionary containing the tool arguments.

    Returns:
        Dictionary returned by the corresponding fs_tools function.
    """
    if tool_name == "read_file":
        filepath = arguments.get("filepath")

        if not filepath:
            return {
                "success": False,
                "error": "Missing required argument: filepath",
            }

        return read_file(filepath)

    if tool_name == "list_files":
        directory = arguments.get("directory")

        if not directory:
            return {
                "success": False,
                "error": "Missing required argument: directory",
            }
        return list_files(
            directory,
            arguments.get("extension"),
        )    

    if tool_name == "write_file":
        filepath = arguments.get("filepath")
        content = arguments.get("content")

        if not filepath:
            return {
            "success": False,
            "error": "Missing required argument: filepath",
        }

        if content is None:
            return {
                "success": False,
                "error": "Missing required argument: content",
            }

        return write_file(
            filepath,
            content,
        )

    if tool_name == "search_in_file":
        filepath = arguments.get("filepath")
        keyword = arguments.get("keyword")

        if not filepath:
            return {
                "success": False,
            "error": "Missing required argument: filepath",
        }

        if not keyword:
            return {
                "success": False,
                "error": "Missing required argument: keyword",
            }

        return search_in_file(
            filepath,
            keyword,
        )

    return {
        "success": False,
        "content": "",
        "metadata": {},
        "error": f"Unknown tool: {tool_name}",
    }
def run_chat(user_query: str):
    if LLM_PROVIDER == "openai":
        return run_openai_chat(user_query)

    elif LLM_PROVIDER == "gemini":
        return run_gemini_chat(user_query)

    raise ValueError(
        f"Unsupported provider: {LLM_PROVIDER}"
    )

SYSTEM_PROMPT = """
You are a file-system assistant that helps users inspect and manage files.

You have access to these tools:

- list_files(directory)
    Lists files and directories.

- read_file(filepath)
    Reads the contents of supported files.
    Supported formats include:
    - .txt
    - .docx
    - .pdf

- search_in_file(filepath, query)
    Searches for a query inside a supported file.

- write_file(filepath, content)
    Writes text content to a file.

IMPORTANT FILE HANDLING RULES:

1. PDF files ARE supported.
2. You MUST use read_file() when the user asks you to read or inspect a PDF.
3. Do NOT claim that PDFs cannot be read.
4. Do NOT assume a file is unsupported based only on its extension.
5. If you need to find relevant files first, use list_files().
6. If the user asks a question requiring information from multiple files, inspect the relevant files using the available tools before answering.
7. For questions involving resumes, search/list the resumes and inspect the relevant files.
8. Base your answer only on information returned by the tools.
9. If a tool reports that a file cannot be read, explain that limitation to the user.
10. Do not invent information that was not returned by the tools.

For resume-related questions:

- The resume directory is usually samples/resumes.
- You may use list_files("samples/resumes") to discover available resumes.
- You may use read_file() on both TXT and PDF resumes.
- PDF resumes should be treated exactly like other supported resume files.
- When the user asks about experience, skills, technologies, testing, frontend/backend development, etc., inspect the relevant resumes rather than assuming information from filenames.

Always use the available tools when they are necessary to answer the user's request.
"""

# Conversation history
messages = []

def run_gemini_chat(user_query):
    """
    Runs a conversation with Gemini while maintaining
    conversation history and allowing tool calling.
    """

    global messages

    client = get_llm_client()

    # Add current user message
    messages.append(
        {
            "role": "user",
            "parts": [
                {
                    "text": user_query,
                }
            ],
        }
    )

    try:
        response = client.models.generate_content(
        model=MODEL_NAME,
        contents=messages,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=GEMINI_TOOLS,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=False
            ),
        ),
    )

    except Exception as e:
        print(f"\nGemini Error:\n{e}\n")
        return None

    assistant_response = response.text

    print("\nAssistant:\n")
    print(assistant_response)

    # Save assistant reply for future context
    messages.append(
        {
            "role": "model",
            "parts": [
                {
                    "text": assistant_response,
                }
            ],
        }
    )

    return assistant_response
    


def run_openai_chat(user_query: str) -> None:
    """
    Send the user's query to the LLM and execute any requested tools.

    Args:
        user_query: Natural language query from the user.
    """

    messages: list[dict] = [
        {
            "role": "system",
            "content": (
                "You are a Resume File Assistant.\n"
                "\n"
                "Rules:\n"
                "- Always use the available tools for filesystem operations.\n"
                "- Never invent filenames.\n"
                "- Never invent file contents.\n"
                "- Base every answer only on tool outputs.\n"
                "- If a tool reports an error, explain it to the user.\n"
            ),
        },
        {
            "role": "user",
            "content": user_query,
        },
    ]

    while True:

        try:
            client = get_llm_client()
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
        except Exception as exc:
            print(f"\nOpenAI API Error: {exc}")
            return

        message = response.choices[0].message

        if not message.tool_calls:

            if message.content:
                print("\nAssistant:\n")
                print(message.content)
            else:
                print("\nAssistant returned no response.")

            return

        messages.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in message.tool_calls
                ],
            }
        )

        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name

            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                print(
                    f"Failed to parse tool arguments for {tool_name}."
                )
                continue

            tool_result = execute_tool(
                tool_name,
                arguments,
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result),
                }
            )

def main() -> None:
    """
    Entry point for the Resume File Assistant.
    """

    print("=" * 60)
    print("Resume File Assistant")
    print("\nSupported operations:")
    print("- Read a file")
    print("- List files")
    print("- Search within files")
    print("- Write text files")
    print("Type 'exit' or 'quit' to close the assistant.")
    print("=" * 60)

    while True:

        try:
            user_query = input("\nYou: ").strip()

            if not user_query:
                continue

            if user_query.lower() in {"exit", "quit"}:
                print("\nGoodbye!")
                break

            run_chat(user_query)

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break

        


if __name__ == "__main__":
    main()