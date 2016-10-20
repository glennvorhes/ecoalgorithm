from flask import Flask, redirect, url_for, render_template, Response
# from ecoalgorithm import db
from ecoalgorithm import _models as models
from ._config import config
import sqlalchemy
from . import _web_methods as web
from ._helpers import printd
import json

app = Flask(__name__)


@app.route('/')
@app.route('/summary')
def summary():

    # all_summ = web.all_summary()
    out_str = 'fish'
    return render_template('summary.html')


@app.route('/summ')
def summary_info():

    summ = web.all_summary()

    if summ is None:
        return Response('{}', mimetype='application/json')
    else:
        return Response(summ.c3_json_str, mimetype='application/json')


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/generation/<int:gen_num>')
def generation(gen_num):
    return render_template('generation.html', summ=web.generation_summary(gen_num))


@app.route('/individual/<guid>')
def individual(guid):
    return render_template('individual.html', summ=web.individual_summary(guid))


def start_web_server(port: int = None, debug: bool = None):
    port = config.web_port if type(port) is not int else port
    debug = config.web_debug if type(debug) is not bool else debug
    app.run(port=port, debug=debug)


__all__ = [app, start_web_server]

if __name__ == '__main__':
    app.run(port=5001, debug=True)
