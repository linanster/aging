def init_views(app):
    from .blue_index import blue_index
    from .blue_test import blue_test
    from .blue_manage import blue_manage
    from .blue_about import blue_about
    from .blue_control import blue_control
    from .blue_upload import blue_upload
    app.register_blueprint(blue_index)
    app.register_blueprint(blue_test)
    app.register_blueprint(blue_manage)
    app.register_blueprint(blue_about)
    app.register_blueprint(blue_control)
    app.register_blueprint(blue_upload)
