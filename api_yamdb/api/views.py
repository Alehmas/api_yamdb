from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Title, Review
from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet
from .permissions import (IsAdminOrAuthorOrReadOnly, CustomAdminPermission,
                          SafeMethodAdminPermission)
from .serializers import (AuthSerializer, CategorySerializer, GenreSerializer,
                          TitleSerializer, TitleSerializerGet,
                          AdminUserSerializer, CommentSerializer,
                          ReviewSerializer, UserSerializer, TokenSerializer)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    list:
    Getting a list of all users.

    create:
    Adding a user.

    retrieve:
    Getting a user by username or getting your account information.

    update:
    Changing user data by username.

    partial_update:
    Change your account information.

    destroy:
    Deleting a user by username.
    """
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = (CustomAdminPermission,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('username',)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(detail=False, methods=['GET', 'PATCH'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        """Getting or changing your account information."""
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            if user.role == 'user':
                serializer = UserSerializer(user,
                                            data=request.data, partial=True)
            else:
                serializer = AdminUserSerializer(user, data=request.data,
                                                 partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    list:
    Getting a list of all reviews.

    create:
    Adding a new review.

    retrieve:
    Get review by id.

    partial_update:
    Partial review update by id.

    destroy:
    Delete review by id.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminOrAuthorOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """
    list:
    Getting a list of all comments on a review.

    create:
    Adding a comment to a review.

    retrieve:
    Get a comment for a review by id.

    partial_update:
    Partially update the review comment by id.

    destroy:
    Deleting a review comment.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAdminOrAuthorOrReadOnly]

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class CategoryViewSet(ListCreateDestroyViewSet):
    """
    list:
    Getting a list of all categories.

    create:
    Adding a new category.

    destroy:
    Deleting a category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (SafeMethodAdminPermission,)


class GenryViewSet(ListCreateDestroyViewSet):
    """
    list:
    Getting a list of all genres.

    create:
    Adding a Genre.

    destroy:
    Removing a genre.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (SafeMethodAdminPermission,)


class TitleViewSet(viewsets.ModelViewSet):
    """
    list:
    Getting a list of all products.

    create:
    Adding a product.

    retrieve:
    Getting information about a product.

    partial_update:
    Partial update of information about the product.

    destroy:
    Deleting a product.
    """
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = TitleFilter
    permission_classes = (SafeMethodAdminPermission,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleSerializerGet
        return TitleSerializer


class AuthViewSet(viewsets.GenericViewSet):
    """
    Create new User.
    Getting a JWT token in exchange for username and confirmation code..
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = AuthSerializer

    @action(detail=False, methods=['POST'])
    def signup(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.get_confirm_code()
        return Response(serializer.data, status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def token(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, username=serializer.validated_data['username']
        )
        confirmation_code = serializer.validated_data['confirmation_code']
        if not default_token_generator.check_token(user, confirmation_code):
            return Response('Wrong confirm code',
                            status=status.HTTP_400_BAD_REQUEST)
        user.is_active = True
        user.save()
        refresh = RefreshToken.for_user(user)
        tokens = dict(access_token=str(refresh.access_token),
                      refresh_token=str(refresh))
        return Response(tokens, status=status.HTTP_200_OK)
