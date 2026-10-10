from datetime import date, timedelta

RED_FLAG_SYMPTOMS = {
    "breathing difficulty",
    "collapse",
    "mouth lesions",
    "hoof lesions",
    "sudden death",
}

ALLOWED_TRANSITIONS = {
    "Healthy": {"Suspect"},
    "Suspect": {"Healthy", "Isolated"},
    "Isolated": {"Monitored"},
    "Monitored": {"Isolated", "Cleared"},
    "Cleared": set(),
}


def classify_severity(symptoms: list[str], fever: bool) -> str:
    normalized = {s.strip().lower() for s in symptoms}
    if normalized & RED_FLAG_SYMPTOMS:
        return "Urgent"
    if fever or len(normalized) >= 2:
        return "Moderate"
    return "Low"


def calculate_next_due(date_administered: date, booster_interval_days: int) -> date:
    return date_administered + timedelta(days=booster_interval_days)


def transition_allowed(current: str, target: str) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())
