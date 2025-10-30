from typing import Optional, List
import logging
from server.database.base import DatabaseManager
from server.models.user import UserInDB, UserCreate, UserRole, UserManager
from server.utils.data_utils import prepare_user_data

logger = logging.getLogger(__name__)


class UserRepository:

    def __init__(self, db: DatabaseManager):
        self.db = db

    async def initialize(self):
        await self._init_tables()

    async def _init_tables(self):
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            full_name VARCHAR(100),
            hashed_password VARCHAR(255) NOT NULL,
            role ENUM('guest', 'user', 'admin') DEFAULT 'user',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """

        try:
            await self.db.execute(create_users_table)
            logger.info("Users table initialized")

            await self._ensure_admin_user()

        except Exception as e:
            logger.warning(f"Table initialization warning: {e}")

    async def _ensure_admin_user(self):
        admin_email = "admin@marketplace.com"
        admin_password = "admin123"

        try:
            existing_admin = await self.get_by_email(admin_email)
            if existing_admin:
                logger.info("Admin user already exists")
                return

            admin_user = UserCreate(
                username="admin",
                email=admin_email,
                full_name="System Administrator",
                password=admin_password
            )

            result = await self.create(admin_user, UserRole.ADMIN)
            if result:
                logger.info("Default admin user created")
            else:
                logger.error("Failed to create default admin user")

        except Exception as e:
            logger.error(f"Error ensuring admin user: {e}")

    async def create(self, user: UserCreate, role: UserRole = UserRole.USER) -> Optional[UserInDB]:
        hashed_password = UserManager.hash_password(user.password)

        query = """
        INSERT INTO users (username, email, full_name, hashed_password, role)
        VALUES (%(username)s, %(email)s, %(full_name)s, %(hashed_password)s, %(role)s)
        """

        params = {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "hashed_password": hashed_password,
            "role": role
        }

        try:
            result = await self.db.execute(query, params)
            if result:
                return await self.get_by_email(user.email)
        except Exception as e:
            logger.error(f"Error creating user {user.username}: {e}")
        return None

    async def get_by_id(self, user_id: int) -> Optional[UserInDB]:
        query = "SELECT * FROM users WHERE id = %(id)s"
        try:
            result = await self.db.fetch_one(query, {"id": user_id})
            if result:
                prepared_data = prepare_user_data(result)
                return UserInDB(**prepared_data)
        except Exception as e:
            logger.error(f"Error getting user by id {user_id}: {e}")
        return None

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        query = "SELECT * FROM users WHERE email = %(email)s"
        try:
            result = await self.db.fetch_one(query, {"email": email})
            if result:
                prepared_data = prepare_user_data(result)
                return UserInDB(**prepared_data)
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
        return None

    async def get_by_username(self, username: str) -> Optional[UserInDB]:
        query = "SELECT * FROM users WHERE username = %(username)s"
        try:
            result = await self.db.fetch_one(query, {"username": username})
            if result:
                prepared_data = prepare_user_data(result)
                return UserInDB(**prepared_data)
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
        return None

    async def authenticate(self, email: str, password: str) -> Optional[UserInDB]:
        try:
            user = await self.get_by_email(email)
            if user and UserManager.verify_password(password, user.hashed_password):
                return user
            elif user:
                logger.warning(f"Password verification failed for {email}")
            else:
                logger.warning(f"User not found: {email}")
        except Exception as e:
            logger.error(f"Authentication error for {email}: {e}")
        return None

    async def get_all(self) -> List[UserInDB]:
        query = "SELECT * FROM users WHERE is_active = TRUE"
        try:
            results = await self.db.fetch_all(query)
            users = []
            for result in results:
                try:
                    prepared_data = prepare_user_data(result)
                    users.append(UserInDB(**prepared_data))
                except Exception as e:
                    logger.error(f"Error parsing user data: {e}")
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    async def update_role(self, user_id: int, new_role: UserRole) -> bool:
        query = "UPDATE users SET role = %(role)s WHERE id = %(id)s"
        try:
            result = await self.db.execute(query, {"role": new_role, "id": user_id})
            return result > 0
        except Exception as e:
            logger.error(f"Error updating user role {user_id}: {e}")
            return False

    async def get_user_count(self) -> int:
        query = "SELECT COUNT(*) as count FROM users"
        try:
            result = await self.db.fetch_one(query)
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            return 0
