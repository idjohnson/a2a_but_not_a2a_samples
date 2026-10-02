import json
import os

import requests

URL = os.getenv("REIMBURSE_URL", "http://127.0.0.1:8000/chat")


def send(message: str, session_id):
    resp = requests.post(
        URL, json={"message": message, "session_id": session_id}, timeout=120
    )
    resp.raise_for_status()
    return resp.json()


def fill_form(data: dict) -> str:
    if data.get("instructions"):
        print(f"Instructions: {data['instructions']}")
    values = {}
    for key, current in data["form_data"].items():
        if key == "request_id":
            values[key] = current
            continue
        shown = "" if str(current).startswith("<") else current
        entered = input(f"{key} [{shown}]: ").strip()
        values[key] = entered or shown
    return json.dumps(values)


def main():
    print("Expense Reimbursement CLI. Type 'quit' or 'exit' to stop.")
    session_id = None
    while True:
        try:
            message = input("\nYou: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break
        if message.strip().lower() in ("quit", "exit"):
            break
        if not message.strip():
            continue

        try:
            data = send(message, session_id)
            session_id = data["session_id"]
            while data["type"] == "form":
                print("\nPlease complete the form:")
                data = send(fill_form(data), session_id)
            print(f"\nAgent: {data['response']}")
        except requests.exceptions.ConnectionError:
            print(f"Error: could not connect to {URL}. Is the server running?")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
