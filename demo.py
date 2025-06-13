import bcrypt

password = b"admin#1"
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(hashed)