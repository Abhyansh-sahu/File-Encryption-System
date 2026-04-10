import shutil
import os
import mysql.connector
import random
currsor = mysql.connector.connect(host="localhost", user="root", password="password", database="encry_registration")
cursor = currsor.cursor()
def login():
    print("Welcome to the login page!")
    email=input("Please enter your email: ")
    password=input("Please enter your password: ")
    cursor.execute("SELECT * FROM data WHERE Email = %s AND Password = %s", (email, password))
    result = cursor.fetchone()
    if result:
        print(f"Welcome, {result[1]}!")
        while True:
            print("Press 1 to encrypt a new file or press 2 for decrypting an encrypted file else press any key to exit.")
            if input() == "1":
                new_file()
            elif input() == "2":
                open_file()
            else:
                print("Thank you for using the encryption program! Goodbye!")
                break
    else:
        print("Invalid email or password. Please try again.")
def registration():
    print("Welcome to the registration page!")
    name=input("Please enter your name: ")
    cursor.execute("SELECT Email FROM data")
    result = [i[0] for i in cursor.fetchall()]
    while True:
        email=input("Please enter your email: ")
        if email in result:
            print("Email already exists. Please enter a different email.")
            continue
        index=email.index("@")
        if "@gmail.com" in email[index:]:
            break
        else:
            print("Invalid email format. Please enter a valid Gmail address.")
    password=input("Please enter your password: ")
    print(f"Thank you, {name}! Your account has been created.")
    cursor.execute("INSERT INTO data (  Name, Email, Password) VALUES (%s, %s, %s)", (name, email, password))
    currsor.commit()
    return 0
def new_file():
    file_path=input("Enter the path of the file to be encrypted: ")
    try:
        with open(file_path, 'r') as file:
            data = file.readlines()
            file_name =os.path.basename(file_path).replace(".", "_").replace(" ", "_")
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {file_name} (letter VARCHAR(10) PRIMARY KEY, Code VARCHAR(100) UNIQUE, updated_code VARCHAR(100) UNIQUE)""")# file name error same as another table name
            code(data, file_name)
            print(f"File '{file_name}' has been encrypted and stored in the database.")
            # source_path = file_path
            # destination_folder = r"C:\Users\squar\OneDrive\Desktop\encrypted_file"
            # os.makedirs(destination_folder, exist_ok=True)
            # destination_path = os.path.join(destination_folder, os.path.basename(file_path))
            # shutil.move(source_path, destination_path)
            return file_name
    except FileNotFoundError:
        print("File not found. Please check the path and try again.")
def updated_code():
    file_name=input("Enter the name of the file to retrieve the updated code: ")
    cursor.execute("Show tables")
    table=cursor.fetchall()
    if (file_name,) in table:
        char=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '"', '#', 
            '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', 
            ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~',' ']
        cursor.execute(f"SELECT letter FROM {file_name}")
        data=cursor.fetchall()
        for i in data:
                while True:
                    code=''.join(random.choices(char, k=3))
                    cursor.execute(f"SELECT updated_code FROM {file_name}")
                    result = cursor.fetchall()
                    if (code,) not in result:
                        cursor.execute(f"UPDATE {file_name} SET updated_code = %s WHERE letter = %s", (code, i[0]))
                        currsor.commit()
                        break
    with open(f"{file_name}_1.txt", 'a') as file:
            cursor.execute(f"SELECT letter, updated_code FROM {file_name}")
            result = cursor.fetchall()
            for i in data:
                for j in i:
                    if j == " ":
                        file.write("\n")
                    else:
                        for k in result:
                            if j == k[0]:
                                file.write(k[1])
                                break
def open_file():
    file_name = input("Enter the name of the file to be decrypted: ")
    cursor.execute("SHOW TABLES")
    table = cursor.fetchall()
    if (file_name,) in table:
        cursor.execute(f"SELECT letter, updated_code FROM {file_name}")
        result = cursor.fetchall()
        decrypt_dict = {code: letter for letter, code in result}
        with open(f"{file_name}_1.txt", 'r') as file:
            data = file.read()
        words = data.split()
        output_file = f"{file_name}_decrypted.txt"
        with open(output_file, 'w') as decrypted_file:
            for word in words:
                if word in decrypt_dict:
                    decrypted_file.write(decrypt_dict[word])
                else:
                    decrypted_file.write("?")

        print(f"File '{file_name}' decrypted successfully.")
        os.startfile(output_file)
    else:
        print("File not found in database.")
def code(data, file_name):
    l=[]
    char=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
          'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 
          'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
          'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 
          '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '"', '#', 
          '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', 
          ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~',' ']
    for i in data:
        for j in i:
            if j in char and j not in l:
                l.append(j)
                while True:
                    code=''.join(random.choices(char, k=3))
                    cursor.execute(f"SELECT updated_code FROM {file_name}")
                    result = cursor.fetchall()
                    if (code,) not in result:
                        cursor.execute(f"INSERT INTO {file_name} (letter, Code, updated_code) VALUES (%s, %s, %s)", (j, code, code))
                        currsor.commit()
                        break
    cursor.execute(f"SELECT letter, Code FROM {file_name}")
    result = cursor.fetchall()
    with open(f"{file_name}_1.txt", 'a') as file:
        for i in data:
            for j in i:
                if j == " ":
                    file.write("\n")
                else:
                    for k in result:
                        if j == k[0]:
                            file.write(k[1])
                            break
def main():
    while True:
        print("Welcome to the encryption program!")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        choice = input("Please enter your choice: ")
        if choice == "1":
            login()
        elif choice == "2":
            registration()
        elif choice == "3":
            print("Thank you for using the encryption program! Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
main()