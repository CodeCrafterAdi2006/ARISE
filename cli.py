"""
Life Engine — Command Line Interface
Main entry point for logging actions, viewing the ASCII dashboard, and managing config.
"""
import sys
import argparse
from datetime import datetime
import storage
import engine
from actions import resolve_action
from events import EVENT_POOL

# Try to detect if console supports unicode characters
try:
    _encoding = sys.stdout.encoding or 'ascii'
    "■□├─└─│⚡".encode(_encoding)
    CHAR_FILL = "■"
    CHAR_EMPTY = "□"
    CHAR_BRANCH = "  ├─ "
    CHAR_LEAF = "  │  └─ "
    CHAR_SUB_LEAF = "  └─ "
    CHAR_SHOCK = "⚡"
except Exception:
    CHAR_FILL = "#"
    CHAR_EMPTY = "-"
    CHAR_BRANCH = "  |- "
    CHAR_LEAF = "  |  `- "
    CHAR_SUB_LEAF = "  `- "
    CHAR_SHOCK = "!"


def get_progress_bar(value):
    """
    Generates a 10-character wide progress bar.
    """
    filled = max(0, min(10, int(round(value / 10.0))))
    return "[" + CHAR_FILL * filled + CHAR_EMPTY * (10 - filled) + "]"


def get_time_ago(timestamp_str):
    """
    Returns a human-readable string representing elapsed time since timestamp_str.
    """
    if not timestamp_str:
        return "never"
    try:
        dt = datetime.fromisoformat(timestamp_str)
        diff = datetime.now() - dt
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            return f"{int(seconds // 60)} minutes ago"
        elif seconds < 86400:
            return f"{int(seconds // 3600)} hours ago"
        else:
            return f"{int(seconds // 86400)} days ago"
    except Exception:
        return "unknown"


def print_dashboard(state, config, show_full=False):
    """
    Prints a premium ASCII dashboard.
    """
    print("\n" + "=" * 40)
    print("           L I F E   E N G I N E")
    print("=" * 40)
    
    overall = state.get("overall_score", 50.0)
    print(f"OVERALL SCORE: {overall:5.1f} {get_progress_bar(overall)}")
    print("-" * 40)
    
    hierarchy = config.get("hierarchy", {})
    fundamentals = state.get("fundamentals", {})
    sub_scores = state.get("sub_attributes", {})
    primary_scores = state.get("primary_attributes", {})
    
    for primary, data in hierarchy.items():
        p_val = primary_scores.get(primary, 50.0)
        p_display = primary.replace("_", " ").upper()
        print(f"\n{p_display:<14} {get_progress_bar(p_val)} {p_val:5.1f}")
        
        # Get sub-attributes
        subs = data.get("subs", {})
        sub_list = []
        for sub_name in subs.keys():
            val = sub_scores.get(sub_name, 50.0)
            sub_list.append((sub_name, val))
            
        if show_full:
            # Show all sub-attributes and their fundamentals
            for sub_name, val in sub_list:
                print(f"{CHAR_BRANCH}{sub_name.replace('_', ' ').title():<18}: {val:5.1f}")
                # Print underlying fundamentals for this sub
                funds = subs[sub_name]
                for fund_name, weight in funds.items():
                    fund_val = fundamentals.get(fund_name, 50.0)
                    print(f"{CHAR_LEAF}{fund_name:<16} (w={weight:0.2f}): {fund_val:5.1f}")
        else:
            # Sort and show top 2 sub-attributes
            sub_list.sort(key=lambda x: x[1], reverse=True)
            for sub_name, val in sub_list[:2]:
                print(f"{CHAR_BRANCH}{sub_name.replace('_', ' ').title():<18}: {val:5.1f}")
                
    print("\n" + "-" * 40)
    consistency = fundamentals.get("consistency", 0.0)
    # Calculate active days count
    active_days_count = int(round((consistency / 100.0) * 7.0))
    print(f"Consistency (Last 7 Days): {get_progress_bar(consistency)} {consistency:5.1f}% ({active_days_count}/7 days active)")
    print(f"Last Update              : {get_time_ago(state.get('last_update'))}")
    print("=" * 40 + "\n")


def handle_log(state, config, action_key):
    """
    Handles logging of an action.
    """
    actions_dict = config.get("actions", {})
    
    if not action_key:
        # Show interactive selector menu
        print("\nSelect Action to Log:")
        action_list = []
        for idx, (act_id, act_def) in enumerate(actions_dict.items(), 1):
            aliases_str = ", ".join(act_def.get("aliases", []))
            print(f"{idx:2}) [{aliases_str:<5}] {act_def.get('name')}")
            action_list.append(act_id)
            
        print(" q) [exit ] Cancel")
        choice = input("Choice (number or alias): ").strip()
        
        if choice.lower() in ['q', 'quit', 'exit']:
            print("Cancelled.")
            return
            
        # Try resolving choice as index number
        try:
            val = int(choice)
            if 1 <= val <= len(action_list):
                action_key = action_list[val - 1]
        except ValueError:
            action_key = choice
            
    # Resolve and log action
    try:
        action_name, triggered_events = engine.log_action(state, config, action_key)
        print(f"\n[Success] Logged action: {action_name}")
        
        # Display triggered events
        if triggered_events:
            print("\n[Shock Events Occurred!]")
            for event in triggered_events:
                print(f"  {CHAR_SHOCK} {event}")
    except ValueError as e:
        print(f"\n[Error] {e}")


def handle_log_event(state, config, event_key):
    """
    Manually triggers an event.
    """
    if event_key not in EVENT_POOL:
        print(f"\n[Error] Event '{event_key}' is not recognized.")
        print("Available events: " + ", ".join(EVENT_POOL.keys()))
        return
        
    event_def = EVENT_POOL[event_key]
    # Apply effects
    fundamentals = state["fundamentals"]
    sub_scores = state["sub_attributes"]
    primary_scores = state["primary_attributes"]
    
    # Event changes are applied directly
    engine.apply_deltas_to_fundamentals(
        fundamentals, 
        event_def.get("effects", {}), 
        config.get("synergies", []), 
        sub_scores, 
        primary_scores
    )
    
    # Log the event
    state["event_log"].append({
        "event_id": event_key,
        "name": event_def.get("name"),
        "timestamp": datetime.now().isoformat()
    })
    
    # Recalculate and save
    fundamentals["consistency"] = engine.get_rolling_consistency(state["action_log"], datetime.now())
    sub_scores, primary_scores, overall = engine.compute_scores(fundamentals, config["hierarchy"])
    state["sub_attributes"] = sub_scores
    state["primary_attributes"] = primary_scores
    state["overall_score"] = overall
    state["last_update"] = datetime.now().isoformat()
    
    storage.save_state(state)
    print(f"\n[Success] Manually triggered shock event: {event_def.get('name')}")


def handle_validate(config):
    """
    Explicitly validates config.json schema and weights.
    """
    try:
        storage.save_config(config)  # Runs validation inside
        print("\n[Valid] data/config.json structure and weights are perfectly valid!")
    except Exception as e:
        print(f"\n[Invalid] Config contains errors:\n  {e}")


def handle_config_edit(config):
    """
    Interactive config parameter editor.
    """
    print("\n" + "!" * 50)
    print(" WARNING: Modifying config variables affects scores retroactively.")
    print("!" * 50)
    confirm = input("Are you sure you want to proceed? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled.")
        return
        
    print("\nSelect Parameter Type to Edit:")
    print("1) Fundamental Decay Rates")
    print("2) Sub-Attribute / Primary Weights")
    print("Choice: ")
    choice = input().strip()
    
    if choice == "1":
        # Edit Decay Rates
        decay_rates = config.get("decay_rates", {})
        print("\nCurrent Decay Rates:")
        keys = sorted(decay_rates.keys())
        for idx, k in enumerate(keys, 1):
            print(f"{idx:2}) {k:<25}: {decay_rates[k]:.2f}/day")
            
        c_sub = input("\nSelect number to edit (or 'q' to quit): ").strip()
        if c_sub.lower() in ['q', 'exit']:
            return
            
        try:
            val = int(c_sub)
            if 1 <= val <= len(keys):
                target_key = keys[val - 1]
                new_val_str = input(f"Enter new daily decay rate for '{target_key}' (currently {decay_rates[target_key]}): ").strip()
                new_val = float(new_val_str)
                if new_val < 0:
                    print("Decay rates cannot be negative.")
                    return
                # Save backup config
                old_val = decay_rates[target_key]
                decay_rates[target_key] = new_val
                
                try:
                    storage.save_config(config)
                    print(f"[Success] Updated decay rate of '{target_key}' from {old_val} to {new_val}.")
                except Exception as e:
                    decay_rates[target_key] = old_val
                    print(f"[Error] Failed to save config: {e}")
        except Exception as e:
            print(f"Error: {e}")
            
    elif choice == "2":
        # Edit Sub-Attribute Weights
        hierarchy = config.get("hierarchy", {})
        print("\nSelect Category:")
        categories = list(hierarchy.keys())
        for idx, cat in enumerate(categories, 1):
            print(f"{idx:2}) {cat.replace('_', ' ').title()}")
            
        cat_choice = input("Choice: ").strip()
        try:
            cat_idx = int(cat_choice)
            if 1 <= cat_idx <= len(categories):
                category = categories[cat_idx - 1]
                subs = hierarchy[category]["subs"]
                print(f"\nSub-Attributes under {category.upper()}:")
                sub_keys = list(subs.keys())
                for s_idx, sub in enumerate(sub_keys, 1):
                    print(f"  {s_idx:2}) {sub.replace('_', ' ').title()}")
                    
                sub_choice = input("\nSelect Sub-Attribute to edit fundamental weights: ").strip()
                sub_val = int(sub_choice)
                if 1 <= sub_val <= len(sub_keys):
                    target_sub = sub_keys[sub_val - 1]
                    funds = subs[target_sub]
                    print(f"\nWeights for '{target_sub}':")
                    fund_keys = list(funds.keys())
                    new_weights = {}
                    
                    for f_key in fund_keys:
                        n_weight_str = input(f"  Enter weight for '{f_key}' (currently {funds[f_key]}): ").strip()
                        new_weights[f_key] = float(n_weight_str)
                        
                    # Validate sum
                    total = sum(new_weights.values())
                    if abs(total - 1.0) > 1e-4:
                        print(f"\n[Warning] Weights sum to {total:.3f}, expected 1.0. Readjusting proportionally...")
                        for f_key in new_weights:
                            new_weights[f_key] = round(new_weights[f_key] / total, 4)
                            
                    # Backup and attempt save
                    old_weights = dict(funds)
                    hierarchy[category]["subs"][target_sub] = new_weights
                    
                    try:
                        storage.save_config(config)
                        print(f"[Success] Updated weights for '{target_sub}' to {new_weights}.")
                    except Exception as e:
                        hierarchy[category]["subs"][target_sub] = old_weights
                        print(f"[Error] Failed to save config: {e}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Invalid choice.")

def handle_reset(config):
    """
    Resets the state to initial default baseline values.
    """
    print("\n" + "!" * 50)
    print(" WARNING: This will permanently erase all action logs and reset progress.")
    print("!" * 50)
    confirm = input("Are you sure you want to reset all state? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled.")
        return
        
    state = {
        "last_update": datetime.now().isoformat(),
        "fundamentals": {
            "sleep": 50.0, "nutrition": 50.0, "exercise": 50.0, "recovery": 50.0,
            "curiosity": 50.0, "clarity": 50.0, "cognitive_flexibility": 50.0,
            "consistency": 0.0, "self_efficacy": 50.0, "ambiguity_tolerance": 50.0,
            "self_awareness": 50.0, "acceptance": 50.0, "patience": 50.0,
            "active_listening": 50.0, "boundary_setting": 50.0, "humor": 50.0,
            "meaning_making": 50.0, "presence": 50.0, "control": 50.0
        },
        "sub_attributes": {},
        "primary_attributes": {},
        "action_log": [],
        "event_log": []
    }
    # Run bottom-up computation to seed the empty sub/primary scopes
    sub, prim, overall = engine.compute_scores(state["fundamentals"], config["hierarchy"])
    state["sub_attributes"] = sub
    state["primary_attributes"] = prim
    state["overall_score"] = overall
    storage.save_state(state)
    print("\n[Success] Progress has been reset to baseline defaults.")


def main():
    parser = argparse.ArgumentParser(description="Life Engine Simulation CLI")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "log", "log-event", "validate", "config", "reset"],
                        help="Action to perform (default: status)")
    parser.add_argument("argument", nargs="?", default=None,
                        help="Additional parameter for command (e.g. action alias or event ID)")
    parser.add_argument("--full", action="store_true",
                        help="Show full attribute details including all fundamentals")
    
    args = parser.parse_args()
    
    # Load config (exit if corrupted)
    try:
        config = storage.load_config()
    except Exception as e:
        print(f"\n[Critical Error] Failed to load configuration:\n  {e}\nFix data/config.json before continuing.")
        sys.exit(1)
        
    # Load state. If missing or corrupted, initialize default state.
    state = storage.load_state()
    if state is None:
        print("\n[Notice] No valid state.json detected. Initializing standard baselines...")
        # Create fresh state from default values (50.0 baseline)
        state = {
            "last_update": datetime.now().isoformat(),
            "fundamentals": {
                "sleep": 50.0, "nutrition": 50.0, "exercise": 50.0, "recovery": 50.0,
                "curiosity": 50.0, "clarity": 50.0, "cognitive_flexibility": 50.0,
                "consistency": 0.0, "self_efficacy": 50.0, "ambiguity_tolerance": 50.0,
                "self_awareness": 50.0, "acceptance": 50.0, "patience": 50.0,
                "active_listening": 50.0, "boundary_setting": 50.0, "humor": 50.0,
                "meaning_making": 50.0, "presence": 50.0, "control": 50.0
            },
            "sub_attributes": {},
            "primary_attributes": {},
            "action_log": [],
            "event_log": []
        }
        # Run first bottom-up computation to seed the empty sub/primary scopes
        sub, prim, overall = engine.compute_scores(state["fundamentals"], config["hierarchy"])
        state["sub_attributes"] = sub
        state["primary_attributes"] = prim
        state["overall_score"] = overall
        storage.save_state(state)
        
    # Standard time update check for status or other display commands
    if args.command == "status":
        # Catch up simulation (decay + random shocks) up to current time
        triggered_events = engine.update_simulation(state, config, datetime.now())
        storage.save_state(state)
        if triggered_events:
            print("\n[Shock Events Occurred!]")
            for event in triggered_events:
                print(f"  {CHAR_SHOCK} {event}")
        print_dashboard(state, config, show_full=args.full)
        
    elif args.command == "log":
        handle_log(state, config, args.argument)
        
    elif args.command == "log-event":
        handle_log_event(state, config, args.argument)
        
    elif args.command == "validate":
        handle_validate(config)
        
    elif args.command == "config":
        handle_config_edit(config)
        
    elif args.command == "reset":
        handle_reset(config)


if __name__ == "__main__":
    main()
