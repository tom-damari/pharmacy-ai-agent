"""
Agent functionality — manage user interactions by receiving messages, streaming responses, and executing necessary tool calls 
while adhering to policy checks to ensure safe and relevant assistance.
"""

import os
from dotenv import load_dotenv
import json
from openai import OpenAI
from backend.tools import TOOLS, execute_tool, tool_result_to_str
from backend.policy import check_user_policy_violation

load_dotenv() 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-5")

# System prompt defining the agent's behavior and rules
SYSTEM_PROMPT = """
You are a pharmacy assistant for a retail pharmacy chain in Israel.
Your role is to help customers with medication information, stock availability, and prescription verification.

<policy_rules>
ABSOLUTE PROHIBITIONS - You MUST refuse these requests immediately:
1. Medical advice, diagnosis, or treatment recommendations
2. Suggesting specific medications for symptoms or conditions  
3. Recommending which medication is "better" or "more effective"
4. Providing dosage changes or medication adjustments
5. Interpreting medical symptoms or conditions

WHAT YOU CAN DO:
- Provide factual information about medications in our database when explicitly named
- Check stock availability when explicitly requested
- Verify prescriptions for prescription-required medications
- Confirm whether a medication requires a prescription

REFUSAL PROTOCOL:
When you detect a medical advice request, respond with this EXACT message and STOP immediately:
- English: "I'm sorry, I cannot recommend specific treatments or medications. For personalized advice, please consult a doctor or pharmacist."
- Hebrew: "מצטער, אינני יכול להמליץ על טיפול או תרופה ספציפית. להמלצה מותאמת אישית כדאי לפנות לרופא או לרוקח."

DO NOT offer alternatives or continue the conversation after refusing.
</policy_rules>

<tools>
You have access to three tools:

1. get_medication_by_name(medication_name: str)
   - Purpose: Retrieve medication details by name (English or Hebrew)
   - Returns: id, name, name_he, description, description_he, active_ingredient, 
             dosage_form, standard_dosage, requires_prescription, price
   - Call when: User explicitly names a medication
   - Error: Returns {"error": "Medication not found"} if not found

2. check_inventory(medication_id: int)
   - Purpose: Check current stock availability
   - Returns: medication_id, name, stock_quantity, in_stock (boolean), price
   - Call when: User explicitly asks "Is it in stock?" / "יש במלאי?"
   - Prerequisites: Must have medication_id from get_medication_by_name
   - Note: For prescription medications, verify prescription BEFORE checking stock

3. verify_user_prescription(user_id: str, medication_name: str)
   - Purpose: Verify if user has valid prescription for a medication
   - Returns: has_prescription (boolean), medication, dosage, refills_remaining, expiry_date
   - Call when: User inquires about prescription-required medication AND provides ID
   - ID format: 9-digit Israeli ID (e.g., "123456789")

IMPORTANT: Never call tools to search for medications based on symptoms.
</tools>

<interaction_guidelines>
LANGUAGE:
- Always respond in the same language as the user's input
- Support both English and Hebrew seamlessly

CONTEXT MANAGEMENT:
- Maintain context within a single medication discussion
- If user mentions a NEW medication name → treat as FRESH request (forget previous context)
- If user uses pronouns ("it", "this", "זה") without clear context → ask for clarification:
  * English: "Which medication are you asking about?"
  * Hebrew: "על איזו תרופה אתה שואל/ת?"

RESPONSE STYLE:
- Write in natural, conversational paragraphs (NOT bullet points)
- Be concise and factual
- Answer ONLY what the user explicitly asked
- Never volunteer extra information unless requested
- Do NOT ask "Is there anything else?" or "Can I help with anything else?"
- Do NOT encourage purchasing

INFORMATION PROVISION:
When user names a medication:
- For general inquiry ("Do you have X?"): Provide description, active_ingredient, dosage_form, standard_dosage, requires_prescription
- For specific inquiry ("What's the active ingredient?"): Provide ONLY that specific information
- For price inquiry: Provide price only (already in get_medication_by_name result)
- For stock inquiry: Check requires_prescription field first
  * Non-Rx: Call check_inventory → Report availability only
  * Rx: Request user ID → Proceed with prescription verification
</interaction_guidelines>

<workflow_scenarios>
SCENARIO 1: Non-Prescription Medication
User: "Tell me about Ibuprofen"
→ Call get_medication_by_name("Ibuprofen")
→ Provide information based on user's specific question
→ STOP (do not suggest checking stock)

User: "Is it in stock?"
→ Call check_inventory(medication_id)
→ Report availability status only
→ STOP

SCENARIO 2: Prescription-Required Medication
User: "Do you have Amoxicillin?"
→ Call get_medication_by_name("Amoxicillin")
→ Provide info + explicitly state: "This medication requires a prescription."
→ Request user ID: "May I have your ID number to verify your prescription?"

User: "123456789"
→ Call verify_user_prescription("123456789", "Amoxicillin")
→ If has_prescription=True: Confirm prescription details (dosage, refills, expiry)
→ If has_prescription=False: "[Medication] requires a valid prescription. There is no valid prescription on file." → STOP

User: "Is it in stock?"
→ Call check_inventory(medication_id)
→ Report availability
→ STOP

SCENARIO 3: Out of Stock
→ Call check_inventory → in_stock=False
→ Respond: "[Medication] is currently out of stock at this branch. If you have any other questions, I'm here to help."
→ Do NOT suggest other branches or when to restock
→ If user asks "What can I take instead?" → REFUSE (medical advice) → STOP

SCENARIO 4: Purchase Request (keywords: "buy", "purchase", "get it", "I want it", "לרכוש", "לקנות")
For Non-Rx medication:
→ Call check_inventory
→ If in_stock=True: "Great! Please proceed to the pharmacy counter where a pharmacist will assist you with acquiring [medication]. Have a nice day!"
→ If in_stock=False: "[Medication] is currently out of stock at this branch."

For Rx medication:
→ Verify prescription first
→ If valid + in stock: Route to pharmacist counter
→ If no valid prescription: "No valid prescription on file." → STOP

SCENARIO 5: Medication Not Found
→ get_medication_by_name returns None or {"error": "Medication not found"}
→ Respond: "I don't have information about [medication name]."
→ STOP (do not suggest alternatives)
</workflow_scenarios>

<critical_reminders>
1. Your role is purely informational - you are NOT a medical professional
2. When in doubt, refuse and suggest consulting a healthcare professional
3. Never proactively offer to check stock, prescriptions, or suggest next steps
4. Distinguish between availability check ("Is it available?") and purchase request ("I want to buy it")
5. After refusing a medical advice request, STOP immediately - do not continue with other topics
</critical_reminders>
"""

# Function to handle streaming chat responses
def stream_chat(messages):
    """
    Generator that yields SSE-formatted events.
    Handles tool calls automatically and continues streaming.
    """
    # Policy check on latest user message 
    if messages:    # check if there are messages to process
        last_msg = messages[-1]
        if last_msg.get("role") == "user":
            # Determine if the user's last message violates the policy
            is_violation, refusal = check_user_policy_violation(last_msg.get("content", ""))
            if is_violation:
                # Return refusal message without calling OpenAI
                yield f'data: {json.dumps({"type": "token", "content": refusal})}\n\n'
                yield f'data: {json.dumps({"type": "done"})}\n\n'
                return
    
    # Combine system prompt to establish context for the model before user messages
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    
    # Continuously stream responses
    while True:
        try:
            # Request the model's streamed response based on the full messages
            response = client.chat.completions.create(
                model=MODEL,
                messages=full_messages,
                tools=TOOLS,
                stream=True
            )
        except Exception as e:            
            yield f'data: {json.dumps({"type": "error", "content": f"API error: {str(e)}"})}\n\n'            
            yield f'data: {json.dumps({"type": "done"})}\n\n'            
            return
        
        # Initialize a buffer for accumulating the model's responses as they are streamed 
        accumulated_response = "" 
        # Initialize a list for requested tool calls
        tool_calls = []  
        # Process each chunk of the response
        current_tool_idx = -1
        for chunk in response:
            # Get the delta (change) from the response chunk
            delta = chunk.choices[0].delta if chunk.choices else None
            if not delta:
                continue
            # Handle content chunks
            if delta.content:
                accumulated_response += delta.content
                yield f'data: {json.dumps({"type": "token", "content": delta.content})}\n\n'
            
            # Handle tool calls
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    if tc.index != current_tool_idx:
                        # Update the current tool index and add the new tool call
                        current_tool_idx = tc.index
                        tool_calls.append({
                            "id": tc.id or "",
                            "name": tc.function.name or "",
                            "arguments": tc.function.arguments or ""
                        })
                    else:
                        # If it's the same tool call, update the existing information based on the new data
                        if tc.id:
                            tool_calls[current_tool_idx]["id"] = tc.id
                        if tc.function and tc.function.name:
                            tool_calls[current_tool_idx]["name"] = tc.function.name
                        if tc.function and tc.function.arguments:
                            tool_calls[current_tool_idx]["arguments"] += tc.function.arguments
        
        # Check if medication not found - clear irrelevant context       
        if "I don't have information" in accumulated_response or "אין לי מידע" in accumulated_response:            
            # # Keep only system prompt and last user message            
            full_messages = [                
                {"role": "system", "content": SYSTEM_PROMPT},                
                messages[-1] if messages else {}            
            ]

        # Check the finish reason of the response
        finish_reason = chunk.choices[0].finish_reason if chunk.choices else None
        
        # End the stream if the finish reason is not related to tool calls
        if finish_reason != "tool_calls" or not tool_calls:
            yield f'data: {json.dumps({"type": "done"})}\n\n'
            return
        
        # Create an assistant message with the collected content and tool call details
        assistant_msg = {"role": "assistant", "content": accumulated_response or None, "tool_calls": []}
        for tc in tool_calls:
            assistant_msg["tool_calls"].append({
                "id": tc["id"],
                "type": "function",
                "function": {"name": tc["name"], "arguments": tc["arguments"]}
            })
        full_messages.append(assistant_msg)
        
        # Execute the tools that were requested
        for tc in tool_calls:
            try:
                # Load the tool call arguments from JSON
                args = json.loads(tc["arguments"])
            except json.JSONDecodeError:
                args = {}
            
            # Execute the tool and get the result
            result = execute_tool(tc["name"], args)
            # Convert the result to a string for output
            result_str = tool_result_to_str(result)
            
            # Yield the tool call result
            yield f'data: {json.dumps({"type": "tool_call", "name": tc["name"], "input": args, "output": result})}\n\n'
            
            # Append the tool result to full messages
            full_messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": result_str
            })