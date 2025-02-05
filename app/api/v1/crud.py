from app.core.database import Database
from app.api.v1.schemas import UserCreate
from app.api.v1.exceptions import UserAlreadyExistsException, UserNotFoundException

from app.core.logging import logger
from app.api.common.hashing import hash_password

async def create_user(db: Database, user: UserCreate) -> dict:
    """
    Создание нового пользователя.
    """
    query_check = "SELECT id FROM users WHERE email = %s"
    existing_user = await db.fetch(query_check, user.email)
    
    if existing_user:
        logger.error(f"Пользователь с email {user.email} уже существует.")
        raise UserAlreadyExistsException(user.email)

    hashed_password = hash_password(user.password)

    query_create = """
    INSERT INTO users (username, email, password)
    VALUES (%s, %s, %s)
    """
    try:
        user_id = await db.execute(query_create, user.username, user.email, hashed_password)
        logger.success(f"Пользователь {user.username} успешно создан с ID {user_id}.")
        return {"id": user_id, "username": user.username, "email": user.email}
    except Exception as e:
        logger.error(f"Ошибка при создании пользователя: {e}")
        raise

async def get_user_by_id(db: Database, user_id: int) -> dict:
    """
    Получение данных пользователя по его ID.
    """
    query = "SELECT id, username, email FROM users WHERE id = %s"
    try:
        users = await db.fetch(query, user_id)
        if not users:
            logger.error(f"Пользователь с ID {user_id} не найден.")
            raise UserNotFoundException(user_id)
        
        user = users[0]
        logger.info(f"Информация о пользователе с ID {user_id} успешно получена.")
        return {"id": user["id"], "username": user["username"], "email": user["email"]}
    except UserNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Неизвестная ошибка при запросе данных пользователя с ID {user_id}: {e}")
        raise