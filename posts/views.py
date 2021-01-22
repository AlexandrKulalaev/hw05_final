from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.select_related('group').order_by('-pub_date')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group.all()[:12]

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts,
        'page': page,
        'paginator': paginator
    }
    return render(request, 'group.html', context)


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()

            return redirect('index')

        return render(request, 'new.html', {'form': form})

    form = PostForm()
    return render(request, 'new.html', {'form': form})


User = get_user_model()


def profile(request, username):
    author = User.objects.get(username=username)
    post_list = Post.objects.filter(author=author).select_related(
        'author').order_by('-pub_date')
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = author.following.filter(user=request.user).exists()
    followers = Follow.objects.filter(author=author).count()
    follows = Follow.objects.filter(user=author).count()
    is_user = True
    if request.user == author:
        is_user = False
    context = {
        'page': page,
        'author': author,
        'paginator': paginator,
        'following': following,
        'followers': followers,
        'follows': follows,
        'is_user': is_user
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    comments = Comment.objects.filter(post=post_id)
    author = get_object_or_404(User, username=username)
    text = Post._meta.get_field("text")
    post = get_object_or_404(Post, id=post_id, author=author)
    count = Post.objects.filter(author=author).select_related('author').count()
    form = CommentForm(request.POST or None)
    followers = Follow.objects.filter(author=author).count()
    follows = Follow.objects.filter(user=author).count()
    context = {
        'post': post,
        'author': author,
        'count': count,
        'post_id': post_id,
        'text': text,
        'form': form,
        'comments': comments,
        'followers': followers,
        'follows': follows,
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    author = User.objects.get(username=username)
    post = get_object_or_404(Post, author=author, id=post_id)

    if request.user != author:
        return redirect('post', username=username, post_id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None,
                        instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('post', username=username, post_id=post_id)
    form = PostForm(instance=post)
    context = {
        'form': form,
        'post': post,
        'is_edit': True
    }
    return render(request, 'new.html', context)


@login_required
def add_comment(request, username, post_id):
    author = User.objects.get(username=username)
    post = get_object_or_404(Post, author=author, id=post_id)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return redirect('post', username, post_id, )
    comments = form.save(commit=False)
    comments.author = request.user
    comments.post = post
    form.save()
    return redirect('post', username, post_id, )


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator
    }
    return render(request, "follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user and not Follow.objects.filter(
        user=request.user, author=author
    ).exists():
        Follow.objects.create(
            user=request.user, author=author
        )
        return redirect('profile', username=username)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception=None):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request, "misc/404.html", {"path": request.path},
        status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
