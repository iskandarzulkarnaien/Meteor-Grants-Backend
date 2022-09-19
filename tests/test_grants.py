from grants import create_app


def test_create_household():
    app = create_app()
    with app.test_client() as test_app:
        data = {'Housing Type': 'Landed'}
        response = test_app.post('/household/new', data=data)
        assert response.status_code == 200

        # TODO: Check that household has been created in the DB
