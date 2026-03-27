import sqlite3


def get_connection():
    """Возвращает соединение с базой данных"""
    return sqlite3.connect("supplements.db")


def init_db():
    """Создаёт таблицы если их нет"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS supplements (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            name_en     TEXT,
            category    TEXT DEFAULT 'bio',
            description TEXT,
            ingredients TEXT,
            benefits    TEXT,
            dosage      TEXT,
            available_ru INTEGER DEFAULT 1,
            sanctions_note TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS symptom_cards (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            symptom      TEXT NOT NULL UNIQUE,
            emoji        TEXT DEFAULT '🔍',
            causes       TEXT,
            advice       TEXT,
            supplement_names TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_logs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            query      TEXT,
            found      INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("База данных готова!")


def search_supplements(query: str) -> list:
    """Поиск добавок по названию, ингредиентам или пользе"""
    conn = get_connection()
    cursor = conn.cursor()
    q = f"%{query.lower()}%"
    cursor.execute("""
        SELECT name, category, description, ingredients, benefits, dosage,
               available_ru, sanctions_note
        FROM supplements
        WHERE LOWER(name) LIKE ?
           OR LOWER(name_en) LIKE ?
           OR LOWER(ingredients) LIKE ?
           OR LOWER(benefits) LIKE ?
        LIMIT 5
    """, (q, q, q, q))
    results = cursor.fetchall()
    conn.close()
    return results


def search_by_ingredient(ingredient: str) -> list:
    """Поиск всех добавок содержащих конкретный ингредиент"""
    conn = get_connection()
    cursor = conn.cursor()
    q = f"%{ingredient.lower()}%"
    cursor.execute("""
        SELECT name, category, ingredients, benefits, available_ru
        FROM supplements
        WHERE LOWER(ingredients) LIKE ?
        ORDER BY name
    """, (q,))
    results = cursor.fetchall()
    conn.close()
    return results


def get_all_symptoms() -> list:
    """Получить все симптомы для меню"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT symptom, emoji FROM symptom_cards ORDER BY symptom")
    results = cursor.fetchall()
    conn.close()
    return results


def get_symptom_card(symptom: str) -> tuple | None:
    """Получить карточку симптома"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT symptom, emoji, causes, advice, supplement_names
        FROM symptom_cards WHERE symptom = ?
    """, (symptom,))
    result = cursor.fetchone()
    conn.close()
    return result


def log_search(user_id: int, query: str, found: bool):
    """Логируем каждый поиск"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO search_logs (user_id, query, found) VALUES (?, ?, ?)",
        (user_id, query, 1 if found else 0)
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
