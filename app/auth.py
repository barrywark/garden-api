from app.api.users import fastapi_users

current_user = fastapi_users.current_user()
current_active_user = fastapi_users.current_user(active=True)