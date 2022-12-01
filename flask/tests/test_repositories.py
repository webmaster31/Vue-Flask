from app.repositories import PersonRepository


def test_person_repository_get_by_id(app, client, user_test_1, non_active_user):
    with app.app_context():
        with PersonRepository() as repo:
            # get by id returns the same person
            person = repo.get_by_id(user_test_1.entity_id)
            assert person == user_test_1

            # get by id do not returns not active user
            person = repo.get_by_id(non_active_user.entity_id)
            assert person is None


def test_person_repository_get_by_email(app, client, user_test_2, non_active_user):
    with app.app_context():
        with PersonRepository() as repo:
            # get by email returns the same person
            person = repo.get_by_email(user_test_2.email)
            assert person.entity_id == user_test_2.entity_id

            # get by id do not returns not active user
            person = repo.get_by_email(non_active_user.email)
            assert person is None


def test_person_repository_is_exist(app, client, user_test_1, non_active_user, non_existing_user):
    with app.app_context():
        with PersonRepository() as repo:
            # is_exists returns True for existing person
            assert repo.is_exist(user_test_1)

            # is_exists returns False for non existing person
            assert repo.is_exist(non_existing_user) is False

            # is_exists returns False for non active person
            assert repo.is_exist(non_active_user) is False
