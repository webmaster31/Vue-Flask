from app import login_manager

from app.models import Person
from app.tokens import confirm_access_token


@login_manager.request_loader
def load_user_from_request(request):
    person = Person()
    entity_id = None
    # try to login using Basic Auth
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            entity_id = confirm_access_token(api_key)
        except TypeError:
            pass
        if entity_id:
            user = person.get(entity_id, key='entity_id')
            if user:
                return user
        return None
    # finally, return None if both methods did not login the user
    return None
