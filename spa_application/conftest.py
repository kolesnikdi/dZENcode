import pytest
import random
import string
from rest_framework.test import APIClient

from comments.models import Comment


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


@pytest.fixture(scope='function')
def comments(randomizer):
    for i in range(1, 27):
        Comment.add_root(
            username=randomizer.username(),
            email=randomizer.email(),
            text=randomizer.random_text(i*10)
        )
    return comments
