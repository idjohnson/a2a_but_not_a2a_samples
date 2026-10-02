import os
import json
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
URL = os.getenv("REIMBURSE_URL", "http://127.0.0.1:8000/chat")

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Expense Reimbursement</title>
    <style>
        body { font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; }
        #chatbox { height: 400px; border: 1px solid #ccc; overflow-y: scroll; padding: 10px; margin-bottom: 10px; background-color: #fafafa; }
        .msg-container { margin-bottom: 10px; clear: both; overflow: hidden; }
        .user-msg { color: #fff; background-color: #007bff; float: right; padding: 8px 12px; border-radius: 15px; max-width: 80%; }
        .agent-msg { color: #000; background-color: #e9ecef; float: left; padding: 8px 12px; border-radius: 15px; max-width: 80%; }
        .system-msg { color: red; text-align: center; clear: both; }
        #input-area { display: flex; }
        #input-area input[type="text"] { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
        #input-area button { padding: 10px 15px; margin-left: 5px; cursor: pointer; border: none; background-color: #007bff; color: white; border-radius: 4px; }
        .form-container { background: #fff; padding: 15px; margin-top: 10px; border: 1px solid #ddd; border-radius: 5px; clear: both; float: left; width: 100%; box-sizing: border-box; }
        .form-container label { display: block; margin-top: 10px; font-weight: bold; }
        .form-container input { width: 100%; padding: 8px; margin-top: 5px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
        .form-btn { margin-top: 15px; padding: 10px 15px; cursor: pointer; border: none; background-color: #28a745; color: white; border-radius: 4px; width: 100%; }
    </style>
</head>
<body>
    <h2>Expense Reimbursement</h2>
    <div id="chatbox">
        <div class="msg-container">
            <div class="agent-msg">Hello! I am the expense reimbursement agent. What expense report do you have a question about or need to submit?</div>
        </div>
    </div>
    
    <div id="input-area">
        <input type="text" id="user-input" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
        <button onclick="sendMessage()">Send</button>
    </div>
    
    <div id="form-area" style="display: none;">
        <div class="form-container" id="dynamic-form">
            <!-- Form fields go here -->
        </div>
        <button class="form-btn" onclick="submitForm()">Submit Form</button>
    </div>

    <script>
        const chatbox = document.getElementById('chatbox');
        const userInput = document.getElementById('user-input');
        const inputArea = document.getElementById('input-area');
        const formArea = document.getElementById('form-area');
        const dynamicForm = document.getElementById('dynamic-form');
        let currentSessionId = null;

        function appendMessage(sender, text, isHtml=false) {
            const containerDiv = document.createElement('div');
            containerDiv.className = 'msg-container';
            
            const msgDiv = document.createElement('div');
            if (sender === 'You') {
                msgDiv.className = 'user-msg';
            } else if (sender === 'System') {
                msgDiv.className = 'system-msg';
            } else {
                msgDiv.className = 'agent-msg';
            }
            
            if(isHtml) {
                msgDiv.innerHTML = text;
            } else {
                msgDiv.innerText = text;
            }
            
            containerDiv.appendChild(msgDiv);
            chatbox.appendChild(containerDiv);
            chatbox.scrollTop = chatbox.scrollHeight;
        }

        function handleKeyPress(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        }

        async function sendToServer(message) {
            try {
                appendMessage('System', 'Loading...', true);
                const loadingMsg = chatbox.lastChild;
                
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message, session_id: currentSessionId })
                });
                
                chatbox.removeChild(loadingMsg);
                
                const data = await response.json();
                if (data.error) {
                    appendMessage('System', 'Error: ' + data.error);
                    inputArea.style.display = 'flex';
                    return;
                }
                
                currentSessionId = data.session_id;

                if (data.type === 'form') {
                    renderForm(data);
                } else {
                    appendMessage('Agent', data.response);
                    inputArea.style.display = 'flex';
                    formArea.style.display = 'none';
                    userInput.focus();
                }
            } catch (error) {
                appendMessage('System', 'Failed to communicate with server.');
                inputArea.style.display = 'flex';
            }
        }

        function sendMessage() {
            const text = userInput.value.trim();
            if (!text) return;
            appendMessage('You', text);
            userInput.value = '';
            inputArea.style.display = 'none';
            
            sendToServer(text);
        }

        function renderForm(data) {
            inputArea.style.display = 'none';
            formArea.style.display = 'block';
            dynamicForm.innerHTML = '';
            
            if (data.instructions) {
                const instDiv = document.createElement('div');
                instDiv.innerText = data.instructions;
                instDiv.style.marginBottom = '10px';
                instDiv.style.color = '#333';
                dynamicForm.appendChild(instDiv);
            }

            for (const [key, value] of Object.entries(data.form_data)) {
                if (key === 'request_id') {
                    const hiddenInput = document.createElement('input');
                    hiddenInput.type = 'hidden';
                    hiddenInput.id = `form-${key}`;
                    hiddenInput.value = value;
                    dynamicForm.appendChild(hiddenInput);
                    continue;
                }
                
                const label = document.createElement('label');
                label.innerText = key;
                
                const input = document.createElement('input');
                input.type = 'text';
                input.id = `form-${key}`;
                
                const shown = String(value).startsWith('<') ? '' : value;
                input.value = shown;
                input.placeholder = String(value).startsWith('<') ? value : '';
                
                dynamicForm.appendChild(label);
                dynamicForm.appendChild(input);
            }
            chatbox.scrollTop = chatbox.scrollHeight;
        }

        function submitForm() {
            const formData = {};
            const inputs = dynamicForm.querySelectorAll('input');
            inputs.forEach(input => {
                const key = input.id.replace('form-', '');
                formData[key] = input.value;
            });
            
            appendMessage('You', '<i>[Submitted Form]</i>', true);
            formArea.style.display = 'none';
            sendToServer(JSON.stringify(formData));
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    session_id = data.get("session_id")

    try:
        resp = requests.post(
            URL, json={"message": message, "session_id": session_id}, timeout=120
        )
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.exceptions.ConnectionError:
        return jsonify({"error": f"could not connect to {URL}. Is the backend server running?"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
