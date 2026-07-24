import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from fs_tools import (
    list_files,
    read_file,
    search_in_file,
    write_file,
)


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
        return read_file(arguments["filepath"])

    if tool_name == "list_files":
        return list_files(
            arguments["directory"],
            arguments.get("extension"),
        )

    if tool_name == "write_file":
        return write_file(
            arguments["filepath"],
            arguments["content"],
        )

    if tool_name == "search_in_file":
        return search_in_file(
            arguments["filepath"],
            arguments["keyword"],
        )

    return {
        "success": False,
        "error": f"Unknown tool: {tool_name}",
    }

    def run_chat(user_query: str) -> None:
    """
    Send the user's query to the LLM and execute any requested tools.

    Args:
        user_query: Natural language query from the user.
    """

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful resume file assistant. "
                "Use the available tools whenever filesystem "
                "operations are required."
            ),
        },
        {
            "role": "user",
            "content": user_query,
        },
    ]

    while True:

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        message = response.choices[0].message

        if not message.tool_calls:

            if message.content:
                print("\nAssistant:\n")
                print(message.content)

            return

        messages.append(message)

        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

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

        except Exception as exc:
            print(f"\nError: {exc}")


if __name__ == "__main__":
    main()