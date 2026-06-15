"""
Life Engine — Rules Module Tests
"""
import pytest
from rules import calculate_gain, calculate_synergies

def test_calculate_gain_diminishing():
    # Positive gains have diminishing returns
    # raw_gain = 10, current_value = 0 -> effective = 10 * (1 - 0) = 10
    assert calculate_gain(0.0, 10.0) == pytest.approx(10.0)
    
    # raw_gain = 10, current_value = 50 -> effective = 10 * (1 - 0.5) = 5
    assert calculate_gain(50.0, 10.0) == pytest.approx(5.0)
    
    # raw_gain = 10, current_value = 90 -> effective = 10 * (1 - 0.9) = 1
    assert calculate_gain(90.0, 10.0) == pytest.approx(1.0)


def test_calculate_gain_penalties():
    # Penalties are applied linearly, no diminishing returns
    assert calculate_gain(80.0, -5.0) == -5.0
    assert calculate_gain(20.0, -5.0) == -5.0


def test_calculate_synergies():
    fundamentals = {"self_awareness": 80.0}
    sub_scores = {"focus": 60.0}
    primary_scores = {"discipline": 75.0, "vitality": 50.0}
    
    synergies_config = [
        {
            "id": "discipline_boosts_cognition",
            "trigger_attribute": "discipline",
            "threshold": 70.0,
            "multiplier": 1.2,
            "target_category": "cognition"
        },
        {
            "id": "vitality_boosts_discipline",
            "trigger_attribute": "vitality",
            "threshold": 70.0,
            "multiplier": 1.3,
            "target_category": "discipline"
        },
        {
            "id": "focus_boosts_cognition",
            "trigger_attribute": "focus",
            "threshold": 50.0,
            "multiplier": 1.15,
            "target_category": "cognition"
        }
    ]
    
    mults = calculate_synergies(fundamentals, sub_scores, primary_scores, synergies_config)
    
    # Discipline: vitality is 50.0 (< 70), so trigger is inactive. Multiplier = 1.0
    assert mults["discipline"] == 1.0
    
    # Cognition: 
    # discipline = 75.0 (>= 70) -> active (+0.2 bonus)
    # focus = 60.0 (>= 50) -> active (+0.15 bonus)
    # Total cognition multiplier = 1.0 + 0.2 + 0.15 = 1.35
    assert mults["cognition"] == pytest.approx(1.35)


def test_calculate_synergies_cap():
    fundamentals = {}
    sub_scores = {}
    primary_scores = {"discipline": 90.0, "vitality": 90.0}
    
    synergies_config = [
        {
            "id": "s1", "trigger_attribute": "discipline", "threshold": 70.0, "multiplier": 1.5, "target_category": "cognition"
        },
        {
            "id": "s2", "trigger_attribute": "vitality", "threshold": 70.0, "multiplier": 1.6, "target_category": "cognition"
        }
    ]
    
    mults = calculate_synergies(fundamentals, sub_scores, primary_scores, synergies_config)
    
    # Cognition bonuses: +0.5 and +0.6. Total = 1.0 + 0.5 + 0.6 = 2.1
    # Cap = 2.0
    assert mults["cognition"] == 2.0
