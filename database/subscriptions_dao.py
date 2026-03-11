# Этот файл оставлен для обратной совместимости, но фактически использует users_dao
from .users_dao import is_subscribed, toggle_subscription, get_subscribed_users

# Можно добавить комментарий о том, что подписки теперь в таблице users
__all__ = ['is_subscribed', 'toggle_subscription', 'get_subscribed_users']