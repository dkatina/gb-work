from werkzeug.security import generate_password_hash

hashed = generate_password_hash("password123")
print("Hashed password:", hashed)
