from django.db import models
from django.db.models import Avg
from django.contrib.auth import get_user_model


User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField()
    genre = models.ManyToManyField(Genre, related_name='titles')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='titles')

    rating = models.FloatField(null=True, blank=True)

    def update_rating(self):
        avg_rating = self.reviews.aggregate(Avg('score'))['score__avg']
        self.rating = avg_rating
        self.save()

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    score = models.IntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')

    class Meta:
        unique_together = ('title', 'author')


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre, on_delete=models.CASCADE, related_name='genre_titles')
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='genre_titles')

    class Meta:
        unique_together = ('genre', 'title')
