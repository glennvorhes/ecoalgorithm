from flask import Flask
from ecoalgorithm.db_connect import db
from ecoalgorithm import models
import sqlalchemy

app = Flask(__name__)


@app.route('/')
def summary():
    out_str = ''
    gens = db.sess.query(models.DbGeneration).order_by(sqlalchemy.desc(models.DbGeneration.gen_num))

    for g in gens:
        assert isinstance(g, models.DbGeneration)
        """
        :type: models.DbGeneration
        """

        out_str += 'Generation {0}<br>'.format(g.gen_num)

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


if __name__ == '__main__':
    app.run(port=5001)
