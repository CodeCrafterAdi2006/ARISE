"""
Life Engine — Events Module
Defines random/manual shocks (events) and rolls for random events on time elapsed.
"""
import random

# Predefined event pool mapping to raw fundamental deltas
EVENT_POOL = {
    "pulled_all_nighter": {
        "name": "Pulled an All-Nighter",
        "effects": {
            "sleep": -15.0,
            "self_efficacy": -3.0,
            "clarity": -5.0
        },
        "trigger_probability": 0.05,
        "description": "Stayed up all night. Vitality and mental clarity took a massive hit."
    },
    "internship_rejection": {
        "name": "Rejected from Internship",
        "effects": {
            "acceptance": +5.0,
            "self_efficacy": -6.0,
            "patience": +3.0
        },
        "trigger_probability": 0.03,
        "description": "Faced setback. Rejection builds resilience but shocks self-efficacy."
    },
    "cracked_leetcode": {
        "name": "Cracked a Hard LeetCode",
        "effects": {
            "self_efficacy": +6.0,
            "curiosity": +3.0,
            "clarity": +2.0
        },
        "trigger_probability": 0.08,
        "description": "Solved a tough problem. Confidence surged."
    },
    "real_conversation": {
        "name": "Had a Real Conversation",
        "effects": {
            "active_listening": +4.0,
            "presence": +3.0,
            "humor": +2.0
        },
        "trigger_probability": 0.08,
        "description": "Connected deeply with someone. Social and presence stats boosted."
    },
    "got_sick": {
        "name": "Got Sick",
        "effects": {
            "recovery": -8.0,
            "sleep": -6.0,
            "nutrition": -4.0
        },
        "trigger_probability": 0.04,
        "description": "Caught a bug. Recovery and baseline vitality plummeted."
    }
}

def roll_random_events(elapsed_days, current_vitality=50.0):
    """
    Simulates daily checks for random shocks.
    Each full day elapsed triggers independent probability checks.
    
    Args:
        elapsed_days (float): Number of days passed since last run.
        current_vitality (float): Current vitality value (used to scale sick chance).
        
    Returns:
        list: Selected event IDs.
    """
    triggered_events = []
    days = int(elapsed_days)
    
    if days <= 0:
        return triggered_events
        
    # Cap daily rolls to prevent overflow shock if user is absent for a long time
    days = min(days, 5)
    
    for _ in range(days):
        for event_id, event_def in EVENT_POOL.items():
            prob = event_def.get("trigger_probability", 0.05)
            
            # Boost sickness probability if Vitality is dangerously low
            if event_id == "got_sick" and current_vitality < 30.0:
                prob = 0.20  # 4x higher risk
                
            if random.random() < prob:
                triggered_events.append(event_id)
                # Max 1 random event per day roll
                break
                
    # Cap at a maximum of 2 random events per update to protect state
    return triggered_events[:2]
