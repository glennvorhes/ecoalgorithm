from flask import Flask, redirect, url_for, render_template
from ecoalgorithm.db_connect import db
from ecoalgorithm import _models as models
from ._config import config
import sqlalchemy

app = Flask(__name__)


@app.route('/')
@app.route('/summary')
def summary():
    out_str = ''
    generations = db.sess.query(models.DbGeneration).order_by(sqlalchemy.desc(models.DbGeneration.gen_num))
    """
    :type: list[models.DbGeneration]
    """

    out_tuples = []

    for g in generations:
        print(g.individuals)
        # best = g.individuals[0]
        out_tuples.append((g.gen_num, None, None))

    # for g in gens:
    #     assert isinstance(g, models.DbGeneration)
    #     """
    #     :type: models.DbGeneration
    #     """
    #
    #     out_str += 'Generation {0}<br>'.format(g.gen_num)

    gen_summary = db.sess.query(
        models.SpeciesBase.gen_num,
        sqlalchemy.func.max(models.SpeciesBase.success),
        models.SpeciesBase.class_name,
        sqlalchemy.func.count(models.SpeciesBase.class_name)
    ).group_by(
        models.SpeciesBase.gen_num,
        models.SpeciesBase.class_name
    ).order_by(
        sqlalchemy.desc(models.SpeciesBase.gen_num),
        sqlalchemy.asc(models.SpeciesBase.class_name)
    )

    return render_template('summary.html', generations=generations)
    for g in gen_summary:
        print(g)


    return out_str


@app.route('/generation')
def generation():
    f = db.sess.query(models.DbGeneration).order_by(sqlalchemy.desc(models.DbGeneration.gen_num)).first()
    """
    :type: models.DbGeneration
    """

    out_str = ''
    for n in f.individuals:
        out_str += 'Success: {suc}, Class: {cl}, Args {kw} <br>'.format(suc=n.success, kw=n.kwargs, cl=n.class_name)

    print(f)

    return out_str

@app.route('/test')
def test():
    return render_template('test.html')



@app.route('/generation/<int:gen_num>')
def profile(gen_num):
    min_max = db.sess.query(
        sqlalchemy.func.min(models.DbGeneration.gen_num),
        sqlalchemy.func.max(models.DbGeneration.gen_num),
    ).filter(models.DbGeneration.gen_num > 5000).first()

    if min_max[0] is None or min_max[1] is None:
        return redirect(url_for('summary'))

    print(min_max)
    # print(user_id)
    # print(type(user_id))
    return str(3)

def start_web_server(port: int = None, debug: bool = None):
    port = config.web_port if type(port) is not int else port
    debug = config.web_debug if type(debug) is not bool else debug
    app.run(port=port, debug=debug)


if __name__ == '__main__':
    app.run(port=5001, debug=True)
