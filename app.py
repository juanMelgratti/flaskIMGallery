from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/home")
#puedo usar la misma función para más de una ruta
def hello_world():
    return "hello worlddue"

@app.route("/variable/<string:name>/<int:id>")
def variable(name, id):
    return "hello " + name + str(id)




















if __name__ =="__main__":
    app.run(debug=True)

