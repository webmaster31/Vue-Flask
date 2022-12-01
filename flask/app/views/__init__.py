from app.views import authentication, clickwrap


def init_app(app):
    app.register_blueprint(authentication.auth)
    app.register_blueprint(clickwrap.clickwrap_blueprint)

