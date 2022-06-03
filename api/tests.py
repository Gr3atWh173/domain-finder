from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from faker import Faker
from django.contrib.auth import get_user_model


class RegistrationStatusTestCase(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = APIClient()
        self.endpoint_url = "/api/v1/registrationStatus?domain="

    def test_if_registered_domain_is_registered(self):
        response = self.client.get(self.endpoint_url + "google.com")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["registered"])

    def test_if_unregistered_domain_is_unregistered(self):
        # this domain name generated in a cryptographically secure way by my cat
        response = self.client.get(self.endpoint_url + "hqweyvzdiohqwuetybasas.com")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["registered"])

    def test_if_illformed_domain_is_reported(self):
        response = self.client.get(self.endpoint_url + "this_is not okay.com")

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)


class SimilarDomainsTestCase(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = APIClient()
        self.endpoint_url = "/api/v1/similarDomains?domain="

    def test_similar_generated_domains(self):
        response = self.client.get(self.endpoint_url + "google.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserAuthTestCase(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = APIClient()
        self.register_endpoint_url = "/api/v1/auth/users/"
        self.login_endpoint_url = "/api/v1/auth/jwt/create/"
        self.reg_status_endpoint_url = "/api/v1/registrationStatus?domain="
        self.me_endpoint_url = "/api/v1/auth/users/me"
        self.faker = Faker()

    def test_if_user_can_register(self):
        email = self.faker.email()
        username = email.split("@")[0]

        register_dict = {
            "email": email,
            "username": username,
            "password": "123456password",
        }

        response = self.client.post(self.register_endpoint_url, register_dict)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], email)
        self.assertEqual(response.data["username"], username)
        self.assertEqual(response.data["history"], [])

    def test_if_user_can_login(self):
        User = get_user_model()
        email = self.faker.email()
        username = email.split("@")[0]

        new_user = User.objects.create(email=email, username=username)
        new_user.set_password("123456password")
        new_user.save()

        response = self.client.post(
            self.login_endpoint_url,
            {"username": username, "password": "123456password"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in response.data)
        self.assertTrue("refresh" in response.data)

    def test_if_history_is_recording(self):
        User = get_user_model()
        email = self.faker.email()
        username = email.split("@")[0]

        new_user = User.objects.create(email=email, username=username)
        new_user.set_password("123456password")
        new_user.save()

        login_response = self.client.post(
            self.login_endpoint_url,
            {"username": username, "password": "123456password"},
        )
        access_token = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + access_token)

        reg_status_response = self.client.get(
            self.reg_status_endpoint_url + "google.com",
        )

        self.assertEqual(reg_status_response.status_code, status.HTTP_200_OK)

        me_response = self.client.get(
            self.me_endpoint_url,
            headers={"authorization": f"JWT {access_token}"},
            follow=True,
        )

        self.assertTrue("google.com" in me_response.data["history"])
