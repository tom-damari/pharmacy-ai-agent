# 📑 **Evaluation Plan for Pharmacy AI Agent**

## **1. Overview**

This evaluation plan outlines the methodology and criteria used to assess the performance of the Pharmacy AI Agent through End-to-End (E2E) testing. The tests simulate real user interactions, validating the capabilities and functionalities of the agent in various customer journey scenarios.

## **2. Purpose of Evaluation**

The primary purpose of this evaluation is to ensure that the Pharmacy AI Agent:
- Provides accurate and reliable information about medications.
- Validates prescriptions appropriately.
- Adheres to policies regarding medical advice.
- Handles language switching seamlessly between English and Hebrew.
- Manages edge cases gracefully, such as unavailable medications.

## **3. Testing Framework**

- **Framework Used:** `pytest`
- **Test File:** `tests/test_flows.py`
- **Number of Tests:** 17
- **Test Type:** End-to-End tests leveraging real OpenAI API calls.

## **4. Test Structure**

The evaluation consists of three main flows, each with specific test cases:

### **Flow 1: Basic Medication Information**
- **Number of Tests:** 7
- **Objective:** Validate the agent's ability to provide information about medications, including availability and pricing.
- **Key Tests:**
  - Basic inquiries about medication names.
  - Price queries in Hebrew and English.
  - Edge case for medications not found.

### **Flow 2: Prescription Verification Journey**
- **Number of Tests:** 6
- **Objective:** Assess the agent’s capability to handle prescription-required medications and verify user prescriptions.
- **Key Tests:**
  - Valid prescription verification.
  - Handling cases with no prescriptions.
  - Expired prescription scenarios.

### **Flow 3: Out of Stock Handling + Policy Enforcement**
- **Number of Tests:** 4
- **Objective:** Test the agent’s response to out-of-stock situations and its policy enforcement regarding medical advice.
- **Key Tests:**
  - Out-of-stock inquiries.
  - Refusal of medical advice requests.
  - Allowable stock inquiries without policy violations.

## **5. Language Coverage**

- **English:** Approximately 35%
- **Hebrew:** Approximately 30%
- **Mixed Language Switching:** Approximately 35%

## **6. Evaluation Criteria**

### **6.1 Functional Accuracy**
- Validate that the agent correctly uses tools for medication inquiries, prescription validation, and inventory checks.
- Ensure accurate responses are provided based on synthetic data.

### **6.2 Policy Compliance**
- Confirm that the agent refuses to provide medical advice as per the established policies.
- Ensure proper handling of policy violations in user inquiries.

### **6.3 Performance Metrics**
- **Pass Rate:** 100% (All tests should pass)
- **Response Time:** Measure the time taken for each test to ensure acceptable performance under load.

### **6.4 User Experience**
- Evaluate the seamlessness of language switching between English and Hebrew.
- Assess the clarity and helpfulness of the agent's responses.

## **7. Execution of Tests**

To run the tests, use the following command:

```bash
pytest tests/test_flows.py -v -s
```

This command will execute all defined tests, providing detailed output on the results of each test case.

## **8. Conclusion**

The evaluation plan is designed to ensure the Pharmacy AI Agent meets the functional and performance standards necessary for effective operation in a real-world pharmacy environment. Each flow and test case has been crafted to simulate realistic interactions, providing comprehensive coverage for the agent's capabilities.