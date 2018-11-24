import jwt
from django.contrib.auth import authenticate
from rest_framework import serializers

from api.models import Post, User, Likes
from starnavi.settings import SECRET_KEY


class JwtDecode:
    @classmethod
    def decode(cls, request):
        # token = request.META.get('token')
        token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwiZXhwIjoxNTQ3NjY1NzI5fQ.vJTlWZ6GXbpC9d0dx8F4lLj1LNs2xtN95C-ZhIcz6aI"
        user_data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return user_data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'id')


class PostSerializer(serializers.ModelSerializer, JwtDecode):
    def create(self, validated_data):
        request = self.context.get("request")
        user_data = self.decode(request)

        user = User.objects.get(pk=user_data['id'])
        query = Post(user=user,
                     title=validated_data["title"],
                     content=validated_data["content"],
                     created_date=validated_data["created_date"], )
        query.save()
        return query

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.created_date = validated_data.get('created', instance.created_date)
        instance.save()
        return PostSerializer(instance)

    class Meta:
        model = Post
        fields = ('__all__')


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    post = PostSerializer()

    class Meta:
        model = Likes
        fields = ('__all__')


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'token']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    _generate_jwt_token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)
        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        return {
            'email': user.email,
            'username': user.username,
            'token': user.token
        }
