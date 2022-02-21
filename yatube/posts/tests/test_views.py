from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostPagesTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create_user(
            username='Bobby'
        )
        cls.authorized_author_client = Client()
        cls.authorized_author_client.force_login(cls.author)
        cls.not_author = User.objects.create_user(
            username='not_Bobby'
        )
        cls.authorized_not_author_client = Client()
        cls.authorized_not_author_client.force_login(cls.not_author)
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description'
        )
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group,
            author=cls.author
        )
        cls.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    args=[cls.group.slug]
                    ): 'posts/group_list.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': cls.post.pk}
                    ): 'posts/create_post.html',
            reverse('posts:profile',
                    args=[cls.author.username]
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': cls.post.pk}
                    ): 'posts/post_detail.html'
        }
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for i in range(13):
            cls.post = Post.objects.create(
                group=cls.group,
                text="Какой-то там текст",
                author=cls.author
            )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        for reverse_name, template\
                in PostPagesTest.templates_pages_names.items():
            with self.subTest(template=template):
                response = PostPagesTest.authorized_author_client.get(
                    reverse_name
                )
                self.assertTemplateUsed(response, template)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post передает форму создания поста."""
        response = PostPagesTest.authorized_author_client.get(
            reverse('posts:post_create')
        )
        for value, expected in PostPagesTest.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_index_show_post_list(self):
        """На страницу index передаётся список постов."""
        response = PostPagesTest.guest_client.get(reverse('posts:index'))
        post = PostPagesTest.post
        response_post = response.context.get('page_obj').object_list[0]
        post_author = response_post.author
        post_group = response_post.group
        post_text = response_post.text
        self.assertEqual(post_author, PostPagesTest.author)
        self.assertEqual(post_group, PostPagesTest.group)
        self.assertEqual(post_text, post.text)

    def test_group_list_show_group_posts(self):
        """
        На страницу group_list передаётся список постов,
         отфильтрованных по группе.
         """
        response = PostPagesTest.authorized_author_client.get(
            reverse('posts:group_list', args=[PostPagesTest.group.slug])
        )
        post = PostPagesTest.post
        response_group = response.context.get('group')
        response_post = response.context.get('page_obj').object_list[0]
        post_author = response_post.author
        post_text = response_post.text
        self.assertEqual(post_author, PostPagesTest.author)
        self.assertEqual(response_group, PostPagesTest.group)
        self.assertEqual(post_text, post.text)

    def test_profile_show_correct_profile(self):
        """
        На страницу profile передаётся список постов,
        отфильтрованных по пользователю.
        """
        response = PostPagesTest.guest_client.get(
            reverse('posts:profile', args=[PostPagesTest.author.username])
        )
        post = PostPagesTest.post
        author = PostPagesTest.author
        response_author = response.context.get('author')
        response_post = response.context.get('page_obj').object_list[0]
        post_author = response_post.author
        post_group = response_post.group
        post_text = response_post.text
        self.assertEqual(post_author, author)
        self.assertEqual(post_group, PostPagesTest.group)
        self.assertEqual(post_text, post.text)
        self.assertEqual(author, response_author)

    def test_post_detail_show_correct_post_detail(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = PostPagesTest.guest_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': PostPagesTest.post.pk}
                    )
        )
        post = PostPagesTest.post
        author = PostPagesTest.author
        response_post = response.context.get('post')
        post_author = response_post.author
        post_group = response_post.group
        post_text = response_post.text
        self.assertEqual(post_author, author)
        self.assertEqual(post_group, PostPagesTest.group)
        self.assertEqual(post_text, post.text)
        self.assertEqual(post, response_post)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = PostPagesTest.authorized_author_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostPagesTest.post.pk}
                    )
        )
        for value, expected in PostPagesTest.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_first_page_containse_ten_records(self):
        """Колличество постов на первой странице равно 10"""

        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page_obj').object_list), 10)

    def test_second_page_containse_three_records(self):
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page_obj').object_list), 5)

    def test_first_page_containse_ten_records(self):
        """Колличество постов на первой странице равно 10"""

        response = self.client.get(reverse(
            'posts:group_list',
            args=[PostPagesTest.group.slug])
        )
        self.assertEqual(len(response.context.get('page_obj').object_list), 10)

    def test_second_page_containse_three_records(self):
        response = self.guest_client.get(
            reverse('posts:group_list', args=[PostPagesTest.group.slug])
            + '?page=2')
        self.assertEqual(len(response.context.get('page_obj').object_list), 4)

    def test_first_page_containse_ten_records(self):
        """Колличество постов на первой странице равно 10"""

        response = self.client.get(reverse(
            'posts:profile', args=[PostPagesTest.author.username])
        )
        self.assertEqual(len(response.context.get('page_obj').object_list), 10)

    def test_second_page_containse_three_records(self):
        response = self.guest_client.get(
            reverse('posts:profile', args=[PostPagesTest.author.username])
            + '?page=2')
        self.assertEqual(len(response.context.get('page_obj').object_list), 4)
