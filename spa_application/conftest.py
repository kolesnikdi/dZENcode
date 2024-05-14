import pytest
import random
import string
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from comments.models import Comment
from spa_application.settings import RUN_FROM_LOCAL


@pytest.fixture
def api_client():
    return APIClient()


"""randomizers"""
@pytest.fixture(scope='function')
def randomizer():
    return Randomizer()


class Randomizer:

    def email(self):
        """ randomize data for email"""
        return ''.join(random.choice(string.hexdigits) for i in range(10)) + "@gmail.com"

    def username(self):
        """ randomize data for username"""
        return ''.join(random.choice(string.hexdigits) for i in range(10))

    def random_text(self, limit):
        """ randomize text"""
        return ''.join(random.choice(string.ascii_letters) for i in range(limit)).title()


def create_root(i, randomizer):
    root = Comment.add_root(
        username=randomizer.username(),
        email=randomizer.email(),
        text=randomizer.random_text(i*10)
    )
    return root


def create_child(root, i, randomizer):
    child = root.add_child(
        username=randomizer.username(),
        email=randomizer.email(),
        text=randomizer.random_text(i*10)
    )
    return child


@pytest.fixture(scope='function')
def comments(randomizer):
    for i in range(1, 30):
        root = create_root(i, randomizer)
        for _ in range(1, 4):
            new_child = create_child(root, _, randomizer)
            create_child(new_child, 5, randomizer)
    return Comment.objects.all()

@pytest.fixture(scope='function')
def valid_img():
    file_path = str(settings.BASE_DIR) + r'\comments\tests\3.png'
    if not RUN_FROM_LOCAL:
        file_path = '/spa_application/comments/tests/3.png'
    img = SimpleUploadedFile(
        name='logo.jpg',
        content=open(file_path, 'rb').read(),
        content_type='image/jpeg',
    )
    return img

@pytest.fixture(scope='function')
def big_img():
    file_path = str(settings.BASE_DIR) + r'\comments\tests\logo.jpg'
    if not RUN_FROM_LOCAL:
        file_path = '/spa_application/comments/tests/logo.jpg'
    img = SimpleUploadedFile(
        name='logo.jpg',
        content=open(file_path, 'rb').read(),
        content_type='image/jpeg',
    )
    return img

@pytest.fixture(scope='function')
def invalid_format_img():
    file_path = str(settings.BASE_DIR) + r'\comments\tests\wirelizard-Lion-Ornament.svg'
    if not RUN_FROM_LOCAL:
        file_path = '/spa_application/comments/tests/wirelizard-Lion-Ornament.svg'
    img = SimpleUploadedFile(
        name='logo.jpg',
        content=open(file_path, 'rb').read(),
        content_type='image/jpeg',
    )
    return img
