"""
Скрипт для создания и инициализации базы данных антифрод системы.
Учебный проект Security Dashboard
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import getpass

# Конфигурация подключения к PostgreSQL
def get_postgres_config():
    """Получение конфигурации PostgreSQL."""
    host = os.environ.get('DB_HOST', 'localhost')
    port = os.environ.get('DB_PORT', '5432')
    user = os.environ.get('POSTGRES_USER', 'postgres')
    password = os.environ.get('POSTGRES_PASSWORD')
    
    if not password:
        print(f"\nВведите пароль для пользователя '{user}' PostgreSQL:")
        password = getpass.getpass("Пароль: ")
    
    return {
        'host': host,
        'user': user,
        'password': password,
        'port': port
    }

POSTGRES_CONFIG = None

# Конфигурация целевой базы данных
DB_NAME = 'antifraud_p2p'
DB_USER = 'antifraud_user'
DB_PASSWORD = 'antifraud_pass'


def create_database_and_user():
    """Создание базы данных и пользователя."""
    print("=" * 60)
    print("Создание базы данных антифрод системы")
    print("=" * 60)
    
    try:
        # Подключение к PostgreSQL как суперпользователь
        print(f"\n[1/4] Подключение к PostgreSQL ({POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']})...")
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        print("      ✓ Подключение успешно")
        
        # Проверка существования базы данных
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()
        
        if exists:
            print(f"\n[2/4] База данных '{DB_NAME}' уже существует")
            # Удаляем и создаём заново для чистой установки
            print(f"      Удаление существующей базы данных...")
            
            # Отключаем всех пользователей от базы
            cursor.execute(f"""
                SELECT pg_terminate_backend(pid) 
                FROM pg_stat_activity 
                WHERE datname = '{DB_NAME}' AND pid <> pg_backend_pid()
            """)
            cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
            print(f"      ✓ База данных удалена")
        
        # Создание базы данных
        print(f"\n[2/4] Создание базы данных '{DB_NAME}'...")
        cursor.execute(f"CREATE DATABASE {DB_NAME} ENCODING 'UTF8'")
        print(f"      ✓ База данных создана")
        
        # Создание пользователя
        print(f"\n[3/4] Создание пользователя '{DB_USER}'...")
        cursor.execute(f"SELECT 1 FROM pg_roles WHERE rolname = '{DB_USER}'")
        user_exists = cursor.fetchone()
        
        if user_exists:
            print(f"      Пользователь уже существует, обновляем пароль...")
            cursor.execute(f"ALTER USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}'")
        else:
            cursor.execute(f"CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}'")
        
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER}")
        print(f"      ✓ Пользователь настроен")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        # Обработка ошибок PostgreSQL с учётом кодировки
        error_msg = str(e.args[0]) if e.args else str(e)
        try:
            error_msg = error_msg.encode('latin-1').decode('utf-8')
        except:
            pass
        print(f"\n❌ Ошибка PostgreSQL: {error_msg}")
        return False
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False


def init_schema():
    """Инициализация схемы базы данных."""
    print(f"\n[4/4] Инициализация схемы и загрузка тестовых данных...")
    
    try:
        # Подключение к созданной базе данных
        conn = psycopg2.connect(
            host=POSTGRES_CONFIG['host'],
            database=DB_NAME,
            user=POSTGRES_CONFIG['user'],
            password=POSTGRES_CONFIG['password'],
            port=POSTGRES_CONFIG['port']
        )
        cursor = conn.cursor()
        
        # Чтение SQL-скрипта
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sql_file = os.path.join(script_dir, 'init_db.sql')
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Выполнение SQL-скрипта
        cursor.execute(sql_script)
        conn.commit()
        
        # Выдача прав пользователю
        cursor.execute(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {DB_USER}")
        cursor.execute(f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {DB_USER}")
        conn.commit()
        
        # Проверка созданных таблиц
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print(f"      ✓ Создано таблиц: {len(tables)}")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"        - {table[0]}: {count} записей")
        
        cursor.close()
        conn.close()
        
        return True
        
    except FileNotFoundError:
        print(f"      ❌ Файл init_db.sql не найден")
        return False
    except psycopg2.Error as e:
        print(f"      ❌ Ошибка PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"      ❌ Ошибка: {e}")
        return False


def main():
    """Основная функция."""
    global POSTGRES_CONFIG
    
    print("\n" + "=" * 60)
    print("  АНТИФРОД СИСТЕМА P2P - НАСТРОЙКА БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    # Получение конфигурации
    POSTGRES_CONFIG = get_postgres_config()
    
    # Вывод конфигурации
    print(f"\nКонфигурация:")
    print(f"  PostgreSQL: {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}")
    print(f"  Пользователь: {POSTGRES_CONFIG['user']}")
    print(f"  Целевая БД: {DB_NAME}")
    print(f"  Пользователь БД: {DB_USER}")
    
    # Создание базы данных и пользователя
    if not create_database_and_user():
        print("\n❌ Не удалось создать базу данных")
        print("\nПроверьте:")
        print("  1. PostgreSQL запущен и доступен")
        print("  2. Учётные данные postgres корректны")
        print("  3. Пользователь имеет права на создание БД")
        return False
    
    # Инициализация схемы
    if not init_schema():
        print("\n❌ Не удалось инициализировать схему")
        return False
    
    print("\n" + "=" * 60)
    print("  ✅ БАЗА ДАННЫХ УСПЕШНО СОЗДАНА!")
    print("=" * 60)
    print(f"\nПодключение к базе данных:")
    print(f"  Host: {POSTGRES_CONFIG['host']}")
    print(f"  Port: {POSTGRES_CONFIG['port']}")
    print(f"  Database: {DB_NAME}")
    print(f"  User: {DB_USER}")
    print(f"  Password: {DB_PASSWORD}")
    print("\nТеперь можно запустить приложение: python app.py")
    print("=" * 60 + "\n")
    
    return True


if __name__ == '__main__':
    main()
