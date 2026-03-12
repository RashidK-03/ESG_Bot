import sqlite3

DB_NAME = "esg_updates.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS updates (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id   TEXT    NOT NULL,
            source    TEXT,
            title     TEXT,
            link      TEXT,
            published TEXT,
            UNIQUE(chat_id, link)   -- каждый пользователь видит каждую новость один раз
        )
    """)

    conn.commit()
    conn.close()


def save_update(chat_id: str, source: str, title: str, link: str, published: str) -> bool:
    """
    Сохраняет новость для конкретного пользователя.
    Возвращает True если новость новая, False если уже была.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO updates (chat_id, source, title, link, published)
            VALUES (?, ?, ?, ?, ?)
        """, (str(chat_id), source, title, link, published))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()