from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

from .validators import validate_year


class User(AbstractUser):
    """User storage model."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (USER, 'user'), (MODERATOR, 'moderator'), (ADMIN, 'admin')
    )
    email = models.EmailField(max_length=60, unique=True)
    bio = models.CharField(max_length=200, blank=True)
    role = models.CharField(
        max_length=30, choices=ROLE_CHOICES, default=USER
    )

    def save(self, *args, **kwargs):
        if self.role == self.ADMIN:
            self.is_superuser = True
        elif self.role == self.MODERATOR:
            self.is_staff = True
        super().save(*args, **kwargs)


class Category(models.Model):
    """Category storage model."""

    name = models.CharField(
        'Name of category', max_length=256, db_index=True)
    slug = models.SlugField('Short name', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.slug


class Genre(models.Model):
    """Genre storage model."""

    name = models.CharField('Name of Genre', max_length=256, db_index=True)
    slug = models.SlugField('Short name', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.slug


class Title(models.Model):
    """Title storage model."""

    name = models.CharField('Name', max_length=256, db_index=True)
    year = models.PositiveSmallIntegerField(
        verbose_name='Year', db_index=True,
        validators=[validate_year])
    description = models.TextField(verbose_name='Description')
    genre = models.ManyToManyField(
        Genre, verbose_name='Genre', blank=True)
    category = models.ForeignKey(
        Category, verbose_name='Category',
        on_delete=models.SET_NULL, related_name="titles",
        blank=True, null=True)

    class Meta:
        verbose_name = 'Work'
        verbose_name_plural = 'Works'

    def __str__(self):
        return self.name


class Review(models.Model):
    """Review storage model."""

    text = models.TextField('Review text', max_length=200)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    score = models.IntegerField(
        'Рейтинг',
        validators=[MinValueValidator(0, 'At least 0'),
                    MaxValueValidator(10, 'No more than 10')]
    )
    pub_date = models.DateTimeField('Publication date', auto_now_add=True)
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review')
        ]
        ordering = ('-pub_date',)
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Comment storage model."""

    text = models.TextField('Comment', max_length=200)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField('Publication date', auto_now_add=True)

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return self.text
