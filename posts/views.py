from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm, CommentForm
from .models import Post, Group, Comment, Follow, User


def index(request):
    """Обрабатывает главную страницу"""
    post_list = Post.objects.select_related('author').order_by('-pub_date').all()
    # показывать по 10 записей на странице.
    paginator = Paginator(post_list, 10)
    # переменная в URL с номером запрошенной страницы
    page_number = request.GET.get('page')
    # получить записи с нужным смещением
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    """Обрабатывает страницу с группами"""
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.select_related('author').filter(group=group).order_by('-pub_date').all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    """Обрабатываем страницу ввода нового поста"""
    post = Post(author=request.user)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('/')
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    """ Обрабатывает страницу профиля автора/пользователя с постами """
    user_profile = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user_profile).order_by('-pub_date')
    paginator = Paginator(post_list, 5)
    # переменная в URL с номером запрошенной страницы
    page_number = request.GET.get('page')
    # получить записи с нужным смещением
    page = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = user_profile.following.filter(user=request.user).exists()
    return render(request, 'profile.html', {'page': page, 'paginator': paginator,
                                            'user_profile': user_profile, 'following': following})


def post_view(request, username, post_id):
    """ Обрабатывает страницу просмотра отдельной записи """
    user_profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=user_profile)
    # дальше код касаемо комментариев
    comment_list = Comment.objects.filter(post=post).order_by('-created').all()
    comment_form = CommentForm()
    return render(request, 'profile.html', {'post': post, 'user_profile': user_profile,
                                            'comment_form': comment_form, 'comments': comment_list})


@login_required
def post_edit(request, username, post_id):
    """ Обрабатывает страницу редактирования записи """
    user_profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=user_profile)
    if request.user != post.author:
        return redirect(f'/{username}/{post_id}/')
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(f'/{username}/{post_id}/')
    return render(request, 'new_post.html', {'form': form, 'post': post})


@login_required
def add_comment(request, username, post_id):
    """ Обрабатывает POST-запрос и добавляет комментарий к записи """
    user_profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=user_profile)
    comment = Comment(post=post, author=request.user)
    form = CommentForm(request.POST, instance=comment)
    if form.is_valid():
        form.save()
    return redirect(post_view, username=username, post_id=post_id)


@login_required
def follow_index(request):
    """ Выводит список записей авторов, которые есть в подписке """
    post_list = Post.objects.filter(author__following__user=request.user).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    """ Обрабатывает POST-запрос кнопки "Подписаться", добавляет автора в подписку """
    if request.user.username != username:
        author = get_object_or_404(User, username=username)
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    """ Обрабатывает POST-запрос кнопки "Отписаться", удаляет автора из подписки """
    author = get_object_or_404(User, username=username)
    author.following.filter(user=request.user).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
