"""
Life Engine — Storage Module
Manages reading/writing of config.json and state.json with safety checks and backup handling.
"""
import os
import json
import shutil
from attributes import validate_hierarchy

# Resolve paths relative to project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "data", "config.json")
STATE_PATH = os.path.join(BASE_DIR, "data", "state.json")
BACKUP_PATH = os.path.join(BASE_DIR, "data", "state.json.bak")


def load_config():
    """
    Loads config.json and validates its hierarchy and mappings.
    Returns:
        dict: Parsed config.
    Raises:
        ValueError: If configuration fails validation.
    """
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Configuration file not found at: {CONFIG_PATH}")
        
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config.json: {e}")
        
    # Validate the structural mapping
    is_valid, msg = validate_hierarchy(config)
    if not is_valid:
        raise ValueError(f"Config Validation Error: {msg}")
        
    # Additional validation: Verify decay rates cover all fundamentals in the tree
    hierarchy = config.get("hierarchy", {})
    decay_rates = config.get("decay_rates", {})
    all_mapped_fundamentals = set()
    
    for _, primary_data in hierarchy.items():
        subs = primary_data.get("subs", {})
        for _, fund_weights in subs.items():
            for fund_name in fund_weights.keys():
                all_mapped_fundamentals.add(fund_name)
                
    missing_decays = [f for f in all_mapped_fundamentals if f not in decay_rates]
    # Consistency is auto-calculated and exempt from decay
    if "consistency" in missing_decays:
        missing_decays.remove("consistency")
        
    if missing_decays:
        raise ValueError(f"Config Validation Error: Missing decay rates for fundamentals: {missing_decays}")
        
    return config


def load_state():
    """
    Loads state.json. If it does not exist, returns None.
    Returns:
        dict: Parsed state or None.
    """
    if not os.path.exists(STATE_PATH):
        return None
        
    try:
        with open(STATE_PATH, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # If corrupted, try loading backup
        if os.path.exists(BACKUP_PATH):
            try:
                with open(BACKUP_PATH, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return None


def save_state(state):
    """
    Saves state.json safely after creating a backup copy of the current state.
    
    Args:
        state (dict): State dictionary to save.
    """
    # Create directory if missing
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    
    # Create backup copy if existing file is valid
    if os.path.exists(STATE_PATH):
        try:
            # Verify existing file is loadable before backing up (avoid backing up garbage)
            with open(STATE_PATH, 'r') as f:
                json.load(f)
            shutil.copy2(STATE_PATH, BACKUP_PATH)
        except Exception:
            pass
            
    # Write new state
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)


def save_config(config):
    """
    Saves config.json after validation.
    
    Args:
        config (dict): Config dictionary to save.
    """
    is_valid, msg = validate_hierarchy(config)
    if not is_valid:
        raise ValueError(f"Cannot save config: {msg}")
        
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
