from django.test import TestCase, Client
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

from .models import Post, Group, User


class TestHW04(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="sarah", email="connor.s@skynet.com", password="12345"
        )

    def test_profile(self):
        """ После регистрации пользователя создается его персональная страница (profile) """
        response = self.client.get(f"/{self.user.username}/")
        self.assertEqual(response.status_code, 200)

    def test_new_post_auth(self):
        """ Авторизованный пользователь может опубликовать пост (new) """
        self.client.force_login(self.user)
        response = self.client.get("/new/")
        self.assertEqual(response.status_code, 200)
        self.client.post("/new/", {"text": "text1"})
        self.assertTrue(Post.objects.filter(text="text1").exists())

    def test_new_post_no_auth(self):
        """ Неавторизованный посетитель не может опубликовать пост
         (его редиректит на страницу входа) """
        self.client.logout()
        response = self.client.get("/new/", follow=True)
        self.assertEqual(response.redirect_chain, [("/auth/login/?next=/new/", 302)])
        response = self.client.post("/new/", {"text": "text2"}, follow=True)
        self.assertEqual(response.redirect_chain, [("/auth/login/?next=/new/", 302)])
        self.assertFalse(Post.objects.filter(text="text2").exists())

    def test_new_post_display(self):
        """ После публикации поста новая запись появляется на главной странице сайта (index),
        на персональной странице пользователя (profile), и на отдельной странице поста (post) """
        post = Post.objects.create(
            text="You are talking about things I have not done yet in the past tense.",
            author=self.user,
        )
        url_list = [
            "/",
            f"/{post.author.username}/",
            f"/{post.author.username}/{post.id}/",
        ]
        for url in url_list:
            response = self.client.get(url)
            self.assertContains(response, post.text)

    def test_post_edit(self):
        """ Авторизованный пользователь может отредактировать свой пост,
        и его содержимое изменится на всех связанных страницах """
        self.client.force_login(self.user)
        post = Post.objects.create(text="It's driving me crazy!", author=self.user)
        self.client.post(
            f"/{self.user.username}/{post.id}/edit/", {"text": "text3"}, follow=True
        )
        url_list = [
            "",
            f"/{post.author.username}/",
            f"/{post.author.username}/{post.id}/",
        ]
        cache.clear()
        for url in url_list:
            response = self.client.get(url)
            self.assertContains(response, "text3")
            self.assertNotContains(response, post.text)


class TestSprint6(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="sarah", email="connor.s@skynet.com", password="12345"
        )
        self.group = Group.objects.create(
            title="sarah's posts", slug="sarah", description="Posts of Sarah"
        )
        self.post = Post.objects.create(
            text="It is driving me crazy!",
            author=self.user,
            group=self.group,
            image="posts/cent5.jpg",
        )

    def test_404(self):
        """ Проверяем возвращает ли сервер код 404, если страница не найдена """
        response = self.client.get("/404/")
        self.assertEqual(response.status_code, 404)

    def test_post_with_image(self):
        """ Проверяем страницу конкретной записи с картинкой: на странице есть тег <img> """
        url = f"/{self.post.author.username}/{self.post.id}/"
        response = self.client.get(url)
        self.assertContains(response, "<img")

    def test_post_with_image_display(self):
        """ Проверяем, что на главной странице, на странице профайла и на странице группы пост с
         картинкой отображается корректно, с тегом <img> """
        url_list = ["", f"/{self.post.author.username}/", f"/group/{self.group.slug}/"]
        cache.clear()
        for url in url_list:
            response = self.client.get(url)
            self.assertContains(response, "<img")

    def test_wrong_image(self):
        """ Проверяем, что срабатывает защита от загрузки файлов не-графических форматов """
        self.client.force_login(self.user)
        count_posts = Post.objects.count()
        with open("yatube/settings.py", "rb") as img:
            response = self.client.post(
                "/new/", {"text": "post with image", "image": img}
            )
        # Проверяем, что форма выдаст ошибку
        error_message = (
            response.context["form"].fields["image"].error_messages["invalid_image"]
        )
        self.assertFormError(response, "form", "image", error_message)
        # Проверяем, что в базе пост не создался
        self.assertEqual(Post.objects.count(), count_posts)

    def test_cache(self):
        """ Проверяем, работу кэша """
        response = self.client.get("")
        key = make_template_fragment_key("index_page", ["<Page 1 of 1>"])
        html_cache = cache.get(key)
        self.assertIn(html_cache, str(response.content.decode()))

    def test_follow(self):
        """ Проверяем, что авторизованный пользователь может подписываться на других пользователей
         и удалять их из подписок """
        user = User.objects.create_user(
            username="terminator", email="terminator@skynet.com", password="12345"
        )
        self.client.force_login(user)

        self.client.get(f"/{self.user.username}/follow/")
        self.assertTrue(user.follower.filter(author=self.user).exists())

        self.client.get(f"/{user.username}/unfollow/", {"username": user.username})
        self.assertFalse(self.user.follower.filter(author=user).exists())

    def test_follow_index(self):
        """ Проверяем, что новая запись пользователя появляется в ленте тех,
         кто на него подписан и не появляется в ленте тех, кто не подписан на него """
        user = User.objects.create_user(
            username="terminator", email="terminator@skynet.com", password="12345"
        )
        self.client.force_login(user)
        self.client.get(f"/{self.user.username}/follow/")
        response = self.client.get("/follow/")
        self.assertContains(response, self.post.text)
        self.client.get(f"/{self.user.username}/unfollow/")
        response = self.client.get("/follow/")
        self.assertNotContains(response, self.post.text)

    def test_comment(self):
        """ Проверяем, что только авторизированный пользователь может комментировать посты """
        # Проверяем, что незарегистрированный пользоыватель не может комментировать посты
        self.client.post(
            f"/{self.user.username}/{self.post.id}/comment/", {"text": "test_comment"}
        )
        self.assertFalse(self.post.comment_post.filter(text="test_comment").exists())
        user = User.objects.create_user(
            username="terminator", email="terminator@skynet.com", password="12345"
        )
        # Проверяем, что авторизованный пользователь может комментировать
        self.client.force_login(user)
        self.client.post(
            f"/{self.user.username}/{self.post.id}/comment/", {"text": "test_comment"}
        )
        self.assertTrue(self.post.comment_post.filter(text="test_comment").exists())
