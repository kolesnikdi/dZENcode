from django.db import models
from django.core.validators import MinLengthValidator
from treebeard.mp_tree import MP_Node


class Comment(MP_Node):
    username = models.CharField(db_index=True, max_length=20, validators=[MinLengthValidator(3)])
    email = models.EmailField(db_index=True, max_length=254)
    text = models.CharField(max_length=102400)     # max 100kb
    home_page = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to='media/', blank=True, null=True)
    created_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text
