import mysql.connector
from mysql.connector import Error


def check_mysql_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='marketplace_user',
            password='marketplace_pass',
            database='marketplace_db'
        )

        if connection.is_connected():
            print("MySQL connection successful!")

            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            print(f"Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table[0]}")

            cursor.execute("SELECT id, username, email, role FROM users")
            users = cursor.fetchall()

            print(f"Found {len(users)} users:")
            for user in users:
                print(f"   - {user[1]} ({user[2]}) - {user[3]}")

            cursor.close()
            connection.close()
            return True

    except Error as e:
        print(f"MySQL connection error: {e}")
        return False


def check_database_exists():
    """Проверка существования базы данных"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',  # или ваш пользователь
            password=''  # укажите пароль если есть
        )

        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]

        if 'marketplace_db' in databases:
            print("✅ Database 'marketplace_db' exists")
        else:
            print("❌ Database 'marketplace_db' does not exist")
            print("Available databases:", databases)

        cursor.close()
        connection.close()

    except Error as e:
        print(f"❌ Error checking databases: {e}")


if __name__ == "__main__":
    print("🔍 Checking database configuration...")
    check_database_exists()
    print("\n🔍 Testing MySQL connection...")
    check_mysql_connection()