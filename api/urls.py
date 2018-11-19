from django.conf.urls import url
from api.views import PostView, RegistrationAPIView, LoginAPIView, UserRetrieveUpdateAPIView

urlpatterns = [
    url(r'^post/(?P<pk>\d+)/$', PostView.as_view()),
    url(r'^user/?$', UserRetrieveUpdateAPIView.as_view()),
    url(r'^reg/?$', RegistrationAPIView.as_view()),
    url(r'^log/?$', LoginAPIView.as_view()),
]
