
# Pharmacy Agent - Tools Documentation

This document describes the three tools available to the pharmacy agent.

---

## Tool 1: get_medication_by_name

### Name and Purpose
**Name:** `get_medication_by_name`  
**Purpose:** Retrieve medication information by name (English or Hebrew)

### Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `medication_name` | string | Yes | Medication name (supports partial matching, case-insensitive) |

**Example inputs:**
- `"Ibuprofen"`
- `"איבופרופן"`
- `"ibup"` (partial match)

### Output Schema

**Success:**
```json
{
  "id": 1,
  "name": "Ibuprofen",
  "name_he": "איבופרופן",
  "description": "Nonsteroidal anti-inflammatory drug (NSAID) for pain and fever",
  "description_he": "תרופה נוגדת דלקת לא סטרואידית לכאב וחום",
  "active_ingredient": "Ibuprofen",
  "dosage_form": "Tablet",
  "standard_dosage": "200-400mg every 4-6 hours",
  "requires_prescription": false,
  "price": 12.90
}
```

**Not Found:**
```json
{
  "error": "Medication not found"
}
```

Or returns `None` if medication doesn't exist.

### Error Handling

| Error Case | Return Value | Agent Response |
|------------|--------------|----------------|
| Medication not found | `None` or `{"error": "Medication not found"}` | "I don't have information about [medication name]" |
| Empty input | `None` | "Please provide a medication name" |

### Fallback Behavior

- If medication not found → Agent stops and informs user
- No alternative medications suggested (policy violation)
- Agent does NOT search by symptoms or conditions

### Example

**Request:**
```json
{
  "medication_name": "Ibuprofen"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Ibuprofen",
  "name_he": "איבופרופן",
  "description": "Nonsteroidal anti-inflammatory drug (NSAID) for pain and fever",
  "active_ingredient": "Ibuprofen",
  "requires_prescription": false,
  "price": 12.90
}
```

**Agent Output:**  
_"Ibuprofen is a nonsteroidal anti-inflammatory drug (NSAID) used for pain and fever. The standard dosage is 200-400mg every 4-6 hours. It does not require a prescription and costs ₪12.90."_

---

## Tool 2: check_inventory

### Name and Purpose
**Name:** `check_inventory`  
**Purpose:** Check if a medication is currently in stock

### Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `medication_id` | integer | Yes | Medication ID (from `get_medication_by_name` result) |

**Example inputs:**
- `1` (Ibuprofen)
- `2` (Amoxicillin)

### Output Schema

**Success:**
```json
{
  "medication_id": 1,
  "name": "Ibuprofen",
  "stock_quantity": 150,
  "in_stock": true,
  "price": 12.90
}
```

**Not Found:**
```json
{
  "error": "Medication not found"
}
```

### Error Handling

| Error Case | Return Value | Agent Response |
|------------|--------------|----------------|
| Invalid medication_id | `None` | "I couldn't verify stock for that medication" |
| Missing parameter | `{"error": "medication_id is required"}` | "I need a medication ID to check stock" |

### Fallback Behavior

- If medication out of stock → Agent informs user, does NOT suggest alternatives
- If invalid ID → Agent asks user to clarify medication name
- No cross-branch stock checking (only current branch)

### Example

**Request:**
```json
{
  "medication_id": 5
}
```

**Response:**
```json
{
  "medication_id": 5,
  "name": "Loratadine",
  "stock_quantity": 0,
  "in_stock": false,
  "price": 15.90
}
```

**Agent Output:**  
_"Loratadine is currently out of stock at this branch."_

---

## Tool 3: verify_user_prescription

### Name and Purpose
**Name:** `verify_user_prescription`  
**Purpose:** Verify if a user has a valid prescription for a specific medication

### Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | User's 9-digit Israeli ID number |
| `medication_name` | string | Yes | Medication name (English or Hebrew) |

**Example inputs:**
- `user_id`: `"123456789"`
- `medication_name`: `"Amoxicillin"` or `"אמוקסיצילין"`

### Output Schema

**Valid Prescription:**
```json
{
  "has_prescription": true,
  "medication": "Amoxicillin",
  "dosage": "500mg 3 times daily",
  "refills_remaining": 2,
  "expiry_date": "2026-06-15"
}
```

**No Valid Prescription:**
```json
{
  "has_prescription": false,
  "medication": "Amoxicillin"
}
```

**User Not Found:**
```json
{
  "has_prescription": false,
  "error": "User not found"
}
```

**Medication Not Found:**
```json
{
  "has_prescription": false,
  "error": "Medication not found"
}
```

### Error Handling

| Error Case | Return Value | Agent Response |
|------------|--------------|----------------|
| User not found | `{"has_prescription": false, "error": "User not found"}` | "I couldn't verify your prescription information" |
| Medication not found | `{"has_prescription": false, "error": "Medication not found"}` | "I don't have information about that medication" |
| No prescription | `{"has_prescription": false}` | "[Medication] requires a valid prescription. There is no valid prescription on file." |
| Expired prescription | `{"has_prescription": false}` | Same as "No prescription" |

### Fallback Behavior

- If no valid prescription → Agent stops, does NOT provide medication
- If user not found → Agent asks user to verify ID number
- Expired prescriptions are treated as invalid (returns `has_prescription: false`)
- Agent never bypasses prescription requirements

### Example

**Request:**
```json
{
  "user_id": "123456789",
  "medication_name": "Amoxicillin"
}
```

**Response:**
```json
{
  "has_prescription": true,
  "medication": "Amoxicillin",
  "dosage": "500mg 3 times daily",
  "refills_remaining": 2,
  "expiry_date": "2026-06-15"
}
```

**Agent Output:**  
_"You have a valid prescription for Amoxicillin with a dosage of 500mg 3 times daily. You have 2 refills remaining, and the prescription is valid until June 15, 2026."_

---

## Tool Execution Summary

### Correct Tool Calling Sequence

**Non-Prescription Medication:**
```
1. get_medication_by_name("Ibuprofen")
   → requires_prescription: false
2. If user asks: check_inventory(medication_id)
```

**Prescription-Required Medication:**
```
1. get_medication_by_name("Amoxicillin")
   → requires_prescription: true
2. verify_user_prescription(user_id, "Amoxicillin")
   → has_prescription: true/false
3. If valid prescription: check_inventory(medication_id)
```

### Tools NOT Called When:
- User describes symptoms (medical advice - policy violation)
- User asks for recommendations (medical advice - policy violation)
- User requests medication alternatives (medical advice - policy violation)

---

## Data Source

All tools retrieve data from: `backend/synthetic_data.py`

**Available medications:**
- Ibuprofen (requires_prescription: false, in stock)
- Amoxicillin (requires_prescription: true, in stock)
- Omeprazole (requires_prescription: false, in stock)
- Metformin (requires_prescription: true, in stock)
- Loratadine (requires_prescription: false, **out of stock**)
```