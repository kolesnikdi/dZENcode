from rest_framework import serializers
from comments.models import Comment


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'username', 'created_date', 'email', 'home_page', 'text', 'image']

        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
        }


class PostCommentSerializer(serializers.ModelSerializer):
    captcha = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Comment
        fields = ['id', 'username', 'created_date', 'email', 'home_page', 'text', 'image', 'captcha']

        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
        }
