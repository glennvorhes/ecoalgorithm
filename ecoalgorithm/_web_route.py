from flask import Flask, redirect, url_for, render_template
# from ecoalgorithm import db
from ecoalgorithm import _models as models
from ._config import config
import sqlalchemy
from . import _web_methods as web
from ._helpers import printd

app = Flask(__name__)


@app.route('/')
@app.route('/summary')
def summary():
    out_str = 'fish'
    return out_str
    # generations = db.sess.query(models.Generation).order_by(sqlalchemy.desc(models.Generation.gen_num))
    # """
    # :type: list[models.Generation]
    # """
    #
    # out_tuples = []
    #
    # for g in generations:
    #     print(g.individuals)
    #     # best = g.individuals[0]
    #     out_tuples.append((g.gen_num, None, None))
    #
    # # for g in gens:
    # #     assert isinstance(g, models.DbGeneration)
    # #     """
    # #     :type: models.DbGeneration
    # #     """
    # #
    # #     out_str += 'Generation {0}<br>'.format(g.gen_num)
    #
    # gen_summary = db.sess.query(
    #     models.SpeciesBase.gen_num,
    #     sqlalchemy.func.max(models.SpeciesBase.success),
    #     models.SpeciesBase.class_name,
    #     sqlalchemy.func.count(models.SpeciesBase.class_name)
    # ).group_by(
    #     models.SpeciesBase.gen_num,
    #     models.SpeciesBase.class_name
    # ).order_by(
    #     sqlalchemy.desc(models.SpeciesBase.gen_num),
    #     sqlalchemy.asc(models.SpeciesBase.class_name)
    # )

    return render_template('summary.html')


#
# @app.route('/generation')
# def generation():
#     f = db.sess.query(models.Generation).order_by(sqlalchemy.desc(models.Generation.gen_num)).first()
#     """
#     :type: models.DbGeneration
#     """
#
#     out_str = ''
#     for n in f.individuals:
#         out_str += 'Success: {suc}, Class: {cl}, Args {kw} <br>'.format(suc=n.success, kw=n.kwargs, cl=n.class_name)
#
#     print(f)
#
#     return out_str


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
