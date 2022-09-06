from flask import Flask

from Update import appUpdate 
from ObservatoryProject import appObservatoryProject 
from Misc import appMisc 

app = Flask(__name__)
app.register_blueprint(appUpdate, url_prefix='/update')
app.register_blueprint(appObservatoryProject, url_prefix='/observatory-project')
app.register_blueprint(appMisc, url_prefix='/misc')

app.config['JSON_SORT_KEYS'] = False # Notice this line

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0', '8080')