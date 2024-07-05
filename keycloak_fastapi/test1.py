from core.settings import load_settings

db_settings = load_settings("DatabaseSettings")
auth_settings = load_settings("AuthSettings")

print(db_settings)
print(auth_settings)