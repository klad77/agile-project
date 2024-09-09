from django.test import TestCase
from rest_framework.response import Response
from apps.projects.models import Project
from apps.users.models import User
from apps.users.serializers.user_serializers import RegisterUserSerializer


class UserListViewTestCase(TestCase):
    def test_get_empty_list_of_users(self):
        response = self.client.get('/api/v1/users/')

        self.assertEqual(response.status_code, 204)
        self.assertIsInstance(response.data, list)
        self.assertEqual(User.objects.count(), 0)

    def test_get_users(self):
        users = [
            User(username='Administrator', first_name='Anton', last_name='Kimmels', position='Programmer',
                 email='anton@mail.com', phone='+78779521456', password='password'),
            User(username='Andrey', first_name='Andrey', last_name='Popov', position='CEO',
                 email='andrey@mail.com', phone='878779521456', password='passwordpassword'),
        ]

        User.objects.bulk_create(users)

        response = self.client.get('/api/v1/users/')

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, Response)
        self.assertEqual(User.objects.count(), 2)

        self.assertIsInstance(response.data, list)
        for user in response.data:
            self.assertIsInstance(user, dict)
            self.assertIn('first_name', user)
            self.assertIsInstance(user['first_name'], str)
            self.assertRegex(user['first_name'], r'^[a-zA-Z]*$')
            self.assertIn('last_name', user)
            self.assertIsInstance(user['last_name'], str)
            self.assertRegex(user['last_name'], r'^[a-zA-Z]*$')
            self.assertIn('position', user)
            self.assertIsInstance(user['position'], str)
            self.assertIn('phone', user)
            self.assertIsInstance(user['phone'], str)


class RegisterUserViewTestCase(TestCase):
    def setUp(self):
        self.url = '/api/v1/users/register/'
        self.data = {
            "username": "glensteff",
            "first_name": "Glen",
            "last_name": "Steffani",
            "position": "CTO",
            "email": "glen@mail.com",
            "password": "passwordpassword",
            "re_password": "passwordpassword"
        }

    def test_create_valid_user(self):

        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 201)
        self.assertIsInstance(response.data, dict)
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get(username="glensteff")
        self.assertEqual(user.first_name, "Glen")
        self.assertEqual(user.last_name, "Steffani")
        self.assertEqual(user.position, "CTO")
        self.assertEqual(user.email, "glen@mail.com")
        self.assertTrue(user.check_password("passwordpassword"))

    def test_create_user_invalid_email(self):
        self.data['email'] = 'glen'
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)

    def test_create_user_invalid_position(self):
        self.data['position'] = 'Worker'
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 400)


class RegisterUserSerializerTestCase(TestCase):

    def setUp(self):

        self.data = {
            "username": "glensteff",
            "first_name": "Glen",
            "last_name": "Steffani",
            "position": "CTO",
            "email": "glen@mail.com",
            "password": "passwordpassword",
            "re_password": "passwordpassword"
        }

    def test_valid_user_data(self):
        serializer = RegisterUserSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIsInstance(serializer.validated_data['username'], str)
        self.assertIsInstance(serializer.validated_data['first_name'], str)
        self.assertIsInstance(serializer.validated_data['last_name'], str)
        self.assertIsInstance(serializer.validated_data['email'], str)
        self.assertIsInstance(serializer.validated_data['position'], str)
        self.assertIsInstance(serializer.validated_data['password'], str)
        self.assertIsInstance(serializer.validated_data['re_password'], str)

    def test_valid_username(self):
        self.data["username"] = "*glensteff"
        serializer = RegisterUserSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('The username must be alphanumeric characters or have only _ symbol',
                      [str(i) for i in serializer.errors['non_field_errors']])

    def test_valid_first_name(self):
        self.data["first_name"] = "Glen1234"
        serializer = RegisterUserSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('The first name must contain only alphabet symbols',
                      [str(i) for i in serializer.errors['non_field_errors']])

    def test_valid_last_name(self):
        self.data["last_name"] = "Steffani1234"
        serializer = RegisterUserSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('The last name must contain only alphabet symbols',
                      [str(i) for i in serializer.errors['non_field_errors']])

    def test_invalid_password(self):
        self.data["re_password"] = "password"
        serializer = RegisterUserSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
        self.assertEqual(serializer.errors['password'][0], "Passwords don't match")


class UserDetailViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='glensteff',
            first_name='Glen',
            last_name='Steffani',
            email='glen@mail.com',
            phone='87778992277',
            position='CTO',
            project=Project.objects.create(name='Glen CTO project')
        )

    def test_user_detail_success(self):
        response = self.client.get(f'/api/v1/users/1/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data['username'], str)
        self.assertIsInstance(response.data['first_name'], str)
        self.assertIsInstance(response.data['last_name'], str)
        self.assertIsInstance(response.data['email'], str)
        self.assertIsInstance(response.data['phone'], str)
        self.assertIsInstance(response.data['position'], str)
        self.assertIsInstance(response.data['project'], str)

        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['first_name'], self.user.first_name)
        self.assertEqual(response.data['last_name'], self.user.last_name)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['phone'], self.user.phone)
        self.assertEqual(response.data['position'], self.user.position)
        self.assertEqual(response.data['project'], self.user.project.name)

    def test_user_detail_not_found(self):
        response = self.client.get('/api/v1/users/99/')
        self.assertEqual(response.status_code, 404)
        self.assertIn('detail', response.data)
