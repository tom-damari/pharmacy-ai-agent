"""
Tool definitions + execution for OpenAI function calling.
"""

import json
from backend.synthetic_data import (
    get_medication_by_name, check_inventory, verify_user_prescription
)


# Tool schemas(OpenAI function calling format)

TOOLS = [
    # TOOL 1 - get_medication_by_name
    {
        "type": "function",     # Tells OpenAI this is a function tool
        "function": {
            "name": "get_medication_by_name",       # Tool identifier
            "description": "Look up medication details by name. Returns dosage, active ingredient, prescription requirements, and price. Supports English and Hebrew names.",   # What the tool does (helps GPT decide when to use it)
            "parameters": {     # Input schema (JSON Schema format)
                "type": "object",       # Parameters are a JSON object
                "properties": {
                    "medication_name": {    # Parameter name
                        "type": "string",   # Data type
                        "description": "Name of the medication (English or Hebrew)"     # Parameter explanation
                    }
                },
                "required": ["medication_name"]     # Required parameter (mafdatory for this function)
            }
        }
    },
    # TOOL 2 - check_inventory
    {
        "type": "function",
        "function": {
            "name": "check_inventory",
            "description": "Check if a medication is in stock and get current quantity. Use after get_medication_by_name to check availability.",
            "parameters": {
                "type": "object",
                "properties": {
                    "medication_id": {
                        "type": "integer",
                        "description": "The medication ID (from get_medication_by_name result)"
                    }
                },
                "required": ["medication_id"]
            }
        }
    },
    # TOOL 3 - verify_user_prescription
    {
        "type": "function",
        "function": {
            "name": "verify_user_prescription",
            "description": "Verify if a user has a valid prescription for a medication. Required before dispensing prescription-only medications.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {     # User's ID number 
                        "type": "string",       # String type (9-digit ID)
                        "description": "User's 9-digit ID number"
                    },
                    "medication_name": {    # Medication to check prescription for
                        "type": "string",
                        "description": "Name of the medication to check prescription for"
                    }
                },
                "required": ["user_id", "medication_name"]      # Both parameters are mandatory
            }
        }
    }
]


# Tool excecution  
def execute_tool(name, args):
    """Execute a tool by name (tool name) with given args (tool paramteres). Returns JSON-serializable dict."""
    
    # Tool 1 Execustion
    if name == "get_medication_by_name":
        # Extract medication name from args (default to empty string if missing)
        med = get_medication_by_name(args.get("medication_name", ""))
        # If medication not found, return error
        if not med:
            return {"error": "Medication not found"}    
        # Return relevant medication fields
        return {
            "id": med["id"],
            "name": med["name"],
            "name_he": med["name_he"],
            "description": med["description"],
            "description_he": med["description_he"],
            "active_ingredient": med["active_ingredient"],
            "dosage_form": med["dosage_form"],
            "standard_dosage": med["standard_dosage"],
            "requires_prescription": med["requires_prescription"],
            "price": med["price"]
        }
    
    # Tool 2 Execustion
    elif name == "check_inventory":
        # Get medication ID from args
        med_id = args.get("medication_id")
        # Validate that medication_id was provided
        if med_id is None:
            return {"error": "medication_id is required"}
        # Call inventory check function
        stock = check_inventory(med_id)
        # If medication ID is invalid
        if not stock:
            return {"error": "Medication not found"}
        # Return stock information
        return stock
    
    # Tool 3 Execustion
    elif name == "verify_user_prescription":
        # Extract both required parameters
        user_id = args.get("user_id", "")
        med_name = args.get("medication_name", "")
        # Validate both parameters are provided
        if not user_id or not med_name:
            return {"error": "user_id and medication_name are required"}
        # Call prescription verification function
        return verify_user_prescription(user_id, med_name)
    
    # If tool name doesn't match any known tool
    else:
        return {"error": f"Unknown tool: {name}"}


def tool_result_to_str(result):
    """Convert tool result (python) dict to (JSON) string for message content."""
    return json.dumps(result, ensure_ascii=False)       # ensure_ascii=False allows Hebrew characters to remain readable
