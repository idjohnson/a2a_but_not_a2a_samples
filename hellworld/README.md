# Echo Bot Project

This project contains a Python FastAPI server with an `echo_bot` endpoint and a Python-based CLI to interact with it.

## Prerequisites
- Python 3.8+
- Virtual Environment (recommended)

## Setup Instructions

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```

2. **Activate the virtual environment:**
   - On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

3. **Install the requirements:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### 1. Start the FastAPI Server
Open a terminal, ensure your virtual environment is activated, and run:
```bash
uvicorn server:app --reload
```
The server will start on `http://127.0.0.1:8000`. You can view the interactive API documentation at `http://127.0.0.1:8000/docs`.

### 2. Run the CLI
Open a *new* terminal window (leave the server running in the first one), activate the virtual environment again, and run:
```bash
python cli.py
```

The CLI will prompt you to enter text. It will send your input to the server and display the response.

- If you enter text, it will respond with: `Hello, World! I have received your request ({user_request}`
- If you enter empty text (just press enter), it will respond with: `No text input is provided!`

Type `quit` or `exit` to stop the CLI.
