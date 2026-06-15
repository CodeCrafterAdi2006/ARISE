# ⚡ ARISE: Life Engine Simulation CLI

An advanced, command-line life simulation and self-tracking engine that models personal metrics bottom-up—from fundamental daily habits up to high-level primary attributes.

`ARISE: Life Engine` simulates your day-to-day choices, applying realistic mathematical rules such as **linear time-decay**, **asymmetric diminishing returns**, **synergy multipliers**, and **random shock events** to paint a live ASCII dashboard of your overall performance.

---

## 🚀 Key Features

- **Bottom-Up Attribute Hierarchy**:
  - **19 Fundamentals**: Core daily inputs like `sleep`, `nutrition`, `exercise`, `recovery`, `curiosity`, `clarity`, and more.
  - **Sub-Attributes**: Intermediate capabilities like `strength`, `focus`, `willpower`, `resilience`, and `charisma`.
  - **Primary Attributes**: The high-level dimensions of life: `Vitality`, `Cognition`, `Discipline`, `Emotional Core`, `Social`, and `Agency`.
- **Dynamic Real-Time Simulation**:
  - **Linear Decay**: Over time, your fundamentals decay at configurable rates to model natural attribute drop-off.
  - **Diminishing Returns**: Positive gains scale down as individual fundamentals approach their 100.0 cap, making higher levels harder to maintain.
  - **Synergies**: Reaching thresholds (e.g., >70.0) in trigger attributes boosts gains in target categories (e.g., High Discipline boosts Cognition actions by +20%).
- **Interactive Action & Event Logging**:
  - Log daily habits (like `Deep Work`, `Workout`, `Meditation`) using short aliases.
  - Trigger manual or random events (e.g., "Burnout", "Flow State", "Sickness").
- **ASCII Dashboard**: A sleek, reactive CLI dashboard displaying progress bars, primary attribute levels, rolling 7-day consistency metrics, and update history.

---

## 🛠️ Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/CodeCrafterAdi2006/ARISE.git
   cd ARISE
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   source .venv/bin/activate    # macOS/Linux
   ```

3. **Install Dependencies** (for testing):
   ```bash
   pip install pytest
   ```

---

## 🎮 How to Use the CLI

Run `cli.py` using your Python interpreter:

```bash
python cli.py [command] [argument]
```

### Dashboard Preview

```text
========================================
           L I F E   E N G I N E
========================================
OVERALL SCORE:  45.8 [■■■■■□□□□□]
----------------------------------------

VITALITY       [■■■■■□□□□□]  49.5
  ├─ Breath Control    :  49.5
  └─ Strength          :  49.5

COGNITION      [■■■■■□□□□□]  49.8
  ├─ Intelligence      :  49.8
  └─ Focus             :  49.8

DISCIPLINE     [■■■□□□□□□□]  29.9
  ├─ Grit              :  34.9
  └─ Willpower         :  34.9

EMOTIONAL CORE [■■■■■□□□□□]  49.8
  ├─ Resilience        :  49.9
  └─ Antifragility     :  49.9

SOCIAL         [■■■■■□□□□□]  49.8
  ├─ Charisma          :  49.8
  └─ Assertiveness     :  49.8

AGENCY         [■■■■■□□□□□]  49.8
  ├─ Integrity         :  49.8
  └─ Adaptability      :  49.8

----------------------------------------
Consistency (Last 7 Days): [□□□□□□□□□□]   0.0% (0/7 days active)
Last Update              : just now
========================================
```

### Supported Commands

| Command | Argument / Flag | Description |
| :--- | :--- | :--- |
| `status` | `--full` | Displays the ASCII dashboard. Use `--full` to expand sub-attributes and fundamentals. |
| `log` | `[action_alias]` | Logs a habit or action. If run without an argument, shows an interactive selector menu. |
| `log-event` | `[event_id]` | Manually triggers a specific event (e.g., `burnout`, `sickness`). |
| `validate` | None | Validates `data/config.json` structure, keys, and weights. |
| `config` | None | Runs the interactive configuration parameter editor. |
| `reset` | None | Permanently resets all logs and attributes to baseline defaults (50.0). |

### Action Aliases

- **`dw`**: Deep Work Session
- **`wo`**: Workout
- **`med`**: Meditation
- **`net`**: Networking
- **`sl` / `sleep`**: Sleep 8 Hours
- **`jf`**: Junk Food
- **`ds` / `doom`**: Doom Scrolling

---

## 🧪 Running the Tests

To run the test suite and verify calculations:

```bash
python -m pytest
```

---

## 🗺️ Future Roadmap & Upcoming Features

Here are some of the features planned for future updates to the ARISE Life Engine:

1. **Web Dashboard & GUI**:
   - A fully responsive web interface featuring dynamic chart visualizations, progress trends, and interactive logs.
2. **Google Calendar & Habit Tracker Integrations**:
   - Automatically sync and log actions by reading your calendar entries or external habit apps.
3. **Gamified Achievements & Quest System**:
   - Level up attributes, unlock badges, earn streaks, and complete daily quests.
4. **Enhanced ML-Based Recommendations**:
   - An intelligent assistant that analyzes your history to recommend specific actions to balance decaying metrics.
5. **Multi-User Profiles & Cloud Syncing**:
   - Secure cloud backups and support for multiple user profiles.

---

## 📄 License

This project is licensed under the MIT License.
