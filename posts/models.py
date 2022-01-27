from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Group(models.Model):
    """Модель группы постов"""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(max_length=50)

    def __str__(self):
        return self.title


class Post(models.Model):
    """Модель записи/поста"""

    text = models.TextField(help_text=_("Post's content"))
    pub_date = models.DateTimeField(
        _("date published"), auto_now_add=True, db_index=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="post_author"
    )
    group = models.ForeignKey(
        Group,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="post_group",
    )
    image = models.ImageField(upload_to="posts/", blank=True, null=True)

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментария"""

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comment_post"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comment_author"
    )
    text = models.TextField(help_text=_("Comment's content"))
    created = models.DateTimeField(_("date commented"), auto_now_add=True)

    def __str__(self):
        return self.text


class Follow(models.Model):
    """Модель подписки на авторов"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )

    class Meta:
        unique_together = ["user", "author"]

    def __str__(self):
        return f"{self.user}-{self.author}"
