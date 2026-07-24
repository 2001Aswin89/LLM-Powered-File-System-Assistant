import json
from unittest.mock import MagicMock, patch
import src.llm_file_assistant as assistant

import pytest

import llm_file_assistant

def test_execute_tool_unknown_tool():
    result = llm_file_assistant.execute_tool(
        "unknown_tool",
        {},
    )

    assert result["success"] is False
    assert "Unknown tool" in result["error"]

def test_execute_tool_read_file(mocker):
    mocked = mocker.patch(
        "llm_file_assistant.read_file",
        return_value={"success": True},
    )

    result = llm_file_assistant.execute_tool(
        "read_file",
        {"filepath": "resume.txt"},
    )

    mocked.assert_called_once_with("resume.txt")
    assert result["success"] is True

def test_execute_tool_list_files(mocker):
    mocked = mocker.patch(
        "llm_file_assistant.list_files",
        return_value=[],
    )

    llm_file_assistant.execute_tool(
        "list_files",
        {
            "directory": "samples",
            "extension": ".txt",
        },
    )

    mocked.assert_called_once_with(
        "samples",
        ".txt",
    )

def test_execute_tool_write_file(mocker):
    mocked = mocker.patch(
        "llm_file_assistant.write_file",
        return_value={"success": True},
    )

    llm_file_assistant.execute_tool(
        "write_file",
        {
            "filepath": "notes.txt",
            "content": "hello",
        },
    )

    mocked.assert_called_once_with(
        "notes.txt",
        "hello",
    )

def test_execute_tool_search(mocker):
    mocked = mocker.patch(
        "llm_file_assistant.search_in_file",
        return_value={"success": True},
    )

    llm_file_assistant.execute_tool(
        "search_in_file",
        {
            "filepath": "resume.txt",
            "keyword": "Python",
        },
    )

    mocked.assert_called_once_with(
        "resume.txt",
        "Python",
    )

def test_run_chat_final_response(mocker):
    message = MagicMock()
    message.tool_calls = None
    message.content = "Hello from the assistant."

    response = MagicMock()
    response.choices = [MagicMock(message=message)]

    fake_client = MagicMock()

    fake_client.chat.completions.create.return_value = response

    mocker.patch(
        "llm_file_assistant.get_llm_client",
        return_value=fake_client,
    )

    mocked_print = mocker.patch("builtins.print")

    llm_file_assistant.run_chat("Hello")

    fake_client.chat.completions.create.assert_called_once()
    mocked_print.assert_any_call("Hello from the assistant.")

def test_run_chat_tool_call(mocker):
    tool_call = MagicMock()
    tool_call.id = "tool_1"
    tool_call.type = "function"
    tool_call.function.name = "read_file"
    tool_call.function.arguments = json.dumps(
        {
            "filepath": "resume.txt"
        }
    )

    first_message = MagicMock()
    first_message.content = None
    first_message.tool_calls = [tool_call]

    first_response = MagicMock()
    first_response.choices = [MagicMock(message=first_message)]

    second_message = MagicMock()
    second_message.content = "Resume successfully read."
    second_message.tool_calls = None

    second_response = MagicMock()
    second_response.choices = [MagicMock(message=second_message)]

    fake_client = MagicMock()

    fake_client.chat.completions.create.side_effect = [
        first_response,
        second_response,
    ]

    mocker.patch(
        "llm_file_assistant.get_llm_client",
        return_value=fake_client,
    )

    mocked_execute = mocker.patch(
        "llm_file_assistant.execute_tool",
        return_value={"success": True},
    )

    mocked_print = mocker.patch("builtins.print")

    llm_file_assistant.run_chat("Read resume")

    assert fake_client.chat.completions.create.call_count == 2

    mocked_execute.assert_called_once_with(
        "read_file",
        {"filepath": "resume.txt"},
    )

    mocked_print.assert_any_call(
        "Resume successfully read."
    )

def test_run_chat_api_error(mocker):
    fake_client = MagicMock()

    fake_client.chat.completions.create.side_effect = Exception(
        "API unavailable"
    )

    mocker.patch(
        "llm_file_assistant.get_llm_client",
        return_value=fake_client,
    )

    mocked_print = mocker.patch("builtins.print")

    llm_file_assistant.run_chat("Hello")

    mocked_print.assert_any_call(
        "\nOpenAI API Error: API unavailable"
    )