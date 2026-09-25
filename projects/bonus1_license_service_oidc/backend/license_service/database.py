import sqlite3


class Database:
    """Provide access to the application's database."""

    def __init__(self, database: str):
        self.database = database

    def get_connection(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.database)
        db.row_factory = sqlite3.Row
        return db

    def save_license(
        self,
        cloudsmith_token: str,
        expires_at: str,
        user: str,
        keycloak_subject: str,
        entitlement_id: str | None = None,
        token_slug_perm: str | None = None,
    ) -> None:
        db = self.get_connection()
        try:
            db.execute(
                """
                INSERT INTO licenses (
                    cloudsmith_token, expires_at, user, keycloak_subject,
                    cloudsmith_entitlement_id, cloudsmith_token_slug_perm
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(cloudsmith_token) DO UPDATE SET
                    expires_at = excluded.expires_at,
                    user = excluded.user,
                    keycloak_subject = excluded.keycloak_subject,
                    cloudsmith_entitlement_id = excluded.cloudsmith_entitlement_id,
                    cloudsmith_token_slug_perm = excluded.cloudsmith_token_slug_perm,
                    active = 1,
                    revoked_at = NULL
                """,
                (
                    cloudsmith_token,
                    expires_at,
                    user,
                    keycloak_subject,
                    entitlement_id,
                    token_slug_perm,
                ),
            )
            db.commit()
        finally:
            db.close()

    def get_latest_active_license(self) -> sqlite3.Row | None:
        db = self.get_connection()
        try:
            return db.execute(
                """
                  SELECT cloudsmith_token, user, expires_at,
                      cloudsmith_token_slug_perm
                FROM licenses
                WHERE active = 1
                ORDER BY expires_at DESC, id DESC
                LIMIT 1
                """
            ).fetchone()
        finally:
            db.close()

    def get_license(self, cloudsmith_token: str) -> sqlite3.Row | None:
        db = self.get_connection()
        try:
            return db.execute(
                """
                SELECT user, active, expires_at
                    , keycloak_subject, cloudsmith_entitlement_id
                FROM licenses
                WHERE cloudsmith_token = ?
                """,
                (cloudsmith_token,),
            ).fetchone()
        finally:
            db.close()

    def revoke_license(self, cloudsmith_token: str) -> sqlite3.Row | None:
        """Mark a license revoked and return its ownership metadata."""
        db = self.get_connection()
        try:
            license_row = db.execute(
                """
                SELECT user, keycloak_subject, cloudsmith_entitlement_id, active
                FROM licenses
                WHERE cloudsmith_token = ?
                """,
                (cloudsmith_token,),
            ).fetchone()
            if license_row is None or not license_row["active"]:
                return license_row

            db.execute(
                """
                UPDATE licenses
                SET active = 0, revoked_at = datetime('now')
                WHERE cloudsmith_token = ?
                """,
                (cloudsmith_token,),
            )
            db.commit()
            return license_row
        finally:
            db.close()

    def init(self):
        db = self.get_connection()
        try:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS licenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cloudsmith_token TEXT UNIQUE NOT NULL,
                    expires_at TEXT NOT NULL,
                    user TEXT NOT NULL,
                    keycloak_subject TEXT NOT NULL DEFAULT '',
                    cloudsmith_entitlement_id TEXT,
                    cloudsmith_token_slug_perm TEXT,
                    active INTEGER NOT NULL DEFAULT 1,
                    revoked_at TEXT
                )
                """
            )
            columns = {
                row["name"]
                for row in db.execute("PRAGMA table_info(licenses)").fetchall()
            }
            if "cloudsmith_entitlement_id" not in columns:
                db.execute(
                    "ALTER TABLE licenses ADD COLUMN cloudsmith_entitlement_id TEXT"
                )
            if "cloudsmith_token_slug_perm" not in columns:
                db.execute(
                    "ALTER TABLE licenses ADD COLUMN cloudsmith_token_slug_perm TEXT"
                )
            db.commit()
        finally:
            db.close()


def create_database(database: str = "licenses.db") -> Database:
    return Database(database)
