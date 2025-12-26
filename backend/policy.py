"""
Policy enforcement for the pharmacy agent.
Blocks medical advice, diagnosis, and treatment recommendation requests.
"""

import re

# === ENGLISH VIOLATION PATTERNS ===
INVALID_REQUEST_PATTERNS_EN = [
    # === Direct advice/recommendation keywords ===
    r"\b(recommend|suggestion|suggest|advice|advise|prescribe)\b",
    r"\b(recommendation|proposal|opinion)\b",
    
    # === Evaluation patterns ===
    r"\b(good|effective|safe|best|better|okay|suitable|appropriate)\s+(for|with|to\s+treat)\b",
    r"\b(works|work|help|helps|effective)\s+(for|with|against)\b",
    r"\bis\s+\w+\s+(good|safe|effective|okay|suitable)\s+for\b",
    r"\bwill\s+\w+\s+(help|work|cure|fix|treat)\b",
    
    # === "What do you" patterns ===
    r"\bwhat\s+do\s+you\s+(recommend|suggest|think|advise|propose)\b",
    r"\bdo\s+you\s+(recommend|suggest|think\s+i\s+should|advise)\b",
    
    # === Action patterns ===
    r"\b(should|can|could|may|would)\s+(i|we)\s+(take|use|try|stop|continue)\b",
    r"\bwhat\s+(should|can|could|may)\s+i\b",
    r"\bwhat\s+to\s+take\b",
    r"\bcan\s+i\s+take\s+\w+\s+for\b",
    
    # === Medication selection ===
    r"\bwhat\s+(medication|medicine|drug|pill|tablet|remedy)s?\s+(for|should)\b",
    r"\bwhich\s+(medication|medicine|drug|pill|remedy)\b",
    
    # === Dosage patterns ===
    r"\bhow\s+(much|many)\s+.*(to\s+take|should\s+i\s+take)\b",
    r"\btoo\s+much\b",
    r"\bis\s+this\s+enough\b",
    r"\benough\s+(medication|medicine|dose)\b",
    r"\b(increase|decrease|change|adjust|reduce|raise)\s+.*?(dose|dosage|medication|amount)\b",
    r"\bshould\s+i\s+(increase|decrease|stop|continue|change)\b",
    r"\bcan\s+i\s+(increase|decrease|stop|change|continue)\b",
    r"\bstop\s+taking\b",
    
    # === Diagnosis patterns ===
    r"\b(diagnose|diagnosis)\b",
    r"\bwhat'?s\s+wrong\b",
    r"\bwhat\s+do\s+i\s+have\b",
    r"\bwhat'?s\s+wrong\s+with\s+me\b",
    r"\bam\s+i\s+(sick|ill|okay|fine)\b",
    r"\bis\s+this\s+(serious|dangerous|urgent|bad|normal|safe)\b",
    r"\bdo\s+i\s+need\s+(to\s+see\s+)?(a\s+)?(doctor|physician)\b",
    
    # === Treatment patterns ===
    r"\bhow\s+to\s+(treat|cure|fix|heal)\b",
    r"\b(treatment|cure|remedy)\s+for\b",
]

# === HEBREW VIOLATION PATTERNS ===
INVALID_REQUEST_PATTERNS_HE = [
    # === Direct advice/recommendation keywords ===
    r"\b(ממליץ|ממליצה|המלץ|המליצי|תמליץ|תמליצי|המלצה|להמליץ)\b",
    r"\b(מציע|מציעה|תציע|תציעי|להציע|ה?הצעה)\b",
    r"\b(ייעוץ|לייעץ|מייעץ|מייעצת)\b",
    r"\b(מספק|מספקת|לספק)\b",  
    r"\bחושב\s+ש(אני\s+)?(צריך|צריכה)\b",
    r"\b(דעה|דעתך)\b",  
    
    # === Evaluation patterns ===
    r"\b(טוב|יעיל|בטוח|עדיף|מתאים|מומלץ)\b",
    r"\b(עוזר|יעזור|עובד|יעבוד|מסייע)\s+(ל|עם|נגד)",
    r"\bהכי\s+(טוב|יעיל|בטוח|מתאים)\b",
    
    # === "What do you" patterns ===
    r"\bמה\s+(אתה|את)\s+(ממליץ|ממליצה|חושב|חושבת|מציע|מציעה)\b",
    
    # === Action patterns ===
    r"\bמה\s+(לקחת|ליטול|להשתמש|לעשות|צריך|כדאי)\b",
    r"\bהאם\s+(לקחת|ליטול|להשתמש|כדאי)\b",
    r"\bהאם\s+(אני\s+)?(צריך|צריכה)\s+(לקחת|ליטול)\b",
    r"\b(כדאי|שווה)\s+לקחת\b",
    r"\bהאם\s+(להמשיך|להפסיק)\b",
    
    # === Medication selection ===
    r"\b(איזה|איזו|מה)\s+(תרופה|תכשיר|כדור|תרופות)\b",
    r"\bתרופה\s+ל",
    r"\bמה\s+הכי\s+(טוב|יעיל)\b",  
    
    # === Dosage patterns ===
    r"\bכמה\s+(לקחת|ליטול|מינון|כמות)\b",
    r"\b(יותר\s+מדי|הרבה\s+מדי)\b",
    r"\b(מספיק|די)\b",
    r"\b(להגדיל|להקטין|לשנות|להפסיק|להמשיך|להוריד|להעלות)\b",
    r"\bהאם\s+(להגדיל|להקטין|להפסיק|להמשיך|לשנות)\b",
    
    # === Diagnosis patterns ===
    r"\b(אבחנה|לאבחן|אבחון)\b",
    r"\bמה\s+(הבעיה|יש\s+לי|קורה\s+לי|קרה\s+לי)\b",
    r"\bמה\s+(האבחנה|הבעיה\s+שלי)\b",
    r"\bהאם\s+אני\s+(חולה|בסדר|תקין)\b",
    r"\bזה\s+(מסוכן|רציני|דחוף|רע|נורמלי|בסדר)\b",
    r"\bהאם\s+(צריך|כדאי)\s+רופא\b",
    
    # === Treatment patterns ===
    r"\bאיך\s+(לטפל|לרפא|להתמודד|לטפל)\b",
    r"\bמה\s+(ה)?(טיפול|ריפוי|פתרון)\s+ל",
    
    # === Common colloquial patterns ===
    r"\bמה\s+עושים\b",
    r"\b(שווה|כדאי)\s+לקחת\b",
    r"\bמה\s+תגיד\b", 
]


# Strict refusal message with no alternative offer for user violation requests in English and Hebrew 
REFUSAL_RESPONSE_EN = (
    "I'm sorry, I cannot recommend specific treatments or medications. "
    "For personalized advice, please consult a doctor or pharmacist."
)
REFUSAL_RESPONSE_HE = (
    "מצטער, אינני יכול להמליץ על טיפול או תרופה ספציפית. "
    "להמלצה מותאמת אישית כדאי לפנות לרופא או לרוקח."    
)

# Functions to guide agent if searching for hebrew violation patterns is needed
def is_hebrew(text):
    """Check if input text contains Hebrew characters."""
    return bool(re.search(r'[\u0590-\u05FF]', text))


# Functions to detarmine if agent should excute refusal message (user violation occured) 
def check_user_policy_violation(user_message):
    """
    Check if user message violates medical advice policy.
    Returns (is_violation, refusal_text) tuple.
    """
    msg_lower = user_message.lower()
    
    # Check Hebrew patterns if message contains Hebrew
    if is_hebrew(user_message):
        for pattern in INVALID_REQUEST_PATTERNS_HE:
            if re.search(pattern, user_message):
                return True, REFUSAL_RESPONSE_HE
    
    # Check English patterns
    for pattern in INVALID_REQUEST_PATTERNS_EN:
        if re.search(pattern, msg_lower):
            return True, REFUSAL_RESPONSE_EN
        
    return False, None


# Function for matching language of refusal response to user's input
def get_refusal_text(user_message):
    """Get refusal text in appropriate language."""
    return REFUSAL_RESPONSE_HE if is_hebrew(user_message) else REFUSAL_RESPONSE_EN


# # Indicators for model's refusal response in English and Hebrew
# REFUSAL_INDICATOR_EN = (
#         "cannot recommend",        
#         "cannot provide",        
#         "consult a doctor",    
#         "consult a pharmacist",    
# )
# REFUSAL_INDICATOR_HE = (
#         "אינני יכול להמליץ",        
#         "לא יכול להמליץ",        
#         "אינני מוסמך",        
#         "פנה לרופא",    
#         "לפנות לרופא",    
#         "פנה לרוקח",    
#         "כדאי לפנות",    
# )

# # Function to determine if agent should stop due to user violation
# def should_stop_after_refusal(assistant_response):    
#     """    
#     Check if assistant refused due to policy and should stop completely.    
#     assistant_response: The accumulated assistant response text
#     Returns: True if this is a policy refusal and agent should stop
#     """    
#     response_lower = assistant_response.lower()   

#     # Check Hebrew indicators if response contains Hebrew
#     if is_hebrew(assistant_response):
#         return any(indicator in response_lower for indicator in REFUSAL_INDICATOR_HE)
        
#     # Check English indicators
#     return any(indicator in response_lower for indicator in REFUSAL_INDICATOR_EN)