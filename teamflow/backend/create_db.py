import pymysql
import ssl
import os

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.load_verify_locations('./ca.pem')
ctx.check_hostname = False

conn = pymysql.connect(
    host=os.getenv('AIVEN_HOST'),
    port=int(os.getenv('AIVEN_PORT', 17334)),
    user=os.getenv('AIVEN_USER'),
    password=os.getenv('AIVEN_PASSWORD'),
    ssl=ctx
)
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS teamflow")
print("✅ Database 'teamflow' created!")
conn.close()