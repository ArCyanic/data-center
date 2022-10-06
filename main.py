from flask import Flask

from Update import appUpdate 
from ObservatoryProjects import appObservatoryProject 
from ObservatoryPackages import appObservatoryPackages 

app = Flask(__name__)
app.register_blueprint(appUpdate, url_prefix='/update')
app.register_blueprint(appObservatoryProject, url_prefix='/observatory-projects')
app.register_blueprint(appObservatoryPackages, url_prefix='/observatory-packages')

app.config['JSON_SORT_KEYS'] = False # Notice this line

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0', '8080')