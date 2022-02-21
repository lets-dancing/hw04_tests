from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.guest_client = Client()
        cls.author = User.objects.create_user(
            username='test_author'
        )
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(
            cls.author
        )
        cls.not_author = User.objects.create_user(
            username='test_not_author'
        )
        cls.authorized_client_not_author = Client()
        cls.authorized_client_not_author.force_login(
            cls.not_author
        )
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='test_description'
        )
        cls.post = Post.objects.create(
            text='test_text',
            author=cls.author,
            group=cls.group
        )
        cls.templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.author.username}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{cls.post.pk}/edit/': 'posts/create_post.html'
        }
        return super().setUpClass()

    def test_index(self):
        """Главная страница доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_profile(self):
        """Профильная страница доступна любому пользователю."""
        response = self.guest_client.get('/profile/'
                                         f'{PostURLTests.author.username}/')
        self.assertEqual(response.status_code, 200)

    def test_post_detail(self):
        """Подробная информация о посте доступна любому пользователю."""
        response = self.guest_client.get(f'/posts/{PostURLTests.post.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_profile_post_edit_not_auth(self):
        """Прямая ссылка /posts/<post_id>/edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = PostURLTests.guest_client.get(
            (f'/posts/{PostURLTests.post.pk}/edit/'),
            follow=True
        )
        self.assertRedirects(
            response,
            (f'/auth/login/?next='
             f'/posts/{PostURLTests.post.pk}/edit/')
        )

    def test_profile_post_edit_auth_not_author(self):
        """Кнопка (ссылка) для редактирования поста перенаправит
         авторизированного пользователя(не автора поста) на страницу поста.
        """
        response = PostURLTests.authorized_client_not_author.get(
            (f'/posts/{PostURLTests.post.pk}/edit/'),
            follow=True
        )
        self.assertRedirects(response,
                             (f'/posts/{PostURLTests.post.pk}/'))

    def test_profile_post_edit_auth_author(self):
        """Страница редактирования поста доступна автору поста."""
        response = PostURLTests.authorized_client_author.get(
            (f'/posts/{PostURLTests.post.pk}/edit/')
        )
        self.assertEqual(response.status_code, 200)

    def test_group_list(self):
        """Страница всех записей группы доступна любому пользователю."""
        response = PostURLTests.guest_client.get(
            f'/group/{PostURLTests.group.slug}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        """Страница создания поста доступна авторизованному пользователю."""
        response = PostURLTests.authorized_client_author.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_about_author(self):
        """Страница об авторе доступна любому пользователю."""
        response = PostURLTests.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_about_tech(self):
        """Страница о технологиях доступна любому пользователю."""
        response = PostURLTests.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_404(self):
        """При запросе несуществующей страницы сервер возвращает код 404."""
        response = PostURLTests.guest_client.get('/posts/тест/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in PostURLTests.templates_url_names.items():
            with self.subTest(url=url):
                response = PostURLTests.authorized_client_author.get(url)
                self.assertTemplateUsed(response, template)
