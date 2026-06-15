"""
Life Engine — Actions Module
Handles action alias resolution and category mapping for synergy application.
"""

# Map every fundamental to its primary attribute category
FUNDAMENTAL_CATEGORIES = {
    "sleep": "vitality",
    "nutrition": "vitality",
    "exercise": "vitality",
    "recovery": "vitality",
    "curiosity": "cognition",
    "clarity": "cognition",
    "cognitive_flexibility": "cognition",
    "self_efficacy": "discipline",
    "ambiguity_tolerance": "discipline",
    "self_awareness": "emotional_core",
    "acceptance": "emotional_core",
    "patience": "emotional_core",
    "active_listening": "social",
    "boundary_setting": "social",
    "humor": "social",
    "meaning_making": "agency",
    "presence": "agency",
    "control": "agency",
    "consistency": "discipline"
}

def resolve_action(action_key, config_actions):
    """
    Finds an action configuration by its unique ID or shorthand alias.
    
    Args:
        action_key (str): The ID or alias of the action (e.g. 'dw' or 'deep_work').
        config_actions (dict): The 'actions' dictionary from config.json.
        
    Returns:
        tuple: (action_id, action_def) or (None, None) if not found.
    """
    if not action_key:
        return None, None
        
    action_key = action_key.lower().strip()
    
    # Check by primary ID
    if action_key in config_actions:
        return action_key, config_actions[action_key]
        
    # Check by alias
    for act_id, act_def in config_actions.items():
        aliases = [a.lower() for a in act_def.get("aliases", [])]
        if action_key in aliases:
            return act_id, act_def
            
    return None, None


def get_fundamental_category(fundamental_name):
    """
    Returns the primary category (e.g. 'vitality', 'cognition') for a given fundamental.
    """
    return FUNDAMENTAL_CATEGORIES.get(fundamental_name.lower().strip())
