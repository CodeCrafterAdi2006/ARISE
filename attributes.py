"""
Life Engine — Attributes Module
Handles the representation and bottom-up computation of the 3-layer attribute tree.
"""

def validate_hierarchy(config):
    """
    Validates that:
    1. Sub-attribute weights sum to 1.0 (or close with float precision).
    2. Primary attribute weights sum to 1.0.
    """
    hierarchy = config.get("hierarchy", {})
    if not hierarchy:
        return False, "Hierarchy is empty or missing in config."

    primary_weight_sum = 0.0
    for primary_name, primary_data in hierarchy.items():
        primary_weight_sum += primary_data.get("weight", 0.0)
        subs = primary_data.get("subs", {})
        if not subs:
            return False, f"Primary attribute '{primary_name}' has no sub-attributes."
        
        for sub_name, fund_weights in subs.items():
            if not fund_weights:
                return False, f"Sub-attribute '{sub_name}' has no fundamentals mapped."
            weight_sum = sum(fund_weights.values())
            if abs(weight_sum - 1.0) > 1e-4 and weight_sum > 0:
                # If weights are specified but do not sum to 1.0
                return False, f"Fundamental weights for sub-attribute '{sub_name}' sum to {weight_sum}, expected 1.0."
            
    if abs(primary_weight_sum - 1.0) > 1e-4:
        return False, f"Primary attribute weights sum to {primary_weight_sum}, expected 1.0."

    return True, "Hierarchy is valid."


def compute_scores(fundamentals_dict, hierarchy_config):
    """
    Computes all Sub-Attributes and Primary Attributes bottom-up from Fundamentals.
    
    Args:
        fundamentals_dict (dict): Current values of fundamentals (name -> score).
        hierarchy_config (dict): 'hierarchy' section from config.json.
        
    Returns:
        tuple: (sub_attributes, primary_attributes, overall_score)
            sub_attributes: dict (name -> value)
            primary_attributes: dict (name -> value)
            overall_score: float
    """
    sub_scores = {}
    primary_scores = {}
    overall_score = 0.0
    
    for primary_name, primary_data in hierarchy_config.items():
        subs = primary_data.get("subs", {})
        primary_sum = 0.0
        sub_count = 0
        
        for sub_name, fund_weights in subs.items():
            # Calculate sub-attribute value as weighted average of fundamentals
            weighted_sum = 0.0
            total_weight = 0.0
            
            for fund_name, weight in fund_weights.items():
                fund_val = fundamentals_dict.get(fund_name, 10.0)  # Default to floor of 10.0
                weighted_sum += fund_val * weight
                total_weight += weight
                
            # If total_weight is 0 (unmapped), default to floor of 10.0
            sub_val = (weighted_sum / total_weight) if total_weight > 0 else 10.0
            # Clamp between 10.0 and 100.0 (Since fundamentals are clamped, this should be naturally bound)
            sub_scores[sub_name] = max(10.0, min(100.0, sub_val))
            
            primary_sum += sub_scores[sub_name]
            sub_count += 1
            
        # Primary attributes = simple average of their sub-attributes
        primary_val = (primary_sum / sub_count) if sub_count > 0 else 10.0
        primary_scores[primary_name] = max(10.0, min(100.0, primary_val))
        
        # Add to overall score weighted
        overall_score += primary_scores[primary_name] * primary_data.get("weight", 0.0)
        
    return sub_scores, primary_scores, max(10.0, min(100.0, overall_score))
