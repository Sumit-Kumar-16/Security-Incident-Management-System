from werkzeug.security import generate_password_hash


password =input("Enter your password which you want to decrypt: ")

decrypt =generate_password_hash(password)

print(decrypt)

