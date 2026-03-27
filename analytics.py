"""
Запусти этот файл чтобы увидеть статистику бота:
python3 analytics.py
"""
import sqlite3
from datetime import datetime, timedelta


def get_connection():
    return sqlite3.connect("supplements.db")


def show_stats():
    conn = get_connection()
    cursor = conn.cursor()

    print("=" * 50)
    print("📊 СТАТИСТИКА БОТА")
    print("=" * 50)

    # Всего запросов
    cursor.execute("SELECT COUNT(*) FROM search_logs")
    total = cursor.fetchone()[0]
    print(f"\n🔍 Всего поисковых запросов: {total}")

    # Уникальных пользователей
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM search_logs")
    users = cursor.fetchone()[0]
    print(f"👤 Уникальных пользователей: {users}")

    # Запросы за последние 7 дней
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM search_logs WHERE created_at >= ?", (week_ago,))
    week_total = cursor.fetchone()[0]
    print(f"📅 Запросов за 7 дней: {week_total}")

    # Топ-20 запросов
    print("\n🔥 ТОП-20 ЗАПРОСОВ:")
    cursor.execute("""
        SELECT query, COUNT(*) as cnt, SUM(found) as found_cnt
        FROM search_logs
        GROUP BY LOWER(query)
        ORDER BY cnt DESC
        LIMIT 20
    """)
    for i, (query, cnt, found) in enumerate(cursor.fetchall(), 1):
        status = "✅" if found else "❌"
        print(f"  {i:2}. {status} «{query}» — {cnt} раз")

    # Запросы без результата (что нужно добавить в базу)
    print("\n❌ НЕ НАЙДЕНО (добавь в базу!):")
    cursor.execute("""
        SELECT query, COUNT(*) as cnt
        FROM search_logs
        WHERE found = 0
        GROUP BY LOWER(query)
        ORDER BY cnt DESC
        LIMIT 15
    """)
    rows = cursor.fetchall()
    if rows:
        for query, cnt in rows:
            print(f"  • «{query}» — искали {cnt} раз")
    else:
        print("  Пока нет ненайденных запросов")

    # Запросы за сегодня
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT query, found FROM search_logs
        WHERE created_at >= ?
        ORDER BY created_at DESC
        LIMIT 20
    """, (today,))
    rows = cursor.fetchall()
    if rows:
        print(f"\n📌 ЗАПРОСЫ СЕГОДНЯ ({today}):")
        for query, found in rows:
            status = "✅" if found else "❌"
            print(f"  {status} {query}")

    conn.close()
    print("\n" + "=" * 50)


if __name__ == "__main__":
    show_stats()
