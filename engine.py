"""
Life Engine — Core Simulation Engine
Orchestrates updates: elapsed time decay, random events, immediate actions with synergy multipliers, 
rolling consistency, and bottom-up score recomputation.
"""
from datetime import datetime, timedelta
import storage
from attributes import compute_scores
from rules import calculate_gain, calculate_synergies
from actions import resolve_action, get_fundamental_category
from events import roll_random_events, EVENT_POOL

def get_rolling_consistency(action_log, reference_time):
    """
    Calculates Consistency: percentage of unique calendar days in the last 7 days 
    (relative to reference_time) containing at least one logged action.
    """
    if not action_log:
        return 0.0
        
    ref_date = reference_time.date()
    # Define the 7-day rolling window (inclusive of reference day)
    target_dates = {ref_date - timedelta(days=i) for i in range(7)}
    
    logged_dates = set()
    for log in action_log:
        ts_str = log.get("timestamp")
        if ts_str:
            try:
                log_date = datetime.fromisoformat(ts_str).date()
                if log_date in target_dates:
                    logged_dates.add(log_date)
            except Exception:
                pass
                
    active_days = len(logged_dates)
    return (active_days / 7.0) * 100.0


def apply_deltas_to_fundamentals(fundamentals, deltas, config_synergies, sub_scores, primary_scores):
    """
    Applies modification deltas to fundamentals, calculating synergies and diminishing returns.
    """
    # 1. Compute synergy multipliers based on current attributes
    synergy_mults = calculate_synergies(fundamentals, sub_scores, primary_scores, config_synergies)
    
    # 2. Apply deltas
    for fund_name, raw_delta in deltas.items():
        if fund_name not in fundamentals:
            continue
            
        current_val = fundamentals[fund_name]
        
        # Check synergy multiplier for the category of this fundamental
        category = get_fundamental_category(fund_name)
        multiplier = synergy_mults.get(category, 1.0)
        
        # Scale gain if positive, apply penalties directly
        if raw_delta > 0:
            scaled_delta = raw_delta * multiplier
        else:
            scaled_delta = raw_delta
            
        # Apply diminishing returns
        effective_delta = calculate_gain(current_val, scaled_delta)
        
        # Update and clamp
        fundamentals[fund_name] = max(10.0, min(100.0, current_val + effective_delta))


def update_simulation(state, config, current_time=None):
    """
    Runs the simulation update sequence to catch up to current_time:
    1. Calculate elapsed time.
    2. Apply linear decay to fundamentals.
    3. Trigger random events.
    4. Recalculate 7-day consistency.
    5. Recompute bottom-up attribute values.
    
    Args:
        state (dict): The current loaded state dictionary.
        config (dict): Loaded config dictionary.
        current_time (datetime, optional): Timestamp to update to. Defaults to datetime.now().
        
    Returns:
        list: Names of random events triggered during this update.
    """
    if current_time is None:
        current_time = datetime.now()
        
    last_update_str = state.get("last_update")
    if not last_update_str:
        state["last_update"] = current_time.isoformat()
        last_update = current_time
    else:
        try:
            last_update = datetime.fromisoformat(last_update_str)
        except ValueError:
            last_update = current_time
            state["last_update"] = current_time.isoformat()
            
    elapsed_time = current_time - last_update
    elapsed_days = elapsed_time.total_seconds() / 86400.0
    
    # Avoid updates if time runs backwards
    if elapsed_days < 0:
        elapsed_days = 0.0
        
    fundamentals = state["fundamentals"]
    decay_rates = config["decay_rates"]
    
    # 1. Apply linear decay (skip consistency, which is computed dynamically)
    for fund_name, val in fundamentals.items():
        if fund_name == "consistency":
            continue
        rate = decay_rates.get(fund_name, 0.0)
        decay_amount = rate * elapsed_days
        fundamentals[fund_name] = max(10.0, min(100.0, val - decay_amount))
        
    # Get current scores to evaluate event conditions/vitality
    hierarchy = config["hierarchy"]
    sub_scores, primary_scores, _ = compute_scores(fundamentals, hierarchy)
    
    # 2. Trigger random events based on days passed
    triggered_event_ids = roll_random_events(elapsed_days, primary_scores.get("vitality", 50.0))
    for event_id in triggered_event_ids:
        event_def = EVENT_POOL.get(event_id)
        if event_def:
            effects = event_def.get("effects", {})
            # Event changes are applied directly
            apply_deltas_to_fundamentals(
                fundamentals, 
                effects, 
                config.get("synergies", []), 
                sub_scores, 
                primary_scores
            )
            # Recompute intermediate scores in case next event has dependency
            sub_scores, primary_scores, _ = compute_scores(fundamentals, hierarchy)
            # Log the event
            state["event_log"].append({
                "event_id": event_id,
                "name": event_def.get("name"),
                "timestamp": current_time.isoformat()
            })
            
    # 3. Recalculate 7-day consistency and apply it directly as a fundamental value
    fundamentals["consistency"] = get_rolling_consistency(state["action_log"], current_time)
    
    # 4. Final bottom-up scores recalculation
    sub_scores, primary_scores, overall = compute_scores(fundamentals, hierarchy)
    state["sub_attributes"] = sub_scores
    state["primary_attributes"] = primary_scores
    state["overall_score"] = overall
    state["last_update"] = current_time.isoformat()
    
    return [EVENT_POOL[eid]["name"] for eid in triggered_event_ids]


def log_action(state, config, action_key, current_time=None):
    """
    Performs immediate logging of an action.
    1. Updates simulation to catch up to current time (applying decay and random events).
    2. Resolves action alias.
    3. Calculates synergy multipliers and applies action effects to fundamentals.
    4. Appends to action log.
    5. Saves updated state.
    
    Args:
        state (dict): Current state.
        config (dict): Current config.
        action_key (str): Alias or ID of action to log.
        current_time (datetime, optional): Time of log. Defaults to datetime.now().
        
    Returns:
        tuple: (action_name, list_of_random_events_triggered)
    """
    if current_time is None:
        current_time = datetime.now()
        
    # 1. Update simulation to current time first
    random_events = update_simulation(state, config, current_time)
    
    # 2. Resolve Action
    action_id, action_def = resolve_action(action_key, config.get("actions", {}))
    if not action_id:
        raise ValueError(f"Action '{action_key}' is not recognized.")
        
    # 3. Apply action effects to fundamentals
    effects = action_def.get("effects", {})
    fundamentals = state["fundamentals"]
    sub_scores = state["sub_attributes"]
    primary_scores = state["primary_attributes"]
    
    apply_deltas_to_fundamentals(
        fundamentals, 
        effects, 
        config.get("synergies", []), 
        sub_scores, 
        primary_scores
    )
    
    # 4. Log the action
    state["action_log"].append({
        "action_id": action_id,
        "name": action_def.get("name"),
        "timestamp": current_time.isoformat()
    })
    
    # 5. Recalculate rolling consistency and attributes post-action
    fundamentals["consistency"] = get_rolling_consistency(state["action_log"], current_time)
    sub_scores, primary_scores, overall = compute_scores(fundamentals, config["hierarchy"])
    state["sub_attributes"] = sub_scores
    state["primary_attributes"] = primary_scores
    state["overall_score"] = overall
    
    # 6. Save state
    storage.save_state(state)
    
    return action_def.get("name"), random_events
