from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('erpl/engineP5/', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('erpl/engineP5/', path)

if __name__ == '__main__':
    print("Servidor rodando em http://localhost:3000")
    app.run(host='localhost', port=3000)