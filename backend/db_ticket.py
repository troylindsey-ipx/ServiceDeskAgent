import sqlite3
from typing import Optional
from dataclasses import dataclass
from contextlib import contextmanager

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

    def create_ticket(self, inc: str, first: str, last: str, comp_name: str, bldg: str, issue: str) -> Ticket:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tickets (inc, first, last, comp_name, bldg, issue) VALUES (?, ?, ?, ?, ?, ?)",
                (inc, first, last, comp_name, bldg, issue)
            )
            conn.commit()
            return Ticket(inc=inc, first=first, last=last, comp_name=comp_name, bldg=bldg, issue=issue)

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
                issue=[5]
            )
