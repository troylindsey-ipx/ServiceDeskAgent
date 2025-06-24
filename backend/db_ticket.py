import sqlite3
from typing import Optional
from dataclasses import dataclass
from contextlib import contextmanager
import random

@dataclass
class Ticket:
    inc: str
    first: str
    last: str
    comp_name: str
    bldg: str
    issue: str

class DatabaseTicket:
    def __init__(self, db_path: str = "auto_db.sqlite"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create tickets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    inc TEXT PRIMARY KEY,
                    first TEXT NOT NULL,
                    last TEXT NOT NULL,
                    comp_name TEXT NOT NULL,
                    bldg TEXT NOT NULL,
                    issue TEXT NOT NULL
                )
            """)
            conn.commit()

    def _generate_incident_number(self) -> str:
        """Generate a unique incident number in format INC######"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get the highest existing incident number that follows INC###### format
            cursor.execute("SELECT inc FROM tickets WHERE inc LIKE 'INC%' AND LENGTH(inc) = 9 ORDER BY inc DESC LIMIT 1")
            row = cursor.fetchone()
            
            if row:
                try:
                    # Extract the numeric part and increment by random amount
                    last_inc = row[0]
                    numeric_part = last_inc[3:]  # Remove "INC" prefix
                    
                    # Validate that the numeric part is actually numeric
                    if numeric_part.isdigit() and len(numeric_part) == 6:
                        last_number = int(numeric_part)
                        # Increment by random amount between 1 and 100
                        new_number = last_number + random.randint(1, 100)
                    else:
                        # If existing format is invalid, start fresh
                        new_number = random.randint(100000, 999999)
                except (ValueError, IndexError):
                    # If any error parsing existing numbers, start fresh
                    new_number = random.randint(100000, 999999)
            else:
                # Start with a random 6-digit number
                new_number = random.randint(100000, 999999)
            
            # Ensure it's 6 digits
            new_number = max(100000, new_number)
            if new_number > 999999:
                new_number = 999999
            
            return f"INC{new_number:06d}"

    def create_ticket(self, inc: str, first: str, last: str, comp_name: str, bldg: str, issue: str) -> Ticket:
        print(f"DB: Creating ticket with data: first={first}, last={last}, comp_name={comp_name}, bldg={bldg}, issue={issue}")
        print(f"DB: Database path: {self.db_path}")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Generate a unique incident number (ignore the provided inc parameter)
            generated_inc = self._generate_incident_number()
            print(f"DB: Generated incident number: {generated_inc}")
            
            # Ensure uniqueness (in case of collision)
            while True:
                cursor.execute("SELECT inc FROM tickets WHERE inc = ?", (generated_inc,))
                if not cursor.fetchone():
                    break
                # If collision, generate a new one
                generated_inc = self._generate_incident_number()
                print(f"DB: Collision detected, new incident number: {generated_inc}")
            
            try:
                cursor.execute(
                    "INSERT INTO tickets (inc, first, last, comp_name, bldg, issue) VALUES (?, ?, ?, ?, ?, ?)",
                    (generated_inc, first, last, comp_name, bldg, issue)
                )
                conn.commit()
                print(f"DB: Ticket inserted successfully with INC: {generated_inc}")
                
                # Verify the insert worked
                cursor.execute("SELECT COUNT(*) FROM tickets WHERE inc = ?", (generated_inc,))
                count = cursor.fetchone()[0]
                print(f"DB: Verification - Found {count} tickets with INC: {generated_inc}")
                
                return Ticket(inc=generated_inc, first=first, last=last, comp_name=comp_name, bldg=bldg, issue=issue)
                
            except Exception as e:
                print(f"DB: Error inserting ticket: {e}")
                raise

    def get_ticket_by_inc(self, inc: str) -> Optional[Ticket]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tickets WHERE inc = ?", (inc,))
            row = cursor.fetchone()
            if not row:
                return None
            
            return Ticket(
                inc=row[0],
                first=row[1],
                last=row[2],
                comp_name=row[3],
                bldg=row[4],
                issue=row[5]
            )
