
# if len(sys.argv) >= 2 and ('--help' in sys.argv[1:] or
#                                    sys.argv[1] in ('--help-commands', 'egg_info', '--version',
#                                                    'clean')):
#     # Use setuptools for these commands (they don't work well or at all
#     # with distutils).  For normal builds use distutils.
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='ecoalgorithm',
    version='1.0',
    packages=['ecoalgorithm'],
    package_data={
        'ecoalgorithm': [
            'static/*.js',
            'static/*.map',
            'static/*.css',
            'templates/*.html',
            '_test/*.*',
            '_test/test_dbs/results.test_db'
        ]
    },
    url='https://github.com/glennvorhes/ecoalgorithm',
    license='MIT',
    author='Glenn Vorhes',
    author_email='glennvorhes@gmail.com',
    description='Optimization algorithm to mimic competition between species',
    install_requires=[
        'sqlalchemy',
        'flask',
        'typing'
    ]
)
