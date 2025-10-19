
from flask import Flask, request, jsonify, render_template
from rapidfuzz import process, fuzz

app = Flask(__name__)   # ✅ This defines the Flask app

faq = {
    "appointments": {
        "questions": [
            "How do I book an appointment?", "Schedule a doctor visit",
            "Can I make an appointment online?", "Booking doctor consultation",
            "Doctor appointment timings", "Reschedule appointment",
            "Cancel my appointment", "Book an appointment for next week"
        ],
        "answer": (
            "📅 To book an appointment, visit our hospital website or call **123-456-7890**. "
            "Appointments can also be made directly at the reception desk. "
            "If you want to reschedule or cancel, log in to the patient portal or call our Appointment Desk. "
            "We recommend booking 2–3 days in advance for best availability."
        )
    },
    "lab_tests": {
        "questions": [
            "What lab tests are available?", "lab tests", "lab test info",
            "Schedule a lab test", "Lab test results online", "Pathology services",
            "X-ray and MRI availability", "How to get lab reports?",
            "Test preparation guidelines"
        ],
        "answer": (
            "🧪 We provide a wide range of diagnostic services including blood tests, "
            "urine analysis, X-ray, MRI, CT scans, and ultrasound. "
            "Results are uploaded to the patient portal within 24–48 hours. "
            "Some tests require fasting for 8–12 hours (e.g., fasting blood sugar). "
            "Reports can also be collected from the lab helpdesk."
        )
    },
    "doctors": {
        "questions": [
            "Which doctors are available?", "List of specialists",
            "I want to see a cardiologist", "Doctor schedule",
            "Consultation with pediatrician", "Orthopedic specialist timings",
            "Available surgeons this week", "Doctor consultation hours"
        ],
        "answer": (
            "👨‍⚕️ Our hospital has cardiologists, pediatricians, orthopedics, ENT specialists, "
            "gynecologists, neurologists, and surgeons available. "
            "Doctor schedules are regularly updated on our website under the 'Doctors' section. "
            "For urgent cases, please call the reception at **123-456-7890**."
        )
    },
    "billing": {
        "questions": [
            "billing",
            "How do I pay my bill?", "Billing procedure", "Payment options",
            "Do you accept insurance?", "Is EMI available?"
        ],
        "answer": (
            "💳 Bills can be paid at the hospital counter or online via debit/credit card. "
            "We accept major insurance providers—check with our insurance desk for coverage details. "
            "For high-value procedures, EMI options are available through partner banks."
        )
    },
    "emergency": {
        "questions": [
            "Emergency contact number", "Accident case help", "Emergency department",
            "What to do in medical emergency?", "24/7 ambulance service"
        ],
        "answer": (
            "🚨 In case of emergency, please call our 24/7 helpline **111-222-333**. "
            "Our Emergency Department is open round-the-clock and equipped with ICUs, trauma care, "
            "and ambulance services. Critical patients are given immediate priority."
        )
    },
    "pharmacy": {
        "questions": [
            "Hospital pharmacy location", "Buy medicines", "Do you have 24/7 pharmacy?",
            "Can I get prescribed medicines here?", "Does pharmacy offer home delivery?"
        ],
        "answer": (
            "💊 Our hospital pharmacy is located on the ground floor, open 24/7. "
            "You can purchase prescribed medicines directly or through our online portal. "
            "We also provide home delivery for patients living within 10 km of the hospital."
        )
    },
    "insurance": {
        "questions": [
            "insurance",
            "Do you accept health insurance?", "Which insurance companies are accepted?",
            "Insurance claim process", "How to claim my insurance?"
        ],
        "answer": (
            "📑 Yes, we accept most leading insurance providers. "
            "To claim insurance, visit our Insurance Helpdesk with your insurance card and patient ID. "
            "We also offer cashless facilities for selected insurers. "
            "For detailed assistance, email **insurance@citycare.com**."
        )
    },
    "surgery": {
        "questions": [
            "What surgeries are available?", "How to prepare for surgery?",
            "Surgery recovery time", "Post-surgery care", "Surgeon availability"
        ],
        "answer": (
            "🔪 We perform general, orthopedic, cardiac, gynecological, and neurosurgeries. "
            "Pre-surgery instructions depend on the procedure (e.g., fasting, medication stop). "
            "Recovery times vary—minor surgeries may need 2–3 days, major surgeries may need weeks. "
            "Post-surgery care is provided through follow-up visits and rehabilitation programs."
        )
    },
    "visitor_guidelines": {
        "questions": [
            "What are the visiting hours?", "Can children visit patients?",
            "Visiting ICU patients", "Visitor policy"
        ],
        "answer": (
            "👥 Visiting hours are from **5 pM to 8 PM**. "
            "Children below 12 are generally not allowed inside ICUs for safety reasons. "
            "Only two visitors are allowed at a time in general wards. "
            "In ICUs, visits are restricted to immediate family for short durations."
        )
    },
    "general_info": {
        "questions": [
            "Hospital location", "Contact number", "Visiting address",
            "Emergency helpline", "What services are offered?"
        ],
        "answer": (
            "🏥 CityCare Hospital is located at **123 Main Street, Downtown**. "
            "For help, call **123-456-7890**. We provide services such as emergency care, "
            "surgery, pharmacy, diagnostic labs, rehabilitation, and wellness programs."
        )
    },
    "lab_test": {
        "questions": ["lab tests", "blood test", "urine test", "x-ray", "mri", "ct scan"],
        "answer": "🧪 We provide diagnostic services including blood tests, urine analysis, X-ray, MRI, CT scans, and ultrasound. Reports are usually available within 24 hours. For urgent reports, please contact the reception."
    }
}


# ✅ Greeting message (automatic at start)
greeting_message = (
"👋 Welcome to **CityCare Hospital Chatbot!**<br>"
"I can assist you with appointments, doctors, lab tests, emergencies, billing, "
"pharmacy, insurance, surgeries, and more.<br>"
"Please type your question (e.g., *What are the visiting hours?*)."
)

def get_best_answer(user_input):
    user_input = user_input.lower().strip()

    # ✅ Step 1: Simple greetings
    greetings = ["hello", "hi", "hey", "good morning", "good evening", "assalamualaikum", "salam"]
    if user_input in greetings:
        return "Hello! 👋 Welcome to City Hospital. How can I assist you today?"

    # ✅ Step 2: Keyword-based quick detection for special cases
    if any(word in user_input for word in ["visit", "visitor", "visiting"]):
        return faq["visitor_guidelines"]["answer"]

    # ✅ Step 3: Fuzzy matching using RapidFuzz (more accurate)
    best_score = 0
    best_answer = None

    for category, data in faq.items():
        for q in data["questions"]:
            score1 = fuzz.token_sort_ratio(user_input, q.lower())
            score2 = fuzz.partial_ratio(user_input, q.lower())
            score = (score1 + score2) / 2  # average both scores

            if score > best_score:
                best_score = score
                best_answer = data["answer"]

    # ✅ Step 4: Return best match or fallback
    if best_score > 50:  # lowered threshold for better flexibility
        return best_answer
    else:
        return (
            "🤖 I am here to help with hospital-related questions like "
            "appointments, lab tests, doctors, or visiting hours. 😊"
        )


# ✅ Flask routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["GET"])
def start_chat():
    return jsonify({"response": greeting_message})

@app.route("/get", methods=["POST"])
def get_bot_response():
    user_text = request.json.get("msg", "").strip()
    response = get_best_answer(user_text)
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True)
