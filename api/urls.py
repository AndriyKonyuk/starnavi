from django.conf.urls import url
from api.views import PostView, RegistrationAPIView, LoginAPIView, UserRetrieveUpdateAPIView, PostOneView, LikesView

urlpatterns = [
    url(r'^post/?$', PostView.as_view({"get": "list", "post": "create"})),
    url(r'^post/(?P<pk>[0-9]+)/$', PostOneView.as_view()),
    url(r'^like/(?P<pk>[0-9]+)/$', LikesView.as_view()),
    url(r'^user/?$', UserRetrieveUpdateAPIView.as_view()),
    url(r'^reg/?$', RegistrationAPIView.as_view()),
    url(r'^log/?$', LoginAPIView.as_view()),
]
