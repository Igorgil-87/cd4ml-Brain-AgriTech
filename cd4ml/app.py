"""
Web app
"""

import requests
from flask import Flask, request, render_template


app = Flask(__name__,
            template_folder='webapp/templates',
            static_folder='webapp/static')




@app.route('/', methods=['get'])
@app.route('/index.html', methods=['get'])
def welcome():
    return render_template("index.html")




if __name__ == '__main__':
    app.run(debug=True)
