#!/usr/bin/env python3
"""
Database migration script to fix the spelling of 'explaination' to 'explanation'
"""

import os
import sqlite3
import shutil
from datetime import datetime

def migrate_database():
    db_path = "database.db"
    backup_path = f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    print(f"Starting database migration...")
    
    # Create backup of the existing database
    if os.path.exists(db_path):
        print(f"Creating backup: {backup_path}")
        shutil.copy2(db_path, backup_path)
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Check if the old column exists
            cursor.execute("PRAGMA table_info(challenge)")
            columns = cursor.fetchall()
            has_old_column = any(col[1] == 'explaination' for col in columns)
            
            if has_old_column:
                print("Found old 'explaination' column, migrating...")
                
                # Get existing data
                cursor.execute("SELECT id, difficulty, date_created, created_by, title, options, correct_answer_id, explaination FROM challenge")
                existing_data = cursor.fetchall()
                
                # Drop the old table
                cursor.execute("DROP TABLE challenge")
                
                # Create new table with correct spelling
                cursor.execute("""
                CREATE TABLE challenge (
                    id INTEGER PRIMARY KEY,
                    difficulty TEXT NOT NULL,
                    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT NOT NULL,
                    title TEXT NOT NULL,
                    options TEXT NOT NULL,
                    correct_answer_id INTEGER NOT NULL,
                    explanation TEXT
                )
                """)
                
                # Insert the existing data back
                cursor.executemany("""
                INSERT INTO challenge (id, difficulty, date_created, created_by, title, options, correct_answer_id, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, existing_data)
                
                conn.commit()
                print(f"Migration completed successfully! Migrated {len(existing_data)} records.")
            else:
                print("Column 'explaination' not found, database might already be migrated.")
                
        except Exception as e:
            print(f"Error during migration: {e}")
            print("Restoring from backup...")
            conn.close()
            shutil.copy2(backup_path, db_path)
            return False
        finally:
            conn.close()
    else:
        print("No existing database found, new database will be created with correct schema.")
    
    return True

if __name__ == "__main__":
    migrate_database()
