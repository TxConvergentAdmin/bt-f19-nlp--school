import os
from flask import Flask
from flask import jsonify
import sys
sys.path.append(os.path.join(os.path.dirname(__file__),'..'))
import nltk_ner as ner

BUILD_DIR = os.path.join(os.path.dirname(__file__), 'build')

app = Flask(__name__, static_url_path='', static_folder=BUILD_DIR)


@app.route('/')
def index():
    return app.send_static_file('index.html')

#### NLP Endpoints Here
@app.route('/lecture/stuff')
def lecture_stuff():
    items = ner.info(ner.filename)
    return jsonify(ner.infoJSON(items))

####


if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
