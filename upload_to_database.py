import streamlit_authenticator as stauth

import database as db

usernames = ["pparker", "rmiller","ghislao"]
names = ["Peter Parker", "Rebecca Miller","Ghislain LAOKPEZI"]
passwords = ["abc123", "def456","1998"]
mails=["pparker@gmail.com", "rmille@gmail.comr","ghislao@gmail.com"]
hashed_passwords = stauth.Hasher(passwords).generate()


for (username, name, hash_password,mail,password) in zip(usernames, names, hashed_passwords,mails,passwords):
    db.insert_user(username, name, hash_password,mail,password)