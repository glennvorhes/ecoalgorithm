from setuptools import setup

setup(
    name='ecoalgorithm',
    version='',
    packages=['ecoalgorithm'],
    package_data={'ecoalgorithm': ['static/*.js', 'static/*.map', 'static/*.css', 'templates/*.html', '_test/*.*']},
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
