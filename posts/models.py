from django.db import models

from django.contrib.auth import get_user_model
from django.utils.text import Truncator

     
class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name = 'Заголовок', 
                        help_text='Задайте заголовок')
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name = 'Описание', max_length=400, 
                        help_text='Описание группы. Не более 400 символов')
    
    def __str__(self):
        return self.title

User = get_user_model()

class Post(models.Model):
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, 
                                                related_name='author')
    group = models.ForeignKey(Group, blank=True, null=True, 
                            on_delete=models.CASCADE, related_name='group', 
                            verbose_name='Группа')
    image = models.ImageField(upload_to='posts/', blank=True, null=True, 
                            verbose_name='Картинка')
    objects = models.Manager()

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        self.text = Truncator(self.text).words(10)
        return self.text[:15]

class Comment(models.Model):
    post = models.ForeignKey(Post, blank=False, null=False, 
                        verbose_name="Публикация", on_delete=models.CASCADE, 
                        related_name="comments")
    author = models.ForeignKey(User, blank=False, null=False, 
                        verbose_name="Автор", on_delete=models.CASCADE, 
                        related_name="comments")
    text = models.TextField(blank=False, null=False, 
                        verbose_name="Текст комментария")
    created = models.DateTimeField(verbose_name="Дата публикации", 
                        auto_now_add=True)

class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower", null=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following", null=True)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique follow')]
