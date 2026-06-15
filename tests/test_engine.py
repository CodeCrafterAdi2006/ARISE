"""
Life Engine — Core Engine Module Tests
"""
from datetime import datetime, timedelta
import pytest
import engine

@pytest.fixture
def base_config():
    return {
        "hierarchy": {
            "vitality": {
                "subs": {
                    "strength": {
                        "exercise": 0.5,
                        "nutrition": 0.5
                    }
                },
                "weight": 1.0
            }
        },
        "decay_rates": {
            "exercise": 2.0,
            "nutrition": 1.0
        },
        "actions": {
            "deep_work": {
                "name": "Deep Work",
                "aliases": ["dw"],
                "effects": {
                    "exercise": 5.0
                }
            }
        },
        "synergies": []
    }


@pytest.fixture
def base_state():
    return {
        "last_update": "2026-06-15T00:00:00",
        "fundamentals": {
            "exercise": 50.0,
            "nutrition": 50.0,
            "consistency": 0.0
        },
        "sub_attributes": {},
        "primary_attributes": {},
        "action_log": [],
        "event_log": []
    }


def test_get_rolling_consistency():
    ref_time = datetime(2026, 6, 15, 12, 0, 0)
    
    # 1. No actions -> consistency = 0.0
    assert engine.get_rolling_consistency([], ref_time) == 0.0
    
    # 2. Add action on same day (June 15) -> 1/7 days active = 14.285%
    action_log = [
        {"timestamp": "2026-06-15T08:00:00", "action_id": "dw"}
    ]
    assert engine.get_rolling_consistency(action_log, ref_time) == pytest.approx(14.2857, abs=1e-3)
    
    # 3. Add actions on multiple days (June 15, June 14, June 10) -> 3/7 active = 42.857%
    action_log.extend([
        {"timestamp": "2026-06-14T18:00:00", "action_id": "dw"},
        {"timestamp": "2026-06-10T12:00:00", "action_id": "dw"}
    ])
    assert engine.get_rolling_consistency(action_log, ref_time) == pytest.approx(42.8571, abs=1e-3)
    
    # 4. Out of window action (June 7 is 8 days before June 15) -> should not count
    action_log.append({"timestamp": "2026-06-07T12:00:00", "action_id": "dw"})
    assert engine.get_rolling_consistency(action_log, ref_time) == pytest.approx(42.8571, abs=1e-3)


def test_update_simulation_decay(base_state, base_config):
    # Set time forward by exactly 2 days (48 hours)
    start_time = datetime.fromisoformat(base_state["last_update"])
    current_time = start_time + timedelta(days=2)
    
    triggered = engine.update_simulation(base_state, base_config, current_time)
    
    # exercise decay: 2.0/day * 2 days = 4.0 points. New = 50.0 - 4.0 = 46.0
    # nutrition decay: 1.0/day * 2 days = 2.0 points. New = 50.0 - 2.0 = 48.0
    assert base_state["fundamentals"]["exercise"] == 46.0
    assert base_state["fundamentals"]["nutrition"] == 48.0
    
    # Recomputed strength = 46.0*0.5 + 48.0*0.5 = 47.0
    assert base_state["sub_attributes"]["strength"] == 47.0
    assert base_state["primary_attributes"]["vitality"] == 47.0
    assert base_state["overall_score"] == 47.0
    
    # Timestamp is updated
    assert base_state["last_update"] == current_time.isoformat()


def test_update_simulation_decay_floor(base_state, base_config):
    # Set time forward by 100 days to trigger decay floor (10.0)
    start_time = datetime.fromisoformat(base_state["last_update"])
    current_time = start_time + timedelta(days=100)
    
    engine.update_simulation(base_state, base_config, current_time)
    
    assert base_state["fundamentals"]["exercise"] == 10.0
    assert base_state["fundamentals"]["nutrition"] == 10.0
    assert base_state["sub_attributes"]["strength"] == 10.0
