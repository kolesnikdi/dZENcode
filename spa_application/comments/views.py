import base64
from captcha.image import ImageCaptcha
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_cookie
from rest_framework.filters import OrderingFilter
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from comments.serializers import CommentSerializer, PostCommentSerializer
from comments.business_logic import (perform_add_root, perform_add_child, cascade_display, generate_captcha,
                                     check_captcha)
from comments.models import Comment
from spa_application.settings import CACHE_TIMEOUT


class NewCommentView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = PostCommentSerializer

    @method_decorator(cache_page(CACHE_TIMEOUT['new_comments']))
    @method_decorator(vary_on_cookie)
    def get(self, request, *args, **kwargs):
        captcha = generate_captcha(request)
        print(f'<<<<<<captcha_for_manual_test>>>>>>>>{captcha}')
        image_captcha = ImageCaptcha(width=200, height=150)
        captcha_image = image_captcha.generate(captcha)
        captcha_image = base64.b64encode(captcha_image.getvalue()).decode()
        return Response({'captcha': captcha_image}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if error := check_captcha(request, serializer.validated_data.pop('captcha')):
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        new_comment = perform_add_root(serializer.validated_data)
        if isinstance(new_comment, dict):
            error = new_comment
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(CommentSerializer(instance=new_comment).data, status=status.HTTP_200_OK)


class ReplyCommentView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = PostCommentSerializer
    queryset = Comment.objects.all()
    lookup_field = 'id'

    @method_decorator(cache_page(CACHE_TIMEOUT['reply_comments']))
    @method_decorator(vary_on_cookie)
    def get(self, request, *args, **kwargs):
        captcha = generate_captcha(request)
        print(f'<<<<<<captcha_for_manual_test>>>>>>>>{captcha}')
        image_captcha = ImageCaptcha(width=200, height=150)
        captcha_image = image_captcha.generate(captcha)
        captcha_image = base64.b64encode(captcha_image.getvalue()).decode()
        return Response({'captcha': captcha_image}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        root = self.get_object()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if error := check_captcha(request, serializer.validated_data.pop('captcha')):
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        new_comment = perform_add_child(serializer.validated_data, root)
        if isinstance(new_comment, dict):
            error = new_comment
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        else:
            response = CommentSerializer(instance=root).data
            response['my_reply'] = CommentSerializer(instance=new_comment).data
            return Response(response, status=status.HTTP_200_OK)


class ListCommentView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    lookup_field = 'id'

    @method_decorator(cache_page(CACHE_TIMEOUT['list_comment']))
    def get(self, request, *args, **kwargs):
        comment = self.get_object()
        response = cascade_display(self.serializer_class, comment)
        return Response(response, status=status.HTTP_200_OK)


class ListCommentsView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CommentSerializer
    queryset = Comment.get_root_nodes().order_by('-created_date')
    ordering_fields = ['username', 'email', 'created_date']
    ordering_filter = OrderingFilter()
    pagination_class = PageNumberPagination

    @method_decorator(cache_page(CACHE_TIMEOUT['list_comments']))
    def get(self, request, *args, **kwargs):
        queryset = self.ordering_filter.filter_queryset(self.request, self.get_queryset(), self)
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset=queryset, request=request, view=self)
        response = self.serializer_class(paginated_queryset, many=True).data
        return Response(response, status=status.HTTP_200_OK)
