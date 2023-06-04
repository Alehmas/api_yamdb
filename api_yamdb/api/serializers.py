from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """Serialization of all reciew requests."""

    author = SlugRelatedField(slug_field='username', read_only=True)
    score = serializers.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )

    def validate(self, obj):
        request = self.context['request']
        if request.method != 'POST':
            return obj
        title = get_object_or_404(
            Title, pk=self.context['view'].kwargs.get('title_id')
        )
        if Review.objects.filter(title=title,
                                 author=request.user).exists():
            raise ValidationError('Re-comment')
        return obj

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    """Serialization of all comment requests."""

    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class GenreSerializer(serializers.ModelSerializer):
    """Serialization of all genre requests."""

    class Meta:
        exclude = ('id',)
        model = Genre
        lookup_field = 'slug'


class CategorySerializer(serializers.ModelSerializer):
    """Serialization of all category requests."""

    class Meta:
        exclude = ('id',)
        model = Category
        lookup_field = 'slug'


class TitleSerializerGet(serializers.ModelSerializer):
    """Serialization of GET title requests."""

    genre = GenreSerializer(many=True, required=False)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        model = Title


class TitleSerializer(serializers.ModelSerializer):
    """Serialization of POST, PUTCH, DELETE title requests."""

    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug',
        queryset=Genre.objects.all(), required=False
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category')
        model = Title

    def validate_year(self, value):
        today = timezone.now().year
        if value > today:
            raise serializers.ValidationError('Check the year!')
        return value


class AuthSerializer(serializers.ModelSerializer):
    """Serialization of all auth requests."""

    class Meta:
        model = User
        fields = ('username', 'email')
        qs = User.objects.all()
        extra_kwargs = {
            'username': {
                'validators': [
                    UniqueValidator(
                        queryset=qs
                    )
                ]
            },
            'email': {
                'validators': [
                    UniqueValidator(
                        queryset=qs
                    )
                ]
            }
        }

    def validate_username(self, username):
        if username == 'me':
            raise ValidationError('"me" is not valid username')
        if len(username) < 6:
            raise ValidationError(
                'Username must be between 6 and 15 characters long'
            )
        return username

    def get_confirm_code(self, **kwargs):
        user = User.objects.create(
            **self.validated_data, last_login=timezone.now()
        )
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            "Confirmation code",
            f"Your confirmation code: {confirmation_code}",
            settings.ADMIN_EMAIL,
            [self.validated_data['email']],
        )


class UserSerializer(serializers.ModelSerializer):
    """Serialization of all user requests except admin."""

    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('bio', 'email', 'first_name',
                  'last_name', 'role', 'username')


class AdminUserSerializer(serializers.ModelSerializer):
    """Serialization of all admin requests."""

    class Meta:
        model = User
        fields = ('bio', 'email', 'first_name',
                  'last_name', 'role', 'username')


class TokenSerializer(serializers.ModelSerializer):
    """Serialization request token."""

    confirmation_code = serializers.CharField(allow_blank=False)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
