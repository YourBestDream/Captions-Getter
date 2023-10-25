from server import app

#from this file everything should be started

if __name__ == '__main__':
    app.run(host="0.0.0.0",port="5000",debug=True)