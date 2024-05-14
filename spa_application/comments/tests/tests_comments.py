import pytest
import time
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse
from rest_framework import status

from comments.models import Comment


class TestListCommentsView:
    @pytest.mark.django_db
    def test_list_comments_valid_lifo_created_date_sorting(self, api_client, comments):
        response = api_client.get(reverse('comments'), **{'QUERY_STRING': 'page=2'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json
        assert len(response_json) == 4
        assert response_json[0]['created_date'] > response_json[3]['created_date']
        response = api_client.get(reverse('comments'), format='json')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert len(response_json) == 25
        assert response_json[0]['created_date'] > response_json[24]['created_date']

    @pytest.mark.django_db
    def test_list_comments_valid_created_date_sorting(self, api_client, comments):
        response = api_client.get(reverse('comments'), **{'QUERY_STRING': 'ordering=created_date'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert len(response_json) == 25
        assert response_json[0]['created_date'] < response_json[24]['created_date']

    @pytest.mark.django_db
    def test_list_comments_valid_username_sorting(self, api_client, comments):
        response = api_client.get(reverse('comments'), **{'QUERY_STRING': 'ordering=username'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert len(response_json) == 25
        assert response_json[0]['username'] < response_json[24]['username']

    @pytest.mark.django_db
    def test_list_comments_valid_lifo_username_sorting(self, api_client, comments):
        response = api_client.get(reverse('comments'), **{'QUERY_STRING': 'ordering=-username'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert len(response_json) == 25
        assert response_json[0]['username'] > response_json[24]['username']

    @pytest.mark.django_db
    def test_list_comments_valid_email_sorting(self, api_client, comments):
        response = api_client.get(reverse('comments'), **{'QUERY_STRING': 'ordering=email'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert len(response_json) == 25
        assert response_json[0]['email'] < response_json[24]['email']

    @pytest.mark.django_db
    def test_list_comments_valid_lifo_email_sorting(self, api_client, comments):
        response = api_client.get(reverse('comments'), **{'QUERY_STRING': 'ordering=-email'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert len(response_json) == 25
        assert response_json[0]['email'] > response_json[24]['email']

    @pytest.mark.django_db
    def test_list_comments_invalid_sorting(self, api_client, comments):
        response = api_client.get(reverse('comments'), **{'QUERY_STRING': 'ordering=-text'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert len(response_json) == 25
        assert response_json[0]['created_date'] > response_json[3]['created_date']

    @pytest.mark.django_db
    def test_list_comments_nonexistent_sorting(self, api_client, comments):
        response = api_client.get(reverse('comments'), **{'QUERY_STRING': 'ordering=ddddd'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert len(response_json) == 25
        assert response_json[0]['created_date'] > response_json[3]['created_date']


class TestListCommentView:

    @pytest.mark.django_db
    def test_list_comment_valid_cascade_view(self, api_client, comments):
        response = api_client.get(reverse('comment',  args=[comments[0].id]), format='json')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json['id'] == comments[0].id
        assert response_json['descendants']
        assert response_json['descendants'][0]['id'] == comments[0].id + 1
        assert response_json['descendants'][0]['descendants']
        assert response_json['descendants'][0]['descendants'][0]['id'] == comments[0].id + 2

    @pytest.mark.django_db
    def test_list_comment_invalid_id(self, api_client, comments):
        response = api_client.get(reverse('comment',  args=[10000]), format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()['detail'] == 'No Comment matches the given query.'


class TestNewCommentView:
    settings.CACHE_TIMEOUT['new_comments'] = 1
    @pytest.mark.django_db
    def test_new_comment_valid(self, api_client, randomizer, valid_img):
        response = api_client.get(reverse('new_comment'), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        data = {
            'username': randomizer.username(),
            'email': randomizer.email(),
            'text': '<code>print("Hello, World!")</code>',
            'home_page': '',
            'image': valid_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json
        data_for_check = Comment.objects.filter(username=data['username']).first()
        assert response_json['email'] == data_for_check.email
        assert response_json['id'] == data_for_check.id
        assert response_json['text'] == data_for_check.text
        assert response_json['home_page'] == data_for_check.home_page
        assert data_for_check.image.name in response_json['image']

    @pytest.mark.django_db
    def test_new_comment_big_img(self, api_client, randomizer, big_img):
        time.sleep(2)
        response = api_client.get(reverse('new_comment'), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        data = {
            'username': randomizer.username(),
            'email': randomizer.email(),
            'text': '<code>print("Hello, World!")</code>',
            'home_page': '',
            'image': big_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json
        data_for_check = Comment.objects.filter(username=data['username']).first()
        assert response_json['email'] == data_for_check.email
        assert response_json['id'] == data_for_check.id
        assert response_json['text'] == data_for_check.text
        assert response_json['home_page'] == data_for_check.home_page
        assert data_for_check.image.name in response_json['image']
        assert data_for_check.image.height == 240
        assert data_for_check.image.width == 320

    @pytest.mark.django_db
    def test_new_comment_invalid_format_img(self, api_client, randomizer, invalid_format_img):
        time.sleep(2)
        response = api_client.get(reverse('new_comment'), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        data = {
            'username': randomizer.username(),
            'email': randomizer.email(),
            'text': '<code>print("Hello, World!")</code>',
            'home_page': '',
            'image': invalid_format_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert response.json()['image'] == ['Upload a valid image. The file you uploaded was either not an image or a'
                                            ' corrupted image.']

    @pytest.mark.django_db
    def test_new_comment_none_username(self, api_client, randomizer, valid_img):
        time.sleep(2)
        response = api_client.get(reverse('new_comment'), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        data = {
            'username': '',
            'email': randomizer.email(),
            'text': '<code>print("Hello, World!")</code>',
            'home_page': '',
            'image': valid_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['username'] == ['This field may not be blank.']

    @pytest.mark.django_db
    def test_new_comment_none_email(self, api_client, randomizer, valid_img):
        time.sleep(2)
        response = api_client.get(reverse('new_comment'), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        data = {
            'username': randomizer.username(),
            'email': '',
            'text': '<code>print("Hello, World!")</code>',
            'home_page': '',
            'image': valid_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['email'] == ['This field may not be blank.']

    @pytest.mark.django_db
    def test_new_comment_expired_captcha(self, api_client, randomizer, valid_img):
        time.sleep(2)
        response = api_client.get(reverse('new_comment'), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        cache.delete(f'{sessionid}')
        data = {
            'username': randomizer.username(),
            'email': randomizer.email(),
            'text': '<code>print("Hello, World!")</code>',
            'home_page': '',
            'image': valid_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['error'] == 'Your captcha is already expired. Request a new one.'

    @pytest.mark.django_db
    def test_new_comment_invalid_captcha(self, api_client, randomizer, valid_img):
        time.sleep(2)
        response = api_client.get(reverse('new_comment'), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        data = {
            'username': randomizer.username(),
            'email': randomizer.email(),
            'text': '<code>print("Hello, World!")</code>',
            'home_page': '',
            'image': valid_img,
            'captcha': 'captcha',
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['error'] == 'Not valid captcha.'

    @pytest.mark.django_db
    def test_new_comment_to_big_text(self, api_client, randomizer, valid_img):
        time.sleep(2)
        response = api_client.get(reverse('new_comment'), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        data = {
            'username': randomizer.username(),
            'email': randomizer.email(),
            'text': randomizer.random_text(102401),
            'home_page': '',
            'image': valid_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['text'] == ['Ensure this field has no more than 102400 characters.']

    @pytest.mark.django_db
    def test_new_comment_invalid_open_tags(self, api_client, randomizer, valid_img):
        time.sleep(2)
        response = api_client.get(reverse('new_comment'), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        data = {
            'username': randomizer.username(),
            'email': randomizer.email(),
            'text': '<codeprint("Hello, World!")</code>',
            'home_page': '',
            'image': valid_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['error'] == 'Verify your text. You have open Tags'

    @pytest.mark.django_db
    def test_new_comment_invalid_closed_tags(self, api_client, randomizer, valid_img):
        time.sleep(2)
        response = api_client.get(reverse('new_comment'), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        data = {
            'username': randomizer.username(),
            'email': randomizer.email(),
            'text': '<code>print("Hello, World!")/code>',
            'home_page': '',
            'image': valid_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['error'] == 'Verify your text. You have open Tags'

    @pytest.mark.django_db
    def test_new_comment_mot_allowed_tags(self, api_client, randomizer, valid_img):
        time.sleep(2)
        response = api_client.get(reverse('new_comment'), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        data = {
            'username': randomizer.username(),
            'email': randomizer.email(),
            'text': '<abrr>print("Hello, World!")</abrr>',
            'home_page': '',
            'image': valid_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['error'] == ('Use only allowed Tags: <a href=”” title=””> </a> <code> </code> <i> </i>'
                                            ' <strong> </strong>')


class TestReplyCommentView:
    settings.CACHE_TIMEOUT['reply_comments'] = 1
    @pytest.mark.django_db
    def test_reply_comment_valid(self, api_client, randomizer, valid_img, comments):
        response = api_client.get(reverse('reply_comment', args=[comments[0].id]), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        data = {
            'username': randomizer.username(),
            'email': randomizer.email(),
            'text': '<code>print("Hello, World!")</code>',
            'home_page': '',
            'image': valid_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('reply_comment', args=[comments[0].id]), data=data, format='multipart')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()['my_reply']
        assert response_json
        data_for_check = Comment.objects.filter(username=data['username']).first()
        assert response_json['email'] == data_for_check.email
        assert response_json['id'] == data_for_check.id
        assert response_json['text'] == data_for_check.text
        assert response_json['home_page'] == data_for_check.home_page
        assert data_for_check.image.name in response_json['image']

    @pytest.mark.django_db
    def test_reply_comment_big_img(self, api_client, randomizer, big_img, comments):
        time.sleep(2)
        response = api_client.get(reverse('reply_comment', args=[comments[0].id]), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        data = {
            'username': randomizer.username(),
            'email': randomizer.email(),
            'text': '<code>print("Hello, World!")</code>',
            'home_page': '',
            'image': big_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('reply_comment', args=[comments[0].id]), data=data, format='multipart')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()['my_reply']
        assert response_json
        data_for_check = Comment.objects.filter(username=data['username']).first()
        assert response_json['email'] == data_for_check.email
        assert response_json['id'] == data_for_check.id
        assert response_json['text'] == data_for_check.text
        assert response_json['home_page'] == data_for_check.home_page
        assert data_for_check.image.name in response_json['image']
        assert data_for_check.image.height == 240
        assert data_for_check.image.width == 320

    @pytest.mark.django_db
    def test_reply_comment_invalid_format_img(self, api_client, randomizer, invalid_format_img, comments):
        time.sleep(2)
        response = api_client.get(reverse('reply_comment', args=[comments[0].id]), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        data = {
            'username': randomizer.username(),
            'email': randomizer.email(),
            'text': '<code>print("Hello, World!")</code>',
            'home_page': '',
            'image': invalid_format_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['image'] == ['Upload a valid image. The file you uploaded was either not an image or a'
                                            ' corrupted image.']

    @pytest.mark.django_db
    def test_reply_comment_none_username(self, api_client, randomizer, valid_img, comments):
        time.sleep(2)
        response = api_client.get(reverse('reply_comment', args=[comments[0].id]), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        data = {
            'username': '',
            'email': randomizer.email(),
            'text': '<code>print("Hello, World!")</code>',
            'home_page': '',
            'image': valid_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['username'] == ['This field may not be blank.']

    @pytest.mark.django_db
    def test_reply_comment_none_email(self, api_client, randomizer, valid_img, comments):
        time.sleep(2)
        response = api_client.get(reverse('reply_comment', args=[comments[0].id]), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        data = {
            'username': randomizer.username(),
            'email': '',
            'text': '<code>print("Hello, World!")</code>',
            'home_page': '',
            'image': valid_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['email'] == ['This field may not be blank.']

    @pytest.mark.django_db
    def test_reply_comment_expired_captcha(self, api_client, randomizer, valid_img, comments):
        time.sleep(2)
        response = api_client.get(reverse('reply_comment', args=[comments[0].id]), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        cache.delete(f'{sessionid}')
        data = {
            'username': randomizer.username(),
            'email': randomizer.email(),
            'text': '<code>print("Hello, World!")</code>',
            'home_page': '',
            'image': valid_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['error'] == 'Your captcha is already expired. Request a new one.'

    @pytest.mark.django_db
    def test_reply_comment_invalid_captcha(self, api_client, randomizer, valid_img, comments):
        time.sleep(2)
        response = api_client.get(reverse('reply_comment', args=[comments[0].id]), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        data = {
            'username': randomizer.username(),
            'email': randomizer.email(),
            'text': '<code>print("Hello, World!")</code>',
            'home_page': '',
            'image': valid_img,
            'captcha': 'captcha',
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['error'] == 'Not valid captcha.'

    @pytest.mark.django_db
    def test_reply_comment_to_big_text(self, api_client, randomizer, valid_img, comments):
        time.sleep(2)
        response = api_client.get(reverse('reply_comment', args=[comments[0].id]), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        data = {
            'username': randomizer.username(),
            'email': randomizer.email(),
            'text': randomizer.random_text(102401),
            'home_page': '',
            'image': valid_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['text'] == ['Ensure this field has no more than 102400 characters.']

    @pytest.mark.django_db
    def test_reply_comment_invalid_open_tags(self, api_client, randomizer, valid_img, comments):
        time.sleep(2)
        response = api_client.get(reverse('reply_comment', args=[comments[0].id]), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        data = {
            'username': randomizer.username(),
            'email': randomizer.email(),
            'text': '<codeprint("Hello, World!")</code>',
            'home_page': '',
            'image': valid_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['error'] == 'Verify your text. You have open Tags'

    @pytest.mark.django_db
    def test_reply_comment_invalid_closed_tags(self, api_client, randomizer, valid_img, comments):
        time.sleep(2)
        response = api_client.get(reverse('reply_comment', args=[comments[0].id]), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        data = {
            'username': randomizer.username(),
            'email': randomizer.email(),
            'text': '<code>print("Hello, World!")/code>',
            'home_page': '',
            'image': valid_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['error'] == 'Verify your text. You have open Tags'

    @pytest.mark.django_db
    def test_reply_comment_mot_allowed_tags(self, api_client, randomizer, valid_img, comments):
        time.sleep(2)
        response = api_client.get(reverse('reply_comment', args=[comments[0].id]), format='json')
        assert response.status_code == status.HTTP_200_OK
        sessionid = response.cookies['sessionid'].value
        captcha = cache.get(f'{sessionid}', None)
        data = {
            'username': randomizer.username(),
            'email': randomizer.email(),
            'text': '<abrr>print("Hello, World!")</abrr>',
            'home_page': '',
            'image': valid_img,
            'captcha': captcha,
        }
        response = api_client.post(reverse('new_comment'), data=data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['error'] == ('Use only allowed Tags: <a href=”” title=””> </a> <code> </code> <i> </i>'
                                            ' <strong> </strong>')
