from datetime import date
from backend.rules import classify_severity, calculate_next_due, transition_allowed


def test_red_flag_symptom_is_urgent():
    assert classify_severity(["breathing difficulty"], False) == "Urgent"


def test_fever_or_two_symptoms_is_moderate():
    assert classify_severity(["loss of appetite"], True) == "Moderate"
    assert classify_severity(["cough", "loss of appetite"], False) == "Moderate"


def test_single_non_red_flag_symptom_is_low():
    assert classify_severity(["mild cough"], False) == "Low"


def test_quarantine_transition_rules():
    assert transition_allowed("Healthy", "Suspect")
    assert transition_allowed("Suspect", "Isolated")
    assert transition_allowed("Isolated", "Monitored")
    assert transition_allowed("Monitored", "Cleared")
    assert not transition_allowed("Healthy", "Cleared")
    assert not transition_allowed("Isolated", "Cleared")


def test_booster_due_date():
    assert calculate_next_due(date(2026, 10, 9), 365) == date(2027, 10, 9)
