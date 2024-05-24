from aes import encryptData, decryptData, generateKeyFromString, generateRandomKey, AESImplementation,AES
import base64
import os
import zlib

def save_encrypted_data(filename, data, key):
    encrypted_data = encryptData(key, data)
    print("encrypted data: ", encrypted_data)
    with open(filename, 'wb') as file:
        file.write(encrypted_data.encode())

def load_and_decrypt_data(filename, key):
    with open(filename, 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = decryptData(key, encrypted_data.decode())
    return decrypted_data



def encryptFile(inp,output):
    if os.path.exists(inp) == False:
        print("File không tồn tại")
        return
    if os.path.exists(output):
        os.remove(output)

    password = input("Nhập mật khẩu: ")
    key = generateKeyFromString(password)
    with open(inp, 'rb') as file:
        with open(output, 'ab') as out:
            data = file.read()
            data = base64.b64encode(data)
            encryptedData = encryptData(key, data.decode())
            out.write(zlib.compress(encryptedData.encode()))

def decryptDataInFile(inp,output):
    password = input("Nhập mật khẩu: ")
    key = generateKeyFromString(password)
    with open(inp, 'rb') as file:

        data = zlib.decompress(file.read()).decode()
        des = decryptData(key, data)
        des = base64.b64decode(des)

        with open(output, 'wb') as out:
            out.write(des)

def decryptFile(inp, output):
    if os.path.exists(inp) == False:
        print("File không tồn tại")
        return
    if os.path.exists(output):
        # Nếu file tồn tại, thì xóa nó
        os.remove(output)


    input("Nhấn enter để giải mã file...")
    #decryptDataInFile(inp, output)
    while True:
        try:
            decryptDataInFile(inp, output)
            break
        except:
            print("Mật khẩu không đúng, vui lòng nhập lại")
            continue


def test1():
    #key = generateKeyFromString('mysecretkey1234')
    filename = 'encrypted_data.dat'

    # Nhập dữ liệu từ người dùng và lưu trữ nó đã mã hóa
    data_to_save = input("Nhập chuỗi cần lưu mã hóa: ")
    password = input("Nhập mật khẩu mã hóa: ")
    key = generateKeyFromString(password)
    save_encrypted_data(filename, data_to_save, key)
    print("Dữ liệu đã được mã hóa và lưu trữ vào file.")

    #Đọc và giải mã dữ liệu khi cần thiết
    input("Nhấn Enter để đọc và giải mã dữ liệu từ file...")

    while True:
        password2 = input("Nhập mật khẩu giải mã: ")
        key2 = generateKeyFromString(password2)
        try:
            loaded_data = load_and_decrypt_data(filename, key2)
            print(f"Dữ liệu sau khi giải mã: {loaded_data}")
            return
        except:
            print("Mật khẩu không đúng, vui lòng nhập lại")


if __name__ == "__main__":
    # đọc tin nhắn, mã hóa và lưu vào file
    #test1()

    # mã hóa và giải mã file ảnh jpg
    encryptFile('box.jpg', 'aqq.aes')
    decryptFile('aqq.aes', 'aqq.jpg')
