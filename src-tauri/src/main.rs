#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use rusqlite::{Connection, Result};
use serde::{Deserialize, Serialize};
use std::fs;
use std::sync::Mutex;
use tauri::{Manager, State};

#[derive(Debug, Serialize, Deserialize)]
struct HunterProfile {
    id: i32,
    current_rank: String,
    current_level: i32,
    current_xp: i32,
    stat_int: i32,
    stat_str: i32,
    stat_blood: i32,
    stat_wil: i32,
    hidden_indomitability: i32,
    hidden_authority: i32,
    current_stamina: i32,
    system_state: String,
    updated_at: String,
}

struct AppState {
    db: Mutex<Connection>,
}

fn init_db(db_path: &std::path::Path) -> Result<Connection> {
    let conn = Connection::open(db_path)?;

    // Initialize Schema exactly as demanded by the SRS
    conn.execute_batch(
        "
        CREATE TABLE IF NOT EXISTS hunter_profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            current_rank TEXT DEFAULT 'F' CHECK (current_rank IN ('F','E','D','C','B','A','S','SS','SSS')),
            current_level INTEGER DEFAULT 1,
            current_xp INTEGER DEFAULT 0,
            stat_int INTEGER DEFAULT 10,
            stat_str INTEGER DEFAULT 10,
            stat_blood INTEGER DEFAULT 10,
            stat_wil INTEGER DEFAULT 10,
            hidden_indomitability INTEGER DEFAULT 0,
            hidden_authority INTEGER DEFAULT 0,
            current_stamina INTEGER DEFAULT 100 CHECK (current_stamina BETWEEN 0 AND 100),
            system_state TEXT DEFAULT 'NORMAL' CHECK (system_state IN ('NORMAL', 'SHATTERED')),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        INSERT OR IGNORE INTO hunter_profile (id) VALUES (1);

        CREATE TABLE IF NOT EXISTS quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT CHECK (category IN ('STUDY', 'FITNESS', 'LIFE')),
            eisenhower_quadrant INTEGER CHECK (eisenhower_quadrant BETWEEN 1 AND 4),
            xp_reward INTEGER NOT NULL,
            status TEXT DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'COMPLETED', 'ABANDONED')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS chronicle_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date DATE UNIQUE NOT NULL,
            total_focus_minutes INTEGER DEFAULT 0,
            study_minutes_total INTEGER DEFAULT 0,
            fitness_minutes_total INTEGER DEFAULT 0,
            completed_quests_count INTEGER DEFAULT 0,
            vitals_json TEXT,
            ai_feedback_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ",
    )?;

    Ok(conn)
}

#[tauri::command]
fn get_hunter_profile(state: State<AppState>) -> Result<HunterProfile, String> {
    let conn = state.db.lock().map_err(|_| "Failed to lock database".to_string())?;

    let mut stmt = conn
        .prepare(
            "SELECT id, current_rank, current_level, current_xp, stat_int, stat_str, 
             stat_blood, stat_wil, hidden_indomitability, hidden_authority, current_stamina, 
             system_state, updated_at FROM hunter_profile WHERE id = 1"
        )
        .map_err(|e| e.to_string())?;

    let profile = stmt
        .query_row([], |row| {
            Ok(HunterProfile {
                id: row.get(0)?,
                current_rank: row.get(1)?,
                current_level: row.get(2)?,
                current_xp: row.get(3)?,
                stat_int: row.get(4)?,
                stat_str: row.get(5)?,
                stat_blood: row.get(6)?,
                stat_wil: row.get(7)?,
                hidden_indomitability: row.get(8)?,
                hidden_authority: row.get(9)?,
                current_stamina: row.get(10)?,
                system_state: row.get(11)?,
                updated_at: row.get(12)?,
            })
        })
        .map_err(|e| e.to_string())?;

    Ok(profile)
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            // Establish the local embedded store
            let app_dir = app
                .path_resolver()
                .app_data_dir()
                .expect("Failed to resolve app data directory");
            
            if !app_dir.exists() {
                fs::create_dir_all(&app_dir).expect("Failed to create app data directory");
            }
            
            let db_path = app_dir.join("arise_core.db");
            let db = init_db(&db_path).expect("Failed to forge the database schemas");

            // Bind the persistence layer to Tauri's managed state
            app.manage(AppState {
                db: Mutex::new(db),
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![get_hunter_profile])
        .run(tauri::generate_context!())
        .expect("Fatal error while igniting the Tauri engine");
}
