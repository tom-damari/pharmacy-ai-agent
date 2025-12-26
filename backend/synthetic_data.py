from datetime import date

MEDICATIONS = [
    {
        "id": 1,
        "name": "Ibuprofen",
        "name_he": "איבופרופן",
        "description": "Nonsteroidal anti-inflammatory drug (NSAID) for pain and fever",
        "description_he": "תרופה נוגדת דלקת לא סטרואידית לכאב וחום",
        "active_ingredient": "Ibuprofen",
        "dosage_form": "Tablet",
        "standard_dosage": "200-400mg every 4-6 hours",
        "requires_prescription": False,
        "stock_quantity": 150,
        "price": 12.90
    },
    {
        "id": 2,
        "name": "Amoxicillin",
        "name_he": "אמוקסיצילין",
        "description": "Antibiotic used to treat bacterial infections",
        "description_he": "אנטיביוטיקה לטיפול בזיהומים חיידקיים",
        "active_ingredient": "Amoxicillin",
        "dosage_form": "Capsule",
        "standard_dosage": "500mg every 8 hours",
        "requires_prescription": True,
        "stock_quantity": 45,
        "price": 28.50
    },
    {
        "id": 3,
        "name": "Omeprazole",
        "name_he": "אומפרזול",
        "description": "Proton pump inhibitor for acid reflux and ulcers",
        "description_he": "מעכב משאבת פרוטונים לרפלוקס וכיבים",
        "active_ingredient": "Omeprazole",
        "dosage_form": "Capsule",
        "standard_dosage": "20mg once daily",
        "requires_prescription": False,
        "stock_quantity": 80,
        "price": 19.90
    },
    {
        "id": 4,
        "name": "Metformin",
        "name_he": "מטפורמין",
        "description": "Oral diabetes medication that helps control blood sugar",
        "description_he": "תרופה פומית לסוכרת לשליטה ברמת הסוכר בדם",
        "active_ingredient": "Metformin Hydrochloride",
        "dosage_form": "Tablet",
        "standard_dosage": "500mg twice daily",
        "requires_prescription": True,
        "stock_quantity": 200,
        "price": 8.50
    },
    {
        "id": 5,
        "name": "Loratadine",
        "name_he": "לוראטדין",
        "description": "Antihistamine for allergy relief",
        "description_he": "אנטיהיסטמין להקלה באלרגיות",
        "active_ingredient": "Loratadine",
        "dosage_form": "Tablet",
        "standard_dosage": "10mg once daily",
        "requires_prescription": False,
        "stock_quantity": 0,
        "price": 15.90
    },
]

USERS = [
    {"id": 1, "id_number": "123456789", "first_name": "David", "last_name": "Cohen", "phone": "050-1234567", "date_of_birth": "1985-03-15"},
    {"id": 2, "id_number": "234567890", "first_name": "Sarah", "last_name": "Levi", "phone": "052-2345678", "date_of_birth": "1990-07-22"},
    {"id": 3, "id_number": "345678901", "first_name": "Michael", "last_name": "Mizrachi", "phone": "054-3456789", "date_of_birth": "1978-11-08"},
    {"id": 4, "id_number": "456789012", "first_name": "Rachel", "last_name": "Goldberg", "phone": "053-4567890", "date_of_birth": "1995-01-30"},
    {"id": 5, "id_number": "567890123", "first_name": "Yossi", "last_name": "Peretz", "phone": "050-5678901", "date_of_birth": "1982-09-12"},
    {"id": 6, "id_number": "678901234", "first_name": "Miriam", "last_name": "Azulay", "phone": "052-6789012", "date_of_birth": "1988-04-25"},
    {"id": 7, "id_number": "789012345", "first_name": "Daniel", "last_name": "Shapiro", "phone": "054-7890123", "date_of_birth": "1972-12-03"},
    {"id": 8, "id_number": "890123456", "first_name": "Noa", "last_name": "Ben-David", "phone": "053-8901234", "date_of_birth": "2000-06-18"},
    {"id": 9, "id_number": "901234567", "first_name": "Eli", "last_name": "Katz", "phone": "050-9012345", "date_of_birth": "1965-08-07"},
    {"id": 10, "id_number": "012345678", "first_name": "Tamar", "last_name": "Friedman", "phone": "052-0123456", "date_of_birth": "1992-02-14"},
]

PRESCRIPTIONS = [
    {"id": 1, "user_id": 1, "medication_id": 2, "dosage": "500mg 3 times daily", "refills_remaining": 2, "expiry_date": "2026-06-15"},
    {"id": 2, "user_id": 3, "medication_id": 4, "dosage": "500mg twice daily", "refills_remaining": 5, "expiry_date": "2025-12-31"},
    {"id": 3, "user_id": 5, "medication_id": 2, "dosage": "250mg 3 times daily", "refills_remaining": 0, "expiry_date": "2026-01-01"},
    {"id": 4, "user_id": 6, "medication_id": 4, "dosage": "1000mg once daily", "refills_remaining": 3, "expiry_date": "2024-09-30"},
    {"id": 5, "user_id": 9, "medication_id": 2, "dosage": "500mg 3 times daily", "refills_remaining": 1, "expiry_date": "2026-08-20"},
    {"id": 6, "user_id": 9, "medication_id": 4, "dosage": "850mg twice daily", "refills_remaining": 4, "expiry_date": "2026-11-15"},
]


def get_medication_by_name(name):
    """Find medication by name (EN/HE, case-insensitive, partial match)."""
    name_lower = name.lower()
    for med in MEDICATIONS:
        if name_lower in med["name"].lower() or name_lower in med["name_he"]:
            return med
    return None


def check_inventory(medication_id):
    """Check stock for a medication by ID."""
    for med in MEDICATIONS:
        if med["id"] == medication_id:
            return {
                "medication_id": med["id"],
                "name": med["name"],
                "stock_quantity": med["stock_quantity"],
                "in_stock": med["stock_quantity"] > 0,
                "price": med["price"]
            }
    return None


def get_user_by_id(user_id_number):
    """Find user by ID number."""
    for user in USERS:
        if user["id_number"] == user_id_number:
            return user
    return None


def get_user_prescriptions(user_id_number):
    """Get all active prescriptions for a user."""
    user = get_user_by_id(user_id_number)
    if not user:
        return []
    
    today = date.today().isoformat()
    results = []
    for rx in PRESCRIPTIONS:
        if rx["user_id"] == user["id"] and rx["expiry_date"] >= today:
            med = next((m for m in MEDICATIONS if m["id"] == rx["medication_id"]), None)
            if med:
                results.append({
                    "prescription_id": rx["id"],
                    "medication_name": med["name"],
                    "medication_name_he": med["name_he"],
                    "dosage": rx["dosage"],
                    "refills_remaining": rx["refills_remaining"],
                    "expiry_date": rx["expiry_date"]
                })
    return results


def verify_user_prescription(user_id_number, medication_name):
    """Check if user has valid prescription for a medication."""
    user = get_user_by_id(user_id_number)
    if not user:
        return {"has_prescription": False, "error": "User not found"}
    
    med = get_medication_by_name(medication_name)
    if not med:
        return {"has_prescription": False, "error": "Medication not found"}
    
    today = date.today().isoformat()
    for rx in PRESCRIPTIONS:
        if rx["user_id"] == user["id"] and rx["medication_id"] == med["id"] and rx["expiry_date"] >= today:
            return {
                "has_prescription": True,
                "medication": med["name"],
                "dosage": rx["dosage"],
                "refills_remaining": rx["refills_remaining"],
                "expiry_date": rx["expiry_date"]
            }
    
    return {"has_prescription": False, "medication": med["name"]}