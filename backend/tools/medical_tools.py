from langchain_core.tools import tool


@tool
def emergency_check(symptoms: str) -> str:
    """
    Check whether the user's description contains signs
    that may require urgent medical attention.

    This is a safety-oriented screening tool, not a diagnosis.
    """

    emergency_signals = [
        "severe chest pain",
        "difficulty breathing",
        "shortness of breath",
        "loss of consciousness",
        "uncontrolled bleeding",
        "severe bleeding",
        "stroke symptoms",
        "face drooping",
        "sudden weakness",
        "suicidal thoughts",
        "severe allergic reaction"
    ]

    text = symptoms.lower()

    detected = [
        signal
        for signal in emergency_signals
        if signal in text
    ]

    if detected:
        return (
            "URGENT: The user's description contains a potential "
            "emergency warning sign. Recommend immediate professional "
            "medical evaluation or local emergency services. "
            f"Detected signals: {detected}"
        )

    return (
        "No predefined emergency warning phrase was detected. "
        "This does not rule out an emergency."
    )


@tool
def symptom_information(symptom: str) -> str:
    """
    Provide general information about a symptom.
    This is educational information and not a diagnosis.
    """

    information = {
        "headache": (
            "Headaches can have many causes, including dehydration, "
            "lack of sleep, stress, infections, migraine, or other "
            "conditions. Persistent, severe, or unusual headaches "
            "should be evaluated by a healthcare professional."
        ),

        "fever": (
            "Fever can occur with infections and other conditions. "
            "The significance depends on factors such as temperature, "
            "duration, age, symptoms, and medical history."
        ),

        "cough": (
            "Cough can occur with respiratory infections, allergies, "
            "asthma, reflux, and other conditions. Persistent or severe "
            "symptoms may require medical evaluation."
        )
    }

    key = symptom.lower().strip()

    return information.get(
        key,
        "I don't have specific information for that symptom in this basic knowledge tool."
    )


@tool
def medical_information(topic: str) -> str:
    """
    Provide general educational information about a medical topic.
    """

    return (
        f"General medical information about '{topic}' should be "
        "based on reliable medical sources and interpreted according "
        "to the individual's symptoms, history, medications, and "
        "clinical context. This assistant should not use this "
        "information to independently diagnose or prescribe."
    )