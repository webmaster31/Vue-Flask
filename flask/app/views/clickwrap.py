import json

from app.tasks import send_task
from app.models import ClickwrapAcceptance
from app.repositories import ClickwrapRepository
from flask import request, Blueprint, current_app as app
from flask_login import login_required, current_user

clickwrap_blueprint = Blueprint('clickwrap', __name__)


@clickwrap_blueprint.route('/clickwrap', methods=['GET'])
@login_required
def get_clickwrap():
    with ClickwrapRepository() as repo:
        clickwrap = repo.get_published()

        return app.response_class(
            response=json.dumps(
                dict(
                    success=True,
                    clickwrap=clickwrap.get_for_api() if clickwrap else clickwrap
                )
            ),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )


@clickwrap_blueprint.route('/clickwrap/draft', methods=['GET'])
@login_required
# TODO: Add protection to make this route accessible only to admin users.
# I.e. @admin_required
def get_draft():
    with ClickwrapRepository() as repo:
        clickwrap = repo.get_draft()

        return app.response_class(
            response=json.dumps(
                dict(
                    success=True,
                    clickwrap=clickwrap.get_for_api() if clickwrap else clickwrap
                )
            ),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )


@clickwrap_blueprint.route('/clickwrap/draft', methods=['POST'])
@login_required
# TODO: Add protection to make this route accessible only to admin users.
# I.e. @admin_required
def save_draft():
    if not request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please use \'application/json\'')),
            status=400,
            mimetype=app.config['MIME_TYPE']
        )

    if "content" not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Property \"content\" is required.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )

    if "content_version" not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Property \"content_version\" is required.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )

    content = request.json['content']
    content_version = request.json['content_version']

    with ClickwrapRepository() as repo:
        clickwrap = repo.save_draft(content, content_version)
        return app.response_class(
            response=json.dumps(
                dict(
                    success=True,
                    message='Clickwrap saved as draft successfully.',
                    clickwrap=clickwrap.get_for_api()
                )
            ),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )


@clickwrap_blueprint.route('/clickwrap/publish', methods=['POST'])
@login_required
# TODO: Add protection to make this route accessible only to admin users.
# I.e. @admin_required
def publish():
    if not request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please use \'application/json\'')),
            status=400,
            mimetype=app.config['MIME_TYPE']
        )

    if "content" not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Property \"content\" is required.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )

    if "content_version" not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Property \"content_version\" is required.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )

    content = request.json['content']
    content_version = request.json['content_version']

    with ClickwrapRepository() as repo:
        clickwrap = repo.get_content_version_published(content_version)
        if clickwrap:
            return app.response_class(
                response=json.dumps(
                    dict(
                        success=False,
                        message='This version has been published already, please use a different version number.'
                    )
                ),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )

        clickwrap = repo.publish(content, content_version)
        return app.response_class(
            response=json.dumps(
                dict(
                    success=True,
                    message='Clickwrap published successfully.',
                    clickwrap=clickwrap.get_for_api()
                )
            ),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )


@clickwrap_blueprint.route('/clickwrap/accept', methods=['PUT'])
@login_required
def accept():
    if not request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please use \'application/json\'')),
            status=400,
            mimetype=app.config['MIME_TYPE']
        )

    if "content_version" not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Property \"content_version\" is required.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )

    if "version" not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Property \"version\" is required.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    
    if "content_md5" not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Property \"content_md5\" is required.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )

    entity_version = request.json['version']
    content_version = request.json['content_version']
    content_md5 = request.json['content_md5']

    forwarded_for = request.headers.getlist("X-Forwarded-For")
    request_ip = forwarded_for[0] if forwarded_for else request.environ['REMOTE_ADDR']

    acceptance = ClickwrapAcceptance(
        ip_address=request_ip,
        user_id=current_user.entity_id,
        clickwrap_version=entity_version,
        clickwrap_content_version=content_version,
        clickwrap_content_md5=content_md5
    )

    with ClickwrapRepository() as repo:
        clickwrap = repo.get_content_version_published(content_version, version=entity_version, content_md5=content_md5)
        if not clickwrap:
            return app.response_class(
                response=json.dumps(
                    dict(
                        success=False,
                        message='This version has not been published. Please re-verify the clickwrap agreement.'
                    )
                ),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )

        if not repo.has_user_accepted(acceptance):
            acceptance = repo.accept_clickwrap(acceptance)
            user_dict = current_user.get_as_dict()
            user_dict.pop("password", None)
            user_dict.pop("raw_password", None)
            user_dict.pop("password_hash", None)
            user_dict.pop("access_token", None)
            user_dict.pop("expires_in", None)
            send_task('dump-clickwrap', 'dump_clickwrap_acceptance', {
                "acceptance": acceptance.get_as_dict(), 
                "user": user_dict, 
                "clickwrap": clickwrap.get_as_dict()
            })

        return app.response_class(
            response=json.dumps(
                dict(
                    success=True,
                    message='Clickwrap accepted successfully.',
                    clickwrap=acceptance.get_for_api()
                )
            ),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
