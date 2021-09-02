from django.urls import path
from django.conf.urls import url, include


from rest_framework_swagger.views import get_swagger_view

from .views import CreatePost, PostList, PostDetails, Analytics, analytics_view

schema_view = get_swagger_view(title='Props API')

urlpatterns = [
    url('createpost', CreatePost.as_view(), name='Create New Post'),
    url('getpostdetails', PostDetails.as_view(), name='Get Post Details'),
    url('getpostlist', PostList.as_view(), name='Get Post List'),
    url('getanalyticsdata', Analytics.as_view(), name='Get Post Analytics'),
    path('analytics', analytics_view, name='Analytics View'),
    url(r'^$', schema_view),
]