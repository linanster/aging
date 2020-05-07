from .tables import db
from .tables import RunningState, Systeminfo
from .tables import Device, Factory, Testdata, TestdataArchive

# from .views import view, TestdataView, TestdataArchiveView

def init_models(app):
    db.init_app(app)
    db.reflect(app=app)
