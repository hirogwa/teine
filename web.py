from flask import Flask, render_template
import os

app = Flask(__name__)


@app.route('/ping', methods=['GET'])
def ping():
    return 'sup'


@app.route('/explorer', methods=['GET'])
def explorer():
    return render_template('explorer.html')


if __name__ == '__main__':
    app.debug = True
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000))
    )
