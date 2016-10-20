import requests
import os


if __name__ == '__main__':
    r = requests.get('https://raw.githubusercontent.com/DefinitelyTyped/DefinitelyTyped/master/c3/c3.d.ts')

    if r.status_code == 200:
        with open(os.path.join('c3', 'c3.d.ts'), 'w') as f:
            f.write(r.text)

    r = requests.get('https://raw.githubusercontent.com/DefinitelyTyped/DefinitelyTyped/master/d3/d3.d.ts')

    if r.status_code == 200:
        with open(os.path.join('d3', 'd3.d.ts'), 'w') as f:
            f.write(r.text)
