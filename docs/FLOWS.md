# 📋 **FLOWS.MD**

```markdown
# Multi-Step Conversation Flows

This document describes the main conversation flows supported by the Pharmacy Agent.

---

## Flow 1: Basic Medication Inquiry

**Purpose:** Customer asks about an over-the-counter medication

**Steps:**
1. User asks: "Do you have Ibuprofen?"
2. Agent calls `get_medication_by_name` → Provides medication info
3. User asks: "How much does it cost?"
4. Agent responds with price from retrieved data
5. User asks: "Is it in stock?"
6. Agent calls `check_inventory` → Reports availability

**Tools Used:** `get_medication_by_name`, `check_inventory`

**Expected Outcome:** Customer receives medication information, price, and stock status

---

## Flow 2: Prescription Verification

**Purpose:** Customer needs a prescription-required medication

**Steps:**
1. User asks: "I need Amoxicillin"
2. Agent calls `get_medication_by_name` → Identifies prescription requirement
3. Agent asks: "May I have your ID number to verify your prescription?"
4. User provides: "123456789"
5. Agent calls `verify_user_prescription` → Validates prescription
6. Agent confirms prescription details and availability

**Tools Used:** `get_medication_by_name`, `verify_user_prescription`

**Expected Outcome:** Prescription is verified and medication can be dispensed (or denied if no valid prescription)

---

## Flow 3: Out of Stock + Medical Advice Refusal

**Purpose:** Demonstrates policy enforcement when customer asks for alternatives

**Steps:**
1. User asks: "Do you have Loratadine?"
2. Agent calls `get_medication_by_name` and `check_inventory` → Reports out of stock
3. User asks: "What should I take instead for allergies?"
4. Agent detects policy violation → Refuses medical advice
5. Agent suggests: "Please consult with a doctor or pharmacist"

**Tools Used:** `get_medication_by_name`, `check_inventory`

**Policy Enforcement:** Agent refuses to recommend alternative medications

**Expected Outcome:** Customer is informed medication is unavailable, but agent does NOT provide medical recommendations

---

## Key Features Demonstrated

- Multi-turn conversations (2-5 turns per flow)
- Context retention across turns
- Tool integration
- Bilingual support (English/Hebrew)
- Policy enforcement (no medical advice)
- Error handling (out of stock, no prescription)

---

## Notes

- All flows use synthetic data from `backend/synthetic_data.py`
- Pre-check policy violations are detected by `backend/policy.py` 
- Tool functions are defined in `backend/tools.py`
- End-to-end tests in `tests/test_flows.py` validate these scenarios
```