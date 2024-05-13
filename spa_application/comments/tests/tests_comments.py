from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.urls import reverse
from rest_framework import status
import pytest


from comments.business_logic import validate_image


class TestBusinessLogic:
    def test_allowed_size_invalid(self):
        """ Another way to set 'absolute path'. Need for correct work 'pytest' command from Terminal."""
        file_path = str(settings.BASE_DIR) + r'\comments\tests\logo.jpg'
        test_logo = SimpleUploadedFile(
            name='logo.jpg',
            content=open(file_path, 'rb').read(),
            content_type='image/jpeg',
        )
        validate_image(test_logo)

    def test_allowed_size_valid(self):
        """ Another way to set 'absolute path'. Need for correct work 'pytest' command from Terminal."""
        file_path = str(settings.BASE_DIR) + r'\comments\tests\3.png'
        test_logo = SimpleUploadedFile(
            name='3.png',
            content=open(file_path, 'rb').read(),
            content_type='image/png',
        )
        validate_image(test_logo)


class TestValidateOrderingFilter:
    @pytest.mark.django_db
    def test_menu_filter_reverse_ordering_positive(self, api_client, comments):
        response = api_client.get(
            reverse('comments'), **{'QUERY_STRING': 'ordering=username'}, format='json',)
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json

    def test_new_comment(self, api_client):
        response0 = api_client.get(
            reverse('new_comment'), format='json',)
        data = {'username': 'randomizer',
                'email': 'randomizer@ukr.net',
                'text': 'andomizer.random_text(i*10)',
                'captcha': response0.json()['captcha'],
                'image': None,
                }
        response = api_client.post(
            reverse('new_comment'), data=data, format='json',)
        response_json = response.json()
        assert response_json