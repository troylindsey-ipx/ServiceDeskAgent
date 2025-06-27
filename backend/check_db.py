#!/usr/bin/env python3
"""
Simple script to check the database contents and location
"""
import os
import sqlite3
from db_ticket import DatabaseTicket

def main():
    print("=== Database Check ===")
    
    # Check current working directory
    print(f"Current working directory: {os.getcwd()}")
    
    # Initialize database
    db = DatabaseTicket()
    print(f"Database path: {db.db_path}")
    print(f"Full database path: {os.path.abspath(db.db_path)}")
    
    # Check if database file exists
    if os.path.exists(db.db_path):
        print(f"✅ Database file exists")
        print(f"File size: {os.path.getsize(db.db_path)} bytes")
    else:
        print(f"❌ Database file does not exist")
        return
    
    # Connect and check table structure
    try:
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if tickets table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tickets'")
            if cursor.fetchone():
                print("✅ Tickets table exists")
                
                # Get table schema
                cursor.execute("PRAGMA table_info(tickets)")
                columns = cursor.fetchall()
                print("Table schema:")
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
                
                # Count total tickets
                cursor.execute("SELECT COUNT(*) FROM tickets")
                count = cursor.fetchone()[0]
                print(f"Total tickets in database: {count}")
                
                # Show all tickets if any exist
                if count > 0:
                    cursor.execute("SELECT * FROM tickets ORDER BY inc")
                    tickets = cursor.fetchall()
                    print("\nAll tickets:")
                    for ticket in tickets:
                        print(f"  INC: {ticket[0]}, Name: {ticket[1]} {ticket[2]}, Computer: {ticket[3]}, Building: {ticket[4]}")
                        print(f"       Issue: {ticket[5]}")
                else:
                    print("No tickets found in database")
                    
            else:
                print("❌ Tickets table does not exist")
                
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    main()
