from django import forms
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post

User = get_user_model()

FIRST_PAGE_RECORDS = 10
SECOND_PAGE_RECORDS = 4


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
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description'
        )
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group,
            author=cls.author,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            text='test_comment'

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
        cls.templates_for_pages_show = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    args=[cls.group.slug]
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    args=[cls.author.username]
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': cls.post.pk}
                    ): 'posts/post_detail.html'
        }
        cls.templates_for_form = {
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': cls.post.pk}
                    ): 'posts/create_post.html',
        }
        cls.templates_for_paginator = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    args=[cls.group.slug]
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    args=[cls.author.username]
                    ): 'posts/profile.html',
        }
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        posts = [Post(
            group=cls.group,
            text='test_post',
            author=cls.author)
            for i in range(13)
        ]
        Post.objects.bulk_create(posts)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for (
            reverse_name,
            template
        ) in PostPagesTest.templates_pages_names.items():
            with self.subTest(template=template):
                response = PostPagesTest.authorized_author_client.get(
                    reverse_name
                )
                self.assertTemplateUsed(response, template)

    def test_create_and_edit_post_show_correct_context(self):
        """Шаблон create_post и post_edit передает форму создания поста."""
        for (
            reverse_name,
            template
        ) in PostPagesTest.templates_for_form.items():
            with self.subTest(template=template):
                response = PostPagesTest.authorized_author_client.get(
                    reverse_name
                )
        for value, expected in PostPagesTest.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_pages_show_correct_link(self):
        """
        Страницы отражают корректные ссылки
        """
        for (
            reverse_name,
            template
        ) in PostPagesTest.templates_for_pages_show.items():
            with self.subTest(template=template):
                response = PostPagesTest.guest_client.get(
                    reverse_name
                )
        post = PostPagesTest.post
        response_post = response.context.get('post')
        post_author = response_post.author
        post_group = response_post.group
        post_text = response_post.text
        post_image = response_post.image
        self.assertEqual(post_author, PostPagesTest.author)
        self.assertEqual(post_group, PostPagesTest.group)
        self.assertEqual(post_text, post.text)
        self.assertEqual(post_image, post.image)

    def test_group_list_show_group_posts(self):
        """
        На страницу group_list передаётся список постов,
        отфильтрованных по группе.
        """
        response = PostPagesTest.authorized_author_client.get(
            reverse('posts:group_list', args=[PostPagesTest.group.slug])
        )
        response_group = response.context.get('group')
        self.assertEqual(response_group, PostPagesTest.group)

    def test_profile_show_correct_profile(self):
        """
        На страницу profile передаётся список постов,
        отфильтрованных по пользователю.
        """
        response = PostPagesTest.guest_client.get(
            reverse('posts:profile', args=[PostPagesTest.author.username])
        )
        author = PostPagesTest.author
        response_author = response.context.get('author')
        self.assertEqual(author, response_author)

    def test_post_detail_show_correct_post_detail(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = PostPagesTest.guest_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': PostPagesTest.post.pk}
                    )
        )
        post = PostPagesTest.post
        response_post = response.context.get('post')
        self.assertEqual(post, response_post)

    def test_paginator(self):
        pages = (
            (1, FIRST_PAGE_RECORDS),
            (2, SECOND_PAGE_RECORDS),
        )
        for page, count in pages:
            for (
                reverse_name,
                template
            ) in PostPagesTest.templates_for_paginator.items():
                with self.subTest(template=template):
                    response = PostPagesTest.guest_client.get(
                        reverse_name, {'page': page}
                    )
        self.assertEqual(len(response.context['page_obj'].object_list), count)

    def test_auth_comments(self):
        """ Только авторизованный пользователь может комментировать посты."""

        comment = Comment.objects.create(author=self.author, post_id=self.post.pk)
        response = PostPagesTest.comment
        self.assertEqual(response, comment)

        # self.client.logout()
        # response = self.response_post(
        #     name='add_comment',
        #     rev_args={
        #         'username': self.user.username,
        #         'post_id': post.id
        #     },
        #     post_args={'text': comment}
        # )
        # reverse_string = reverse(
        #     'add_comment',
        #     kwargs={
        #         'post_id': post.id,
        #         'username': self.user.username
        #     }
        # )
        # redirect_string = f"{settings.LOGIN_URL}?next={reverse_string}"
        # self.assertRedirects(
        #     response,
        #     redirect_string
        # )
