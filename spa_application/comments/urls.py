from django.urls import path

from comments.views import NewCommentView, ReplyCommentView, ListCommentView, ListCommentsView

urlpatterns = [
    path('comments/', ListCommentsView.as_view(), name='comments'),
    path('comments/new/', NewCommentView.as_view(), name='new_comment'),
    path('comments/<int:id>/', ListCommentView.as_view(), name='comment'),
    path('comments/<int:id>/new', ReplyCommentView.as_view(), name='reply_comment'),
]
