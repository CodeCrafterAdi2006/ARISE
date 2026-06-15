"""
Life Engine — Rules Module
Handles calculations for diminishing returns and stacking synergy multipliers.
"""

def calculate_gain(current_value, raw_gain, scaling_factor=1.0):
    """
    Applies asymmetric diminishing returns to positive gains.
    Penalties/losses are applied linearly without diminishing returns.
    
    Args:
        current_value (float): Current score of the fundamental (10.0 to 100.0).
        raw_gain (float): Raw change (positive or negative).
        scaling_factor (float): Optional multiplier.
        
    Returns:
        float: The effective change to apply.
    """
    if raw_gain <= 0:
        return raw_gain
        
    # Diminishing returns: gains slow down as the score approaches 100
    factor = 1.0 - (current_value / 100.0)
    factor = max(0.0, min(1.0, factor))  # Keep factor bound between 0 and 1
    
    return raw_gain * factor * scaling_factor


def calculate_synergies(fundamentals, sub_attributes, primary_attributes, synergies_config):
    """
    Computes active synergy multipliers for each primary attribute category.
    Uses additive stacking and applies a hard cap of 2.0.
    
    Args:
        fundamentals (dict): Current fundamentals.
        sub_attributes (dict): Current sub-attributes.
        primary_attributes (dict): Current primary attributes.
        synergies_config (list): List of synergy definitions from config.json.
        
    Returns:
        dict: Target category -> Total synergy multiplier (range 1.0 to 2.0).
    """
    # Initialize all categories with a base multiplier of 1.0
    active_bonuses = {}
    
    # Check each synergy rule
    for synergy in synergies_config:
        trigger_attr = synergy.get("trigger_attribute")
        threshold = synergy.get("threshold", 70.0)
        mult = synergy.get("multiplier", 1.0)
        target_cat = synergy.get("target_category")
        
        # Look up value across all 3 layers
        val = None
        if trigger_attr in primary_attributes:
            val = primary_attributes[trigger_attr]
        elif trigger_attr in sub_attributes:
            val = sub_attributes[trigger_attr]
        elif trigger_attr in fundamentals:
            val = fundamentals[trigger_attr]
            
        # If attribute is found and exceeds threshold, stack the bonus
        if val is not None and val >= threshold:
            bonus = mult - 1.0
            if target_cat not in active_bonuses:
                active_bonuses[target_cat] = []
            active_bonuses[target_cat].append(bonus)
            
    # Compute final stacked multipliers with a cap of 2.0
    multipliers = {}
    for cat in ["vitality", "cognition", "discipline", "emotional_core", "social", "agency"]:
        bonuses = active_bonuses.get(cat, [])
        total_mult = 1.0 + sum(bonuses)
        multipliers[cat] = min(2.0, max(1.0, total_mult))
        
    return multipliers
