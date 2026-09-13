import sqlite3

class Database:
    """Provide access to the application's database."""

    def __init__(self, database: str):
        """Initialize a database instance with the given database path."""
        self.database = database

    def get_connection(self) -> sqlite3.Connection:
        """Create and return a connection to the database."""
        db = sqlite3.connect(self.database)
        db.row_factory = sqlite3.Row
        return db

    def init(self):
        """Initialize the database and create the required tables."""
        db = self.get_connection()

        try:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS licenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_key TEXT UNIQUE NOT NULL,
                    user TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1
                )
                """
            )

            db.commit()
        finally:
            db.close()


def create_database(database: str = "licenses.db") -> Database:
    """Create and return a configured database instance."""
    return Database(database)
