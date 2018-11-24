import jwt
from rest_framework import status, viewsets
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Post, User, Likes
from api.renderers import UserJSONRenderer
from api.serializers import PostSerializer, UserSerializer, LikeSerializer, JwtDecode
from starnavi.settings import SECRET_KEY
from .serializers import LoginSerializer, RegistrationSerializer
import api.backends as backends


class PostView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    http_method_names = ['get', 'post']
    authentication_classes = (backends.JWTAuthentication,)

    def create(self, request, **kwargs):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Wrong data"}, status=status.HTTP_400_BAD_REQUEST)


class PostOneView(APIView):
    serializer_class = PostSerializer
    authentication_classes = (backends.JWTAuthentication,)

    def get(self, request, pk, **kwargs):
        query = Post.objects.get(pk=pk)
        serializer = PostSerializer(query)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, **kwargs):
        query = Post.objects.get(pk=pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk, **kwargs):
        instance = Post.objects.get(pk=pk)
        serializer = PostSerializer(data=request.data)
        post = serializer.update(instance, request.data)
        return Response(post.data, status=status.HTTP_200_OK)


class LikesView(APIView):
    def post(self, request, pk, **kwargs):
        user_data = JwtDecode.decode(request)

        post = Post.objects.get(pk=pk)
        user = User.objects.get(pk=user_data['id'])

        query = Likes.objects.filter(user=user, post=post)
        if query.exists():
            query.delete()
            return Response({"message": "Successful unlike"}, status=status.HTTP_200_OK)

        query = Likes.objects.create(user=user, post=post)
        query.save()
        serializer = LikeSerializer(query)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = User.objects.all()
        result = UserSerializer(queryset, many=True)
        return Response(result.data)


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
