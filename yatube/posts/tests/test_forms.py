from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from posts.forms import PostForm

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='testauthor')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.group_old = Group.objects.create(
            title='test_group_old',
            slug='test-slug-old',
            description='test_description'
        )
        cls.group_new = Group.objects.create(
            title='test_group_new',
            slug='test-slug-new',
            description='test_description'
        )
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group_old,
            author=cls.author
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_create_post(self):
        """Проверка формы создания нового поста."""
        posts_count = Post.objects.count()
        group_field = PostFormTests.group_old.id
        form_data = {
            'text': 'test_new_post',
            'group': group_field
        }
        response = PostFormTests.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             args=[PostFormTests.author.username]))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=PostFormTests.group_old.id,
                text='test_new_post'
            ).exists()
        )

    def test_edit_post(self):
        """Проверка формы редактирования поста и изменение
        его в базе данных."""
        group_field_new = PostFormTests.group_new.id
        form_data = {
            'text': 'test_edit_post',
            'group': group_field_new
        }
        response = PostFormTests.author_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostFormTests.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': PostFormTests.post.pk}
                    )
        )
        self.assertTrue(
            Post.objects.filter(
                group=PostFormTests.group_new.id,
                text='test_edit_post'
            ).exists()
        )
        self.assertFalse(
            Post.objects.filter(
                group=PostFormTests.group_old.id,
                text='test_post'
            ).exists()
        )
