from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient

User = get_user_model()


class UserAPITestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self._test_user_dict = dict(username='test_user', password='test123')
        User.objects.create_user(**self._test_user_dict)
        self.api_client = APIClient()

    def _login(self):
        self.api_client.login(**self._test_user_dict)

    def _create_other_user(self):
        self.other_user_id = User.objects.create_user(
            username='other_user',
            password='5432',
        ).id

    def test_register(self):
        """
         - user can register with username and password
         - user receives empty statistics
        """
        response = self.api_client.post(
            '/api/user/register/',
            data={'username': 'some_user', 'password': '123'},
        )
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(response.json(),
                             {'username': 'some_user', 'won': 0, 'lost': 0,
                              'won_by_surrender': 0, 'draws': 0,
                              'surrendered': 0})

    def test_register_username_taken(self):
        """
         - user cannot register with username that is already taken
        """
        response = self.api_client.post(
            '/api/user/register/',
            data={'username': 'test_user', 'password': '123'},
        )
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(),
                             {'error': 'This username is already taken'})

    def test_login(self):
        """
         - registered user can login using his username and password
        """
        response = self.api_client.post(
            '/api/user/login/',
            data=self._test_user_dict,
        )
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(),
                             {'username': 'test_user', 'won': 0, 'lost': 0,
                              'won_by_surrender': 0, 'draws': 0,
                              'surrendered': 0})

    def test_login_failed(self):
        """
         - registered user cannot login using wrong password
        """
        failed_dict = self._test_user_dict
        failed_dict['password'] = '4321'

        response = self.api_client.post(
            '/api/user/login/',
            data=failed_dict,
        )
        self.assertEqual(response.status_code, 400)

    def test_me(self):
        """
         - user can receive his statistics
        """
        self._login()

        response = self.api_client.get(
            '/api/user/me/',
        )

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(),
                             {'username': 'test_user', 'won': 0, 'lost': 0,
                              'won_by_surrender': 0, 'draws': 0,
                              'surrendered': 0})

    def test_logout(self):
        """
         - logged in user can log out
        """
        self._login()

        response = self.api_client.post(
            '/api/user/logout/',
        )
        print(response)
        self.assertEqual(response.status_code, 200)

        response = self.api_client.get(
            '/api/user/me/',
        )
        self.assertEqual(response.status_code, 403)

    def test_my_games(self):
        """
         - user can receive list of his games - empty, if none were started
        """
        self._login()

        response = self.api_client.get(
            '/api/user/me/games/',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_my_finished_games(self):
        """
         - user can receive list of his finished games - empty, if none were
           started
        """
        self._login()

        response = self.api_client.get(
            '/api/user/me/games/',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_info_about_some_user(self):
        """
         - user can obtain other user's statistics
        """
        self._login()
        self._create_other_user()

        response = self.api_client.get(
            '/api/user/{}'.format(self.other_user_id),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
                         {'username': 'other_user', 'won': 0, 'lost': 0,
                          'won_by_surrender': 0, 'draws': 0,
                          'surrendered': 0}
                         )

    def test_info_about_non_existing_user(self):
        """
         - user cannot obtain info about non-existing user - server returns
           status 404
        """
        self._login()

        response = self.api_client.get(
            '/api/user/{}'.format(1924503),
        )
        self.assertEqual(response.status_code, 404)
