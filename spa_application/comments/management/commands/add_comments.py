import random
import string
from django.core.management.base import BaseCommand

from comments.models import Comment


def create_root(i):
    root = Comment.add_root(
        username=''.join(random.choice(string.hexdigits) for i in range(10)),
        email=''.join(random.choice(string.hexdigits) for i in range(10)) + "@gmail.com",
        text=''.join(random.choice(string.ascii_letters) for i in range(i * 10)).title()
    )
    return root


def create_child(root, i):
    child = root.add_child(
        username=''.join(random.choice(string.hexdigits) for i in range(10)) + "@gmail.com",
        email=''.join(random.choice(string.hexdigits) for i in range(10)),
        text=''.join(random.choice(string.ascii_letters) for i in range(i * 10)).title()
    )
    return child


class Command(BaseCommand):
    help = 'Adds comments to the database'

    def handle(self, *args, **kwargs):
        for i in range(1, 30):
            root = create_root(i)
            for _ in range(1, 4):
                new_child = create_child(root, _)
                create_child(new_child, 5)
