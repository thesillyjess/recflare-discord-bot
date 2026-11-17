import sqlite3
from datetime import datetime, timezone

class handler:
    def __init__(self):
        self.db = sqlite3.connect('feedback.db')
        cursor = self.db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discordAccountId TEXT NOT NULL,
                feedbackString TEXT,
                dateLeft TEXT NOT NULL,
                guildIdFrom TEXT NOT NULL
            )
        """)
        self.db.commit()

    def shutdown(self):
        self.db.commit()
        self.db.close()

    def addFeedback(self, userId: int, feedbackString: str, guildIdFrom: int):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO feedback (discordAccountId, feedbackString, dateLeft, guildIdFrom) VALUES (?, ?, ?, ?)",
            (str(userId), feedbackString, datetime.now(timezone.utc).strftime("%d/%m/%Y @ %I:%M %p UTC"), str(guildIdFrom))
        )
        self.db.commit()