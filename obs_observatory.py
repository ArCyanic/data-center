from flask import Flask


app = Flask(__name__)


@app.route('/')
def test():
    return 'this is test line.'

if __name__ == '__main__':
    app.run('0.0.0.0', '8080')