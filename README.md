# LLM-Powered File System Assistant

An LLM-powered Python assistant that allows users to interact with local resume files using natural-language requests.

The assistant uses LLM tool/function calling to decide when to perform filesystem operations such as reading, listing, searching, and writing files.

---

## Features

- Read `.txt`, `.pdf`, and `.docx` files
- List files in a directory
- Filter files by extension
- Search files for keywords with surrounding context
- Write text files and create missing directories
- Natural-language interaction with an LLM
- Automatic tool/function calling
- Gemini and OpenAI provider support
- API keys loaded securely from `.env`
- Automated tests for filesystem and LLM assistant functionality

---

## Project Structure

    LLM-Powered-File-System-Assistant/
    │
    ├── src/
    │   ├── fs_tools.py
    │   └── llm_file_assistant.py
    │
    ├── tests/
    │   ├── conftest.py
    │   ├── test_fs_tools.py
    │   └── test_llm_file_assistant.py
    │
    ├── samples/
    │   └── resumes/
    │       ├── resume_david_lee1.pdf
    │       ├── resume_emma_wilson.txt
    │       ├── resume_john_doe.txt
    │       ├── resume_raj_patel.txt
    │       └── resume_sarah_johnson.pdf
    │
    ├── .env.example
    ├── .gitignore
    ├── requirements.txt
    └── README.md

---

## Requirements

- Python 3.11+
- API key for the selected LLM provider
- Internet connection when using the LLM

---

## Setup

### 1. Clone the repository

    git clone <repository-url>
    cd LLM-Powered-File-System-Assistant

### 2. Create a virtual environment

#### Windows

    python -m venv .venv
    .venv\Scripts\activate

#### Linux / macOS

    python3 -m venv .venv
    source .venv/bin/activate

### 3. Install dependencies

    pip install -r requirements.txt

### 4. Configure environment variables

Create a `.env` file in the project root.

For Gemini:

    GEMINI_API_KEY=your-gemini-api-key

For OpenAI:

    OPENAI_API_KEY=your-openai-api-key

The repository includes `.env.example` as a template.

Do not commit `.env` or API keys to Git.

---

## LLM Provider Configuration

The provider and model are configured in:

    src/llm_file_assistant.py

### Gemini

    LLM_PROVIDER = "gemini"
    MODEL_NAME = "gemini-3.1-flash-lite"

### OpenAI

    LLM_PROVIDER = "openai"
    MODEL_NAME = "gpt-4o-mini"

The rest of the application uses the same filesystem tools regardless of the selected provider.

The LLM client is created through:

    get_llm_client()

Requests are routed through:

    run_chat()

This allows the provider to be changed through configuration rather than changing the filesystem implementation.

---

## Running the Assistant

From the project root:

    python src/llm_file_assistant.py

The application starts an interactive CLI:

    ============================================================
    Resume File Assistant

    Supported operations:
    - Read a file
    - List files
    - Search within files
    - Write text files
    Type 'exit' or 'quit' to close the assistant.
    ============================================================

    You:

Enter a natural-language request.

Use `exit` or `quit` to close the assistant.

---

## Example Queries

### List resumes

    You: list all resumes

The assistant can use `list_files()` to inspect the `samples/resumes` directory.

### Search resumes

    You: find resumes mentioning Python experience

The assistant can search the relevant resume files and return matching information.

### Find experienced candidates

    You: list people with 5 or more years of experience

The assistant can inspect resume content and identify candidates whose experience matches the request.

### Read a resume

    You: read resume_john_doe.txt

The assistant can use `read_file()` to retrieve the resume contents.

### Write a file

    You: create a summary file for resume_john_doe.txt

The assistant can read the resume, generate the requested content, and use `write_file()` to create the output file.

---

## Filesystem Tools

The core filesystem functionality is implemented in:

    src/fs_tools.py

### `read_file()`

    read_file(filepath: str) -> dict

Reads supported files and returns structured content and metadata.

Supported formats:

- TXT
- PDF
- DOCX

### `list_files()`

    list_files(directory: str, extension: str = None) -> list

Lists files in a directory.

Returned metadata includes:

- filename
- path
- size
- modification time

An optional extension can be supplied to filter results.

### `write_file()`

    write_file(filepath: str, content: str) -> dict

Writes text to a file and creates missing parent directories when necessary.

### `search_in_file()`

    search_in_file(filepath: str, keyword: str) -> dict

Performs a case-insensitive keyword search and returns matching lines with surrounding context.

---

## Architecture

The project is divided into two main layers:

    User
     │
     ▼
    llm_file_assistant.py
     │
     │ Natural-language request
     ▼
    Selected LLM Provider
    (Gemini / OpenAI)
     │
     │ Tool / Function Call
     ▼
    fs_tools.py
     │
     ├── read_file()
     ├── list_files()
     ├── search_in_file()
     └── write_file()
     │
     ▼
    Local Files
    (samples/resumes)
     │
     ▼
    Tool Result
     │
     ▼
    LLM
     │
     ▼
    Assistant Response

### Core responsibilities

`fs_tools.py`

- Implements actual filesystem operations.
- Does not depend on the LLM.

`llm_file_assistant.py`

- Provides the CLI.
- Configures the LLM provider.
- Registers filesystem tools with the LLM.
- Handles tool/function calling.
- Maintains the conversation flow.
- Returns natural-language responses.

---

## Testing

Run the complete test suite:

    pytest -v

Run filesystem tests only:

    pytest tests/test_fs_tools.py -v

Run LLM assistant tests only:

    pytest tests/test_llm_file_assistant.py -v

The tests cover:

- File reading
- Missing-file handling
- DOCX reading
- Directory listing
- Extension filtering
- Invalid directories
- File writing
- Keyword searching
- No-match searches
- Tool execution
- Tool arguments
- LLM integration behavior
- Error handling

Tests should not require real API calls when mocked provider behavior is being tested.

---

## Security

API keys are loaded from environment variables using `python-dotenv`.

Example:

    GEMINI_API_KEY=your-api-key

Never hard-code API keys in source code.

Never commit `.env` to Git.

The `.gitignore` should exclude sensitive and generated files such as:

    .env
    .venv/
    __pycache__/
    .pytest_cache/

---

## Sample Data

The project includes sample resumes in:

    samples/resumes/

The sample dataset contains both text and PDF resumes and is used to demonstrate the assistant's filesystem and search capabilities.

---

## Assignment Deliverables

The project includes:

- Python source code
- Filesystem tools
- LLM integration with tool/function calling
- `requirements.txt`
- Sample resume files
- Automated tests
- `README.md`
- Environment configuration example

A short demonstration should show the assistant running and performing multiple filesystem operations through natural-language requests.

---

## Recommended Demo Flow

A short demonstration can show:

    1. Start the assistant
    2. List the available resumes
    3. Search for a specific skill or experience
    4. Read a matching resume
    5. Create/write a summary file
    6. Exit the assistant

This demonstrates the complete flow:

    Natural-language request
            ↓
           LLM
            ↓
       Tool selection
            ↓
    Filesystem operation
            ↓
        Tool result
            ↓
           LLM
            ↓
    Assistant response
            ↓
           User

---

## Git Workflow

Development uses feature branches and the `develop` branch.

Typical workflow:

    git checkout develop
    git pull origin develop

    git checkout -b <feature-or-task-branch>

    # Make changes

    git status
    git add .
    git commit -m "description of changes"
    git push -u origin <feature-or-task-branch>

After testing and review, the feature branch can be merged into `develop`.

The stable `develop` branch can subsequently be merged into `main`.

---

## Current LLM Configuration

The project supports:

- Gemini
- OpenAI

The provider is selected through:

    LLM_PROVIDER

and the selected model through:

    MODEL_NAME

The implementation can therefore switch between supported providers without changing the filesystem tools.

---

## License

No specific open-source license is currently defined for this project.

---

## Author

Developed as an LLM-powered file-system assistant project demonstrating:

- Python
- LLM integration
- Tool/function calling
- Filesystem automation
- API integration
- Automated testing
- Git-based development