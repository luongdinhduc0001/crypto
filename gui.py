import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from dac_macs import DACMACS, dacmacs_setup
from maabe_yj14 import MAABE_YJ14, maabe_yj14_setup
from adapter import HybridABEncMA, dabe_setup
from itertools import chain


class User:
    def __init__(self, GID, user_attributes):
        self.GID = GID
        self.user_attributes = user_attributes

    def __str__(self):
        return f"{self.GID}: {self.user_attributes}"


def add_user(GID, user_attributes):
    # if GID in users, replace user_attributes
    # else, add new user
    for user in users:
        if user.GID == GID:
            user.user_attributes = user_attributes
            return
    users.append(User(GID, user_attributes))

def toStr(users):
    res = ""
    for user in users:
        res += str(user) + "\n"
    return res

AAs = []
msg = ""
policy_str = ""
CT = None
users = []
c_user = None
PT = None
abe_scheme = None
scheme_name = ""


def on_closing():
    if messagebox.askokcancel("Thoát", "Bạn có chắc chắn muốn thoát không?"):
        root.destroy()


def str_handler(str):
    if str == "":
        return []
    import re
    text_cleaned = re.sub(r"\s+", " ", str.strip())
    return text_cleaned.strip().upper().split(" ")


def choose_scheme():
    global AAs
    global msg
    global policy_str
    global CT
    global users
    global c_user
    global PT
    global abe_scheme
    global scheme_name

    button1.config(state="normal")
    AAs.clear()
    msg = ""
    policy_str = ""
    CT = None
    users.clear()
    c_user = None
    PT = None

    selected_option = combo.get()
    scheme_name = selected_option
    if selected_option == "DAC-MACS":
        global gpp
        global gmk
        (dac, gpp, gmk) = dacmacs_setup()
        abe_scheme = dac
    elif selected_option == "MA-ABE YJ14":
        global GPP
        global GMK
        (maabe, GPP, GMK) = maabe_yj14_setup()
        abe_scheme = maabe
    elif selected_option == "DABE":
        global gp
        (dabe, gp) = dabe_setup()
        abe_scheme = dabe
    else:
        messagebox.showerror("Lỗi", "Chưa hỗ trợ chức năng này")
        return

    messagebox.showinfo("Thông tin", f"Bạn đã chọn: {selected_option}")


def AAs_setup():
    if scheme_name not in ["DAC-MACS", "MA-ABE YJ14", "DABE"]:
        messagebox.showerror("Lỗi", "Chưa chọn scheme")
        return

    global AAs
    AAs.clear()

    if not entry1.get() and not entry2.get() and not entry3.get():
        messagebox.showerror("Lỗi", "Vui lòng nhập ít nhất một văn bản")
        return

    if entry1.get():
        AAs.append(str_handler(entry1.get()))
    if entry2.get():
        AAs.append(str_handler(entry2.get()))
    if entry3.get():
        AAs.append(str_handler(entry3.get()))

    global authorities
    global authority1
    authorityAttributes = list(chain(*AAs))
    authority1 = "authority1"
    authorities = {}
    button1.config(state="disabled")

    if scheme_name == "DAC-MACS":
        try:
            abe_scheme.setupAuthority(gpp, authority1, authorityAttributes, authorities)
            messagebox.showinfo("Thông tin", f"Đã thiết lập AAs thành công")
            return
        except Exception as e:
            messagebox.showerror("Lỗi", e)
            return

    elif scheme_name == "MA-ABE YJ14":

        try:
            abe_scheme.setupAuthority(GPP, authority1, authorityAttributes, authorities)
            messagebox.showinfo("Thông tin", f"Đã thiết lập AAs thành công")
            return
        except Exception as e:
            messagebox.showerror("Lỗi", e)
            return
    elif scheme_name == "DABE":
        try:
            global dabeSK, dabePK, dabeAllAuthPK
            dabeSK = []
            dabePK = []
            dabeAllAuthPK = {}
            for AA in AAs:
                SK, PK = abe_scheme.authsetup(gp, AA)
                dabeSK.append(SK)
                dabePK.append(PK)
            for PK in dabePK:
                dabeAllAuthPK.update(PK)
            messagebox.showinfo("Thông tin", f"Đã thiết lập AAs thành công")
            return
        except Exception as e:
            messagebox.showerror("Lỗi", e)
            return

    else:
        messagebox.showerror("Lỗi", "Chưa hỗ trợ chức năng này")
        return

    # messagebox.showinfo("Thông tin", f"Danh sách văn bản: {AAs}")


def get_data_and_policy():
    if scheme_name not in ["DAC-MACS", "MA-ABE YJ14", "DABE"]:
        messagebox.showerror("Lỗi", "Chưa chọn scheme")
        return

    if len(AAs) == 0:
        messagebox.showerror("Lỗi", "Chưa thiết lập AAs")
        return

    global msg
    global policy_str
    global CT
    global PT

    CT = None
    PT = None

    msg = entry4.get()
    policy_str = entry5.get()
    if not msg or not policy_str:
        messagebox.showerror("Lỗi", "Vui lòng nhập dữ liệu và quy tắc truy cập")
        return

    if scheme_name == "DAC-MACS":
        try:
            CT = abe_scheme.encrypt(gpp, policy_str, msg.encode(), authorities[authority1])
            messagebox.showinfo("Thông báo", f"Mã hóa dữ liệu thành công CT: {CT}", )
        except Exception as e:
            messagebox.showerror("Lỗi", e)
            return

    elif scheme_name == "MA-ABE YJ14":
        try:
            CT = abe_scheme.encrypt(GPP, policy_str, msg.encode(), authorities[authority1])
            messagebox.showinfo("Thông báo", f"Mã hóa dữ liệu thành công CT: {CT}")
        except Exception as e:
            messagebox.showerror("Lỗi", e)
            return

    elif scheme_name == "DABE":
        try:
            CT = abe_scheme.encrypt(gp, dabeAllAuthPK, msg.encode(), policy_str)
            messagebox.showinfo("Thông báo", f"Mã hóa dữ liệu thành công CT: {CT}")
        except Exception as e:
            messagebox.showerror("Lỗi", e)
            return

    else:
        messagebox.showerror("Lỗi", "Chưa hỗ trợ chức năng này")
        return

    # messagebox.showinfo("Thông tin", f"Dữ liệu: {msg}, quy tắc truy cập: {policy_str}")


def register_user():
    if scheme_name not in ["DAC-MACS", "MA-ABE YJ14", "DABE"]:
        messagebox.showerror("Lỗi", "Chưa chọn scheme")
        return

    if len(AAs) == 0:
        messagebox.showerror("Lỗi", "Chưa thiết lập AAs")
        return

    GID = entry6.get()
    user_attributes = str_handler(entry7.get())

    if not GID or not user_attributes:
        messagebox.showerror("Lỗi", "Vui lòng nhập GID và thuộc tính người dùng")
        return

    add_user(GID, user_attributes)
    if scheme_name == "DAC-MACS":
        global dacmacs_users, label10
        dacmacs_users = {}
        alice = {'id': GID, 'authoritySecretKeys': {}, 'keys': None}

        try:
            alice['keys'], dacmacs_users[alice['id']] = abe_scheme.registerUser(gpp)
            for attr in user_attributes:
                abe_scheme.keygen(gpp, authorities[authority1], attr, dacmacs_users[GID], alice['authoritySecretKeys'])

            messagebox.showinfo("Thông tin", f"Đã đăng ký người dùng thành công")
            label10.config(text=f"{toStr(users)}")
            return
        except Exception as e:
            messagebox.showerror("Lỗi", e)
            return

    elif scheme_name == "MA-ABE YJ14":
        global yj14_users
        yj14_users = {}
        bob = {'id': GID, 'authoritySecretKeys': {}, 'keys': None}

        try:
            bob['keys'], yj14_users[bob['id']] = abe_scheme.registerUser(GPP)
            for attr in user_attributes:
                abe_scheme.keygen(GPP, authorities[authority1], attr, yj14_users[GID], bob['authoritySecretKeys'])
            label10.config(text=f"{toStr(users)}")
            messagebox.showinfo("Thông tin", f"Đã đăng ký người dùng thành công")
            return
        except Exception as e:
            messagebox.showerror("Lỗi", e)
            return

    elif scheme_name == "DABE":
        global dabeUsers, dabeK
        dabeUsers = {}
        dabeK = {}
        eve_gid = GID
        try:
            for i in range(len(AAs)):
                for attr in user_attributes:
                    if attr in AAs[i]:
                        abe_scheme.keygen(gp, dabeSK[i], attr, eve_gid, dabeK)
            messagebox.showinfo("Thông tin", f"Đã đăng ký người dùng thành công")
            label10.config(text=f"{toStr(users)}")
            return
        except Exception as e:
            messagebox.showerror("Lỗi", e)
            return



    else:
        messagebox.showerror("Lỗi", "Chưa hỗ trợ chức năng này")
        return

    messagebox.showinfo("Thông tin", f"GID: {GID}, thuộc tính người dùng: {user_attributes}")


def get_GID():
    if scheme_name not in ["DAC-MACS", "MA-ABE YJ14", "DABE"]:
        messagebox.showerror("Lỗi", "Chưa chọn scheme")
        return

    if len(AAs) == 0:
        messagebox.showerror("Lỗi", "Chưa thiết lập AAs")
        return

    if CT is None:
        messagebox.showerror("Lỗi", "Chưa mã hóa dữ liệu")
        return

    GID = entry8.get()
    if not GID:
        messagebox.showerror("Lỗi", "Vui lòng nhập GID")
        return
    global c_user

    for user in users:
        if user.GID == GID:
            c_user = user
            if scheme_name == "DAC-MACS":
                alice = {'id': GID, 'authoritySecretKeys': {}, 'keys': None}
                alice['keys'], dacmacs_users[alice['id']] = abe_scheme.registerUser(gpp)
                for attr in user.user_attributes:
                    abe_scheme.keygen(gpp, authorities[authority1], attr, dacmacs_users[GID],
                                      alice['authoritySecretKeys'])
                try:
                    TK = abe_scheme.generateTK(gpp, CT['c1'], alice['authoritySecretKeys'], alice['keys'][0])
                    PT = abe_scheme.decrypt(CT, TK, alice['keys'][1])

                    messagebox.showinfo("Thông báo", f"Giải mã thành công PT: {PT.decode()}")
                    return
                except Exception as e:
                    print(e)
                    messagebox.showerror("Lỗi", e)
                    return

            elif scheme_name == "MA-ABE YJ14":
                bob = {'id': GID, 'authoritySecretKeys': {}, 'keys': None}
                bob['keys'], yj14_users[bob['id']] = abe_scheme.registerUser(GPP)
                for attr in user.user_attributes:
                    abe_scheme.keygen(GPP, authorities[authority1], attr, yj14_users[GID], bob['authoritySecretKeys'])
                try:
                    PT = abe_scheme.decrypt(GPP, CT, bob)
                    messagebox.showinfo("Thông báo", f"Giải mã thành công PT: {PT.decode()}")
                    return
                except Exception as e:
                    print(e)
                    messagebox.showerror("Lỗi", e)
                    return

            elif scheme_name == "DABE":
                try:
                    PT = abe_scheme.decrypt(gp, dabeK, CT)
                    messagebox.showinfo("Thông báo", f"Giải mã thành công PT: {PT.decode()}")
                    return
                except Exception as e:
                    print(e)
                    messagebox.showerror("Lỗi", e)
                    return
            else:
                messagebox.showerror("Lỗi", "Chưa hỗ trợ chức năng này")
                return
            messagebox.showinfo("Thông tin", f"GID: {GID}, thuộc tính người dùng: {user.user_attributes}")
            return

    messagebox.showerror("Lỗi", "Không tìm thấy người dùng với GID đã nhập")
    return

def main():
    global root, frame1, lb0, combo, button, lb1, label1, entry1, label2, entry2, label3, entry3, button1, frame2, lb2, label4, entry4, label5, entry5, button2, frame3, lb3, label6, entry6, label7, entry7, button3, frame4, label8, entry8, button4, label9, label10
    # Tạo cửa sổ chính
    root = tk.Tk()
    root.title("MA-ABE System")

    frame1 = tk.Frame(root, borderwidth=2, relief="groove")
    frame1.grid(row=0, column=0, sticky="nsew")
    # Tạo nhãn cho dropdown list
    lb0 = tk.Label(frame1, text="Scheme:")
    lb0.grid(row=0, column=0, padx=10, pady=10)

    # Tạo dropdown list (Combobox)
    combo = ttk.Combobox(frame1, values=["DAC-MACS", "MA-ABE YJ14", "DABE"], state="readonly")
    combo.grid(row=0, column=1, padx=10, pady=10)
    combo.current(0)  # Chọn mục đầu tiên làm mặc định

    # Tạo nút nhấn để lấy giá trị đã chọn
    button = tk.Button(frame1, text="CASetup", command=choose_scheme)
    button.grid(row=0, column=2, padx=10, pady=10)

    lb1 = tk.Label(frame1, text="AAs")
    lb1.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

    # Tạo nhãn và ô nhập văn bản thứ nhất
    label1 = tk.Label(frame1, text="AA1:")
    label1.grid(row=2, column=0, padx=10, pady=5)
    entry1 = tk.Entry(frame1, width=35)
    entry1.grid(row=2, column=1, padx=10, pady=5)

    # Tạo nhãn và ô nhập văn bản thứ hai
    label2 = tk.Label(frame1, text="AA2:")
    label2.grid(row=3, column=0, padx=10, pady=5)
    entry2 = tk.Entry(frame1, width=35)
    entry2.grid(row=3, column=1, padx=10, pady=5)

    # Tạo nhãn và ô nhập văn bản thứ ba
    label3 = tk.Label(frame1, text="AA3:")
    label3.grid(row=4, column=0, padx=10, pady=5)
    entry3 = tk.Entry(frame1, width=35)
    entry3.grid(row=4, column=1, padx=10, pady=5)

    # Tạo nút nhấn
    button1 = tk.Button(frame1, text="AASetup", command=AAs_setup)
    button1.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    frame2 = tk.Frame(root, borderwidth=2, relief="groove")
    frame2.grid(row=1, column=0, sticky="nsew")

    lb2 = tk.Label(frame2, text="Data Owner")
    lb2.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

    label4 = tk.Label(frame2, text="Data:")
    label4.grid(row=7, column=0, padx=10, pady=5)
    entry4 = tk.Entry(frame2)
    entry4.grid(row=7, column=1, padx=10, pady=5)

    label5 = tk.Label(frame2, text="Access policy:")
    label5.grid(row=8, column=0, padx=10, pady=5)
    entry5 = tk.Entry(frame2)
    entry5.grid(row=8, column=1, padx=10, pady=5)

    button2 = tk.Button(frame2, text="Encrypt", command=get_data_and_policy)
    button2.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

    frame3 = tk.Frame(root, borderwidth=2, relief="groove")
    frame3.grid(row=0, column=1, sticky="nsew")

    lb3 = tk.Label(frame3, text="User")
    lb3.grid(row=1, column=3, columnspan=2, padx=10, pady=5)

    label6 = tk.Label(frame3, text="GID:")
    label6.grid(row=2, column=3, padx=10, pady=5)
    entry6 = tk.Entry(frame3)
    entry6.grid(row=2, column=4, padx=10, pady=5)

    label7 = tk.Label(frame3, text="User attributes:")
    label7.grid(row=3, column=3, padx=10, pady=5)
    entry7 = tk.Entry(frame3)
    entry7.grid(row=3, column=4, padx=10, pady=5)

    button3 = tk.Button(frame3, text="Register", command=register_user)
    button3.grid(row=4, column=3, columnspan=2, padx=10, pady=10)

    label9 = tk.Label(frame3, text="")
    label9.grid(row=5, column=3, columnspan=2, padx=10, pady=5)

    label10 = tk.Label(frame3, text="")
    label10.grid(row=6, column=3, columnspan=2, padx=10, pady=5)

    # lb4 = tk.Label(frame, text="User")
    # lb4.grid(row=5, column=3, columnspan=2, padx=10, pady=5)

    frame4 = tk.Frame(root, borderwidth=2, relief="groove")
    frame4.grid(row=1, column=1, sticky="nsew")

    label8 = tk.Label(frame4, text="GID:")
    label8.grid(row=7, column=3, padx=10, pady=5)
    entry8 = tk.Entry(frame4)
    entry8.grid(row=7, column=4, padx=10, pady=5)

    button4 = tk.Button(frame4, text="Decrypt", command=get_GID)
    button4.grid(row=8, column=3, columnspan=2, padx=10, pady=10)

    # Bắt đầu vòng lặp sự kiện chính
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()