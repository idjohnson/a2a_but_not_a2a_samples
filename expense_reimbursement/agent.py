import json
import os
import random
from typing import Any, Optional

import litellm

MODEL = os.getenv("LITELLM_MODEL", "vertex_ai/gemini-2.5-flash")
MAX_TOOL_ROUNDS = 8

SYSTEM_PROMPT = """
You are an agent who handles the reimbursement process for employees.

When you receive a reimbursement request, first create a new request form using create_request_form(). Only provide values that the user supplied, otherwise use an empty string.
  1. 'date': the date of the transaction.
  2. 'amount': the dollar amount of the transaction.
  3. 'purpose': the business justification/purpose of the reimbursement.

Once you created the form, return it to the user by calling return_form with the form data from the create_request_form call.

Once you receive the filled-out form back from the user, check it contains all required information (date, amount, purpose).
If any is missing, call return_form again with the missing fields.

For valid reimbursement requests, use reimburse() to reimburse the employee.
In your response, include the request_id and the status of the reimbursement request.
"""

# Request ids created in this process (demo only).
request_ids: set[str] = set()


def create_request_form(
    date: Optional[str] = None,
    amount: Optional[str] = None,
    purpose: Optional[str] = None,
) -> dict[str, Any]:
    request_id = "request_id_" + str(random.randint(1000000, 9999999))
    request_ids.add(request_id)
    return {
        "request_id": request_id,
        "date": date or "<transaction date>",
        "amount": amount or "<transaction dollar amount>",
        "purpose": purpose or "<business justification/purpose of the transaction>",
    }


def return_form(form_request: Any, instructions: Optional[str] = None) -> dict[str, Any]:
    if isinstance(form_request, str):
        form_request = json.loads(form_request)
    return {
        "type": "form",
        "form": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "format": "date", "title": "Date"},
                "amount": {"type": "string", "format": "number", "title": "Amount"},
                "purpose": {"type": "string", "title": "Purpose"},
                "request_id": {"type": "string", "title": "Request ID"},
            },
            "required": list(form_request.keys()),
        },
        "form_data": form_request,
        "instructions": instructions,
    }


def reimburse(request_id: str) -> dict[str, Any]:
    if request_id not in request_ids:
        return {"request_id": request_id, "status": "Error: Invalid request_id."}
    return {"request_id": request_id, "status": "approved"}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_request_form",
            "description": "Create a request form for the employee to fill out. Use empty strings for unknown values.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date of the transaction."},
                    "amount": {"type": "string", "description": "Requested amount."},
                    "purpose": {"type": "string", "description": "Purpose of the request."},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "return_form",
            "description": "Return a form to the user to complete.",
            "parameters": {
                "type": "object",
                "properties": {
                    "form_request": {
                        "type": "object",
                        "description": "The form data from create_request_form.",
                    },
                    "instructions": {
                        "type": "string",
                        "description": "Instructions for completing the form.",
                    },
                },
                "required": ["form_request"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reimburse",
            "description": "Reimburse the employee for a given request_id.",
            "parameters": {
                "type": "object",
                "properties": {"request_id": {"type": "string"}},
                "required": ["request_id"],
            },
        },
    },
]

TOOL_FUNCS = {
    "create_request_form": create_request_form,
    "return_form": return_form,
    "reimburse": reimburse,
}


class ReimbursementAgent:
    """Keeps per-session message history and runs the LiteLLM tool-calling loop."""

    def __init__(self) -> None:
        self._sessions: dict[str, list[dict[str, Any]]] = {}

    def chat(self, session_id: str, message: str) -> dict[str, Any]:
        messages = self._sessions.setdefault(
            session_id, [{"role": "system", "content": SYSTEM_PROMPT}]
        )
        messages.append({"role": "user", "content": message})

        for _ in range(MAX_TOOL_ROUNDS):
            resp = litellm.completion(model=MODEL, messages=messages, tools=TOOLS)
            msg = resp.choices[0].message
            messages.append(msg.model_dump(exclude_none=True))

            if not msg.tool_calls:
                return {"type": "text", "response": msg.content or ""}

            form = None
            for call in msg.tool_calls:
                result = self._run_tool(call.function.name, call.function.arguments)
                if call.function.name == "return_form" and "error" not in result:
                    form = result
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "name": call.function.name,
                        "content": json.dumps(result),
                    }
                )
            if form is not None:
                return form

        return {"type": "text", "response": "Error: too many tool-call rounds."}

    @staticmethod
    def _run_tool(name: str, raw_args: str) -> dict[str, Any]:
        func = TOOL_FUNCS.get(name)
        if func is None:
            return {"error": f"Unknown tool: {name}"}
        try:
            return func(**json.loads(raw_args or "{}"))
        except Exception as e:
            return {"error": str(e)}
