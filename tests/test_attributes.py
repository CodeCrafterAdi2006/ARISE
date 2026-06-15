"""
Life Engine — Attributes Module Tests
"""
import pytest
from attributes import validate_hierarchy, compute_scores

@pytest.fixture
def sample_config():
    return {
        "hierarchy": {
            "vitality": {
                "subs": {
                    "strength": {
                        "exercise": 0.6,
                        "nutrition": 0.4
                    },
                    "constitution": {
                        "sleep": 0.5,
                        "nutrition": 0.5
                    }
                },
                "weight": 0.4
            },
            "cognition": {
                "subs": {
                    "intelligence": {
                        "curiosity": 1.0
                    }
                },
                "weight": 0.6
            }
        }
    }


def test_validate_hierarchy_success(sample_config):
    is_valid, msg = validate_hierarchy(sample_config)
    assert is_valid is True
    assert "valid" in msg.lower()


def test_validate_hierarchy_invalid_sub_weights(sample_config):
    # Make strength weights sum to 1.1 instead of 1.0
    sample_config["hierarchy"]["vitality"]["subs"]["strength"]["exercise"] = 0.7
    is_valid, msg = validate_hierarchy(sample_config)
    assert is_valid is False
    assert "strength" in msg


def test_validate_hierarchy_invalid_primary_weights(sample_config):
    # Make primary weights sum to 1.2 instead of 1.0
    sample_config["hierarchy"]["vitality"]["weight"] = 0.6
    is_valid, msg = validate_hierarchy(sample_config)
    assert is_valid is False
    assert "primary" in msg.lower()


def test_compute_scores(sample_config):
    fundamentals = {
        "exercise": 80.0,
        "nutrition": 60.0,
        "sleep": 50.0,
        "curiosity": 90.0
    }
    
    sub_scores, primary_scores, overall = compute_scores(fundamentals, sample_config["hierarchy"])
    
    # strength = 80*0.6 + 60*0.4 = 48 + 24 = 72.0
    assert sub_scores["strength"] == 72.0
    
    # constitution = 50*0.5 + 60*0.5 = 25 + 30 = 55.0
    assert sub_scores["constitution"] == 55.0
    
    # intelligence = 90*1.0 = 90.0
    assert sub_scores["intelligence"] == 90.0
    
    # vitality = (strength + constitution) / 2 = (72 + 55) / 2 = 63.5
    assert primary_scores["vitality"] == 63.5
    
    # cognition = (intelligence) / 1 = 90.0
    assert primary_scores["cognition"] == 90.0
    
    # overall = vitality * 0.4 + cognition * 0.6 = 63.5 * 0.4 + 90 * 0.6 = 25.4 + 54.0 = 79.4
    assert overall == pytest.approx(79.4)
