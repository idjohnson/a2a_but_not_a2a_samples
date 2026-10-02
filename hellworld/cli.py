import sys
import requests

def main():
    print("Welcome to the Echo Bot CLI!")
    print("Type your message and press Enter. Type 'quit' or 'exit' to stop.")
    
    url = "http://127.0.0.1:8000/echo_bot"
    
    while True:
        try:
            user_input = input("\nEnter text: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break
            
        if user_input.strip().lower() in ['quit', 'exit']:
            print("Exiting...")
            break
            
        payload = {"user_request": user_input}
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            print(f"Server response: {data.get('response')}")
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to the server at http://127.0.0.1:8000")
            print("Please ensure the FastAPI server is running (e.g. 'uvicorn server:app').")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
