from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from posts.forms import PostForm
from posts.models import Group, Post

from posts.services import get_paginator_and_amount_all_posts

User = get_user_model()


def index(request: HttpRequest) -> HttpResponse:
    """Возвращает главную страницу сайта."""
    post_list = Post.objects.select_related('author', 'group')
    page_obj = get_paginator_and_amount_all_posts(request, post_list)[0]
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """Возвращает страницу с постами для выбранной группы."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author')
    page_obj = get_paginator_and_amount_all_posts(request, post_list)[0]
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """Возвращает страницу автора с его постами."""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group')
    page_obj, amount_posts = get_paginator_and_amount_all_posts(request,
                                                                post_list)
    context = {
        'author': author,
        'amount_posts': amount_posts,
        'page_obj': page_obj
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """Возвращает подробную информация о посте."""
    post = get_object_or_404(Post, id=post_id)
    amount_posts_author = Post.objects.filter(author=post.author).count()
    context = {
        'post': post,
        'amount_posts': amount_posts_author
    }
    return render(request, 'posts/post_detail.html', context)


@login_required(redirect_field_name='users:login')
def post_create(request: HttpRequest) -> HttpResponse:
    """Возвращает страницу c формой создания поста."""
    if not request.method == 'POST':
        form = PostForm()
        return render(request, 'posts/create_post.html',
                      context={'form': form})
    form = PostForm(request.POST)
    if not form.is_valid():
        return render(request, 'posts/create_post.html',
                      context={'form': form})
    new_post = form.save(commit=False)
    new_post.author_id = request.user.id
    new_post.save()
    return redirect('posts:profile', username=request.user.username)


@login_required(redirect_field_name='users:login')
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    """Возвращает страницу c формой редактирования поста."""
    post = get_object_or_404(Post, id=post_id)
    if not request.user.id == post.author_id:
        return redirect('posts:post_detail', post_id=post_id)
    if not request.method == 'POST':
        form = PostForm(instance=post)
        return render(request, 'posts/create_post.html',
                      context={'form': form, 'is_edit': True})
    form = PostForm(request.POST, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/create_post.html',
                  context={'form': form, 'is_edit': True})
