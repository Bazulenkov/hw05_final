from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    """ Форма модели Post, добавляем через нее новую запись и редактируем имеющуюся запись """
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        localized_fields = '__all__'


class CommentForm(ModelForm):
    """ Форма модели Comment, добавляем через нее новый комментарий """
    class Meta:
        model = Comment
        fields = ('text',)
        localized_fields = '__all__'
