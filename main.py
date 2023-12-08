from server import app
import ssl
#from this file everything should be started

if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.load_cert_chain('neptun.pem', 'neptun-key.pem')
    app.run(host="0.0.0.0",port="5000",debug=True)
