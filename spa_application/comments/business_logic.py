import re
import random
import string
from io import BytesIO

from PIL import Image as PILImage
from django.core.files.base import ContentFile
from django.core.cache import cache

from comments.models import Comment
from spa_application.settings import CACHE_TIMEOUT


def validate_image(image):
    if image:
        try:
            img = PILImage.open(image)
            img_format = img.format.upper()
            print(img_format)
            if img_format not in ['JPEG', 'GIF', 'PNG']:
                return {'error': 'Upload image only in next formats JPEG, GIF, PNG'}
        except Exception as e:
            print(e)
            return {'error': '_Upload image only in next formats JPEG, GIF, PNG'}
        img_width, img_height = img.size
        if img_width > 320 or img_height > 240:
            img.thumbnail((320, 240))
            img_io = BytesIO()
            img.save(img_io, format=img_format)
            img_data = img_io.getvalue()
            image = ContentFile(img_data, name=image.name)
    return image


def validate_text(text):
    open_tags = re.findall(r'<([^/][^>]*)>', text)
    cleaned_open_tags = [tag.split()[0] if ' ' in tag else tag for tag in open_tags]
    closed_tags = re.findall(r'</([^>]*)>', text)
    cleaned_closed_tags = [tag.split()[0] if ' ' in tag else tag for tag in closed_tags]
    if cleaned_open_tags != cleaned_closed_tags:
        return {'error': 'Verify your text. You have open Tags'}

    for tag in cleaned_open_tags:
        if tag not in ['a', 'code', 'i', 'strong']:
            return {'error': 'Use only allowed Tags: <a href=”” title=””> </a> <code> </code> <i> </i>'
                             ' <strong> </strong>'}


def cascade_display(serializer, comment):
    data = serializer(comment).data
    descendants = comment.get_descendants()
    if descendants.exists():
        data['descendants'] = [cascade_display(serializer, comment) for comment in descendants]
    return data


def perform_add_root(data):
    img = validate_image(data.pop('image'))
    if isinstance(img, dict):
        error = img
        return error
    if error := validate_text(data['text']):
        return error
    root = Comment.add_root(image=img, **data)
    return root


def perform_add_child(data, comment):
    img = validate_image(data.pop('image'))
    if isinstance(img, dict):
        error = img
        return error
    if error := validate_text(data['text']):
        return error
    reply = comment.add_child(image=img, **data)
    return reply


def generate_captcha(request):
    sessionid = getattr(request.session, 'session_key', None)
    if captcha := cache.get(f'{sessionid}', None):
        return captcha
    captcha = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(6))
    cache.set(f'{sessionid}', captcha, CACHE_TIMEOUT['captcha'])
    return captcha


def check_captcha(request, captcha):
    sessionid = getattr(request.session, 'session_key', None)
    cache_captcha = cache.get(f'{sessionid}', None)
    if not cache_captcha:
        return {'error': 'Your captcha is already expired. Request a new one.'}
    if cache_captcha != captcha:
        return {'error': 'Not valid captcha.'}
    cache.delete(f'{sessionid}')
