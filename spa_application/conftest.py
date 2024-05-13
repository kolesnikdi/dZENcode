import datetime

import pyotp
import pytest
import random
import string

from django.urls import reverse
from django.core.cache import cache
from knox.models import AuthToken
from rest_framework.test import APIClient

from company.models import Company
from address.models import Address
from image.models import Image
from location.models import Location
from product.models import Product, Category
from registration.models import RegistrationTry
from Web_Menu_DA.constants import Types2FA
from two_factor_authentication.models import GoogleAuth


"""randomizers"""


@pytest.fixture(scope='function')
def randomizer():
    return Randomizer()


class Randomizer:

    def email(self):
        """ randomize data for email"""
        return ''.join(random.choice(string.hexdigits) for i in range(10)) + "@gmail.com"

    def upp2_data(self):
        """ randomize data for username, password, password2"""
        return ''.join(random.choice(string.hexdigits) for i in range(10))

    def random_name(self):
        """ randomize data for first_name, last_name"""
        return ''.join(random.choice(string.ascii_letters) for i in range(10)).title()

    def random_name_limit(self, limit):
        """ randomize data for first_name, last_name"""
        return ''.join(random.choice(string.ascii_letters) for i in range(limit)).title()

    def random_phone(self):
        """ randomize data for mobile phone"""
        return '+38063' + ''.join(random.choice(string.digits) for i in range(7))

    def user(self):
        """ randomize data user"""
        user = {
            'username': None,
            'first_name': ''.join(random.choice(string.ascii_letters) for i in range(10)).title(),
            'last_name': ''.join(random.choice(string.ascii_letters) for i in range(10)).title(),
            'password': ''.join(random.choice(string.hexdigits) for i in range(10)),
            'mobile_phone': '+38063' + ''.join(random.choice(string.digits) for i in range(7)),
            'fathers_name': ''.join(random.choice(string.ascii_letters) for i in range(10)).title(),
            'country': ''.join(random.choice(string.ascii_letters) for i in range(10)).title(),
            'city': ''.join(random.choice(string.ascii_letters) for i in range(10)).title(),
            'street': ''.join(random.choice(string.ascii_letters) for i in range(10)).title(),
            'house_number': ''.join(random.choice(string.digits) for i in range(2)),
            'flat_number': ''.join(random.choice(string.digits) for i in range(2)),
            'passport_series': ''.join(random.choice(string.ascii_letters) for i in range(2)).title(),
            'passport_number': ''.join(random.choice(string.digits) for i in range(6)),
            'passport_date_of_issue': datetime.date.today(),
            'passport_issuing_authority': ''.join(random.choice(string.ascii_letters) for i in range(10)).title(),
            'is_staff': False,
            'is_active': True,
            'date_joined': datetime.datetime.now(),
        }
        return user

    def random_digits(self):
        """ randomize digits"""
        return ''.join(random.choice(string.digits) for i in range(10))

    def random_digits_limit(self, limit):
        """ randomize digits"""
        digit = '123456789'
        return ''.join(random.choice(digit) for i in range(limit))

    def company_data(self):
        data = {
            'legal_name': self.random_name(),
            'logo': {'image': None},  # todo upload image
            'legal_address': {'country': self.random_name(),
                              'city': self.random_name(),
                              'street': self.random_name(),
                              'house_number': self.random_digits(),
                              'flat_number': self.random_digits()},
            'actual_address': {'country': self.random_name(),
                               'city': self.random_name(),
                               'street': self.random_name(),
                               'house_number': self.random_digits(),
                               'flat_number': self.random_digits()},
            'code_USREOU': self.random_digits(),
            'phone': self.random_phone(),
            'email': self.email(),
        }
        return data

    def location_data(self):
        data = {
            'legal_name': self.random_name(),
            'logo': {'image': None},  # todo upload image
            'address': {'country': self.random_name(),
                        'city': self.random_name(),
                        'street': self.random_name(),
                        'house_number': self.random_digits(),
                        'flat_number': self.random_digits()},
            'phone': self.random_phone(),
            'email': self.email(),
        }
        return data

    def product_data(self):
        data = {
            'name': self.random_name(),
            'logo': {'image': None},  # todo upload image
            'description': self.upp2_data(),
            'volume': self.random_digits_limit(4),
            'measure': random.choice([0, 1, 2]),
            'cost': self.random_digits_limit(4),
        }
        return data


"""created custom users"""


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(scope='function')
def user(django_user_model, randomizer):
    password = randomizer.upp2_data()
    user = django_user_model.objects.create_user(
        id=randomizer.random_digits_limit(3),
        email=randomizer.email(),
        password=password
    )
    user.user_password = password
    return user


@pytest.fixture(scope='function')
def user_2(django_user_model, randomizer):
    password = randomizer.upp2_data()
    user = django_user_model.objects.create_user(
        id=randomizer.random_digits_limit(3),
        email=randomizer.email(),
        password=password,
        mobile_phone=randomizer.random_phone(),
    )
    user.user_password = password
    return user


@pytest.fixture(scope='function')
def authenticated_client(api_client, user):
    api_client.user_token = AuthToken.objects.create(user)[1]
    api_client.user = user
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {api_client.user_token}')
    return api_client


@pytest.fixture(scope='function')
def authenticated_client_2(user_2):
    api_client = APIClient()
    token = AuthToken.objects.create(user_2)[1]
    api_client.user_token = AuthToken.objects.create(user_2)[1]
    api_client.user = user_2
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {api_client.user_token}')
    return api_client


@pytest.fixture(scope='function')
def authenticated_client_email_2fa(api_client, user, randomizer):
    user.type_2fa = Types2FA.EMAIL
    user.save()
    code = randomizer.random_digits_limit(6)
    cache.set(user.id, {'code': code}, 60)
    api_client.user_token = AuthToken.objects.create(user)[1]
    api_client.user = user
    api_client.credentials(
            HTTP_AUTHORIZATION=f'Token {api_client.user_token}',
            HTTP_2FACODE=code,
    )
    return api_client


@pytest.fixture(scope='function')
def authenticated_client_gauth_2fa(api_client, user):
    user.type_2fa = Types2FA.GAUTH
    user.save()
    otp_base32 = pyotp.random_base32()
    otp_auth_url = pyotp.totp.TOTP(otp_base32).provisioning_uri(
        name=user.email.lower(),
        issuer_name="Web_Menu_DA",
    )
    gauth = GoogleAuth.objects.create(owner_id=user.id, otp_base32=otp_base32, otp_auth_url=otp_auth_url)
    api_client.user = user
    api_client.gauth = gauth
    api_client.credentials(
            HTTP_AUTHORIZATION=f'Token {AuthToken.objects.create(user)[1]}',
            HTTP_2FACODE=pyotp.TOTP(otp_base32).now(),
    )
    return api_client


"""fixture for registration app"""


@pytest.fixture
def reg_try(randomizer, api_client):
    url = reverse('user_reg')
    data = {
        'email': randomizer.email(),
    }
    response = api_client.post(url, data=data, format='json')
    return response


@pytest.fixture
def reg_done_code(api_client, reg_try, randomizer):
    validated_data = randomizer.user()
    data_reg_try = RegistrationTry.objects.get(email=reg_try.data['email'])
    url = reverse('registration_confirm', args=[data_reg_try.code])
    validated_data.update({'password2': validated_data['password']})
    api_client.post(url, data=validated_data, format='json')
    for_check_reg_try = RegistrationTry.objects.get(id=data_reg_try.id)
    return for_check_reg_try.code


"""created custom company / location / product"""


@pytest.fixture(scope='function')
def custom_company(authenticated_client_2, randomizer):
    company_data = randomizer.company_data()
    company = Company.objects.create(
        owner=authenticated_client_2.user,
        logo=Image.objects.create(**company_data['logo']),
        legal_name=company_data['legal_name'],
        legal_address=Address.objects.create(**company_data['legal_address']),
        actual_address=Address.objects.create(**company_data['actual_address']),
        code_USREOU=company_data['code_USREOU'],
        phone=company_data['phone'],
        email=company_data['email'],
    )
    company.user_password = authenticated_client_2.user.user_password
    company.user = authenticated_client_2
    return company


@pytest.fixture(scope='function')
def custom_company_2(user, randomizer):
    company_data = randomizer.company_data()
    company = Company.objects.create(
        owner=user,
        logo=Image.objects.create(**company_data['logo']),
        legal_name=company_data['legal_name'],
        legal_address=Address.objects.create(**company_data['legal_address']),
        actual_address=Address.objects.create(**company_data['actual_address']),
        code_USREOU=company_data['code_USREOU'],
        phone=company_data['phone'],
        email=company_data['email'],
    )
    company.user_password = user.user_password
    company.user = user
    return company


@pytest.fixture(scope='function')
def custom_location(randomizer, custom_company):
    data = randomizer.location_data()
    location = Location.objects.create(
        company_id=custom_company.id,
        logo=Image.objects.create(**data['logo']),
        legal_name=data['legal_name'],
        address=Address.objects.create(**data['address']),
        phone=data['phone'],
        email=data['email'],
    )
    location.user_password = custom_company.user_password
    location.user = custom_company.user
    return location


@pytest.fixture(scope='function')
def custom_product(randomizer, custom_location):
    data = randomizer.product_data()
    product = Product.objects.create(
        company_id=custom_location.company.id,
        name=data['name'],
        logo=Image.objects.create(**data['logo']),
        description=data['description'],
        volume=data['volume'],
        measure=data['measure'],
        cost=data['cost'],
    )
    product.locations.set([custom_location.id])
    product.location_id = custom_location.id
    return product


@pytest.fixture(scope='function')
def custom_products_for_filtering(randomizer, custom_location):
    products = []
    for _ in range(10):
        data = randomizer.product_data()
        product = Product(
            company_id=custom_location.company.id,
            name=data['name'],
            logo=Image.objects.create(**data['logo']),
            description=data['description'],
            volume=data['volume'],
            measure=data['measure'],
            cost=data['cost'],
        )
        products.append(product)
    product_qs = Product.objects.bulk_create(products)
    # with a reverse query, we make a record in the database in one pass
    custom_location.product_location.set(product_qs)

    return product_qs


@pytest.fixture(scope='function')
def custom_category(randomizer, custom_location):
    category = Category.add_root(name=randomizer.random_name())
    category.location.set([custom_location])
    child = category.add_child(name='child_category')
    child.location.set([custom_location])
    category.c_location = custom_location
    category.child = child
    return category


@pytest.fixture(scope='function')
def custom_category_2(randomizer, custom_location):
    category = Category.add_root(name=randomizer.random_name())
    category.location.set([custom_location])
    child = category.add_child(name='child')
    child.location.set([custom_location])
    category.c_location = custom_location
    category.child = child
    return category
