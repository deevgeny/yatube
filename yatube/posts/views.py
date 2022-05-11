from core.paginator import get_page_object
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post


@cache_page(settings.CACHE_TIMEOUT, key_prefix='index_page')
def index(request):
    """Home page."""
    # Get data from database
    posts = Post.objects.select_related('group', 'author').all()
    switcher_index_link_activated = True

    # Get paginator page object and create context
    page_obj = get_page_object(request, posts, settings.PAGINATOR_LIMIT)
    context = {'page_obj': page_obj, 'index': switcher_index_link_activated}

    # Render page with context
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Group posts page."""
    # Get data from database
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author').all()

    # Get paginator page object
    page_obj = get_page_object(request, posts, settings.PAGINATOR_LIMIT)

    # Render page with context
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """User profile page."""
    # Get data from database
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    posts_count = len(posts)
    following = None
    if request.user.is_authenticated:
        following = request.user.follower.filter(author=author).exists()

    # Get paginator page object
    page_obj = get_page_object(request, posts, settings.PAGINATOR_LIMIT)

    # Render page with context
    context = {
        'author': author,
        'posts_count': posts_count,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Post detail page."""
    # Get data from database
    post = get_object_or_404(Post, pk=post_id)
    posts_count = post.author.posts.count()
    comments = post.comments.all()

    # Render page with context
    context = {
        'post': post,
        'posts_count': posts_count,
        'form': CommentForm(),
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Post create page."""
    # View constants
    redirect_target = 'posts:profile'
    template = 'posts/create_post.html'

    # Create form
    form = PostForm(request.POST or None, files=request.FILES or None)

    # GET request
    if request.method != 'POST':
        return render(request, template, {'form': form})

    # POST request: invalid form data - return form with errors
    if not form.is_valid():
        return render(request, template, {'form': form})

    # POST request: valid form data - create post
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect(redirect_target, request.user.username)


@login_required
def post_edit(request, post_id):
    """Post edit page."""
    # View constants
    redirect_target = 'posts:post_detail'
    template = 'posts/create_post.html'

    # Get post object from database
    post = get_object_or_404(Post, pk=post_id)

    # Check user
    if request.user != post.author:
        return redirect(redirect_target, post.id)

    # GET request
    if request.method != 'POST':
        context = {'form': PostForm(instance=post), 'is_edit': True}
        return render(request, template, context=context)

    # POST request
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect(redirect_target, post.id)


@login_required
def add_comment(request, post_id):
    """Add comment page."""
    # View constants
    redirect_target = 'posts:post_detail'

    # Get post object from database
    post = get_object_or_404(Post, pk=post_id)

    # Post request
    form = CommentForm(request.POST or None)
    if form.is_valid:
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect(redirect_target, post_id)


@login_required
def follow_index(request):
    """Follow index page."""
    # View constants
    template = 'posts/follow.html'
    switcher_follow_link_activated = True

    # Get all following posts from database
    authors = User.objects.filter(following__user=request.user)
    posts = Post.objects.filter(author__in=authors)

    # Get paginator page object and prepare context
    page_obj = get_page_object(request, posts, settings.PAGINATOR_LIMIT)
    context = {'page_obj': page_obj, 'follow': switcher_follow_link_activated}

    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Follow author page."""
    # View constants
    redirect_target = reverse('posts:profile', kwargs={'username': username})

    # Get author from database
    author = get_object_or_404(User, username=username)

    # Check constraints
    # User can't follow himself
    if request.user == author:
        return redirect(redirect_target)
    # User can't follow author more than one time
    if Follow.objects.filter(user=request.user, author=author).exists():
        return redirect(redirect_target)

    # Create follow object in db
    Follow.objects.create(
        user=request.user,
        author=author
    )

    return redirect(redirect_target)


@login_required
def profile_unfollow(request, username):
    """Unfollow author page."""
    # View constants
    redirect_target = reverse('posts:profile', kwargs={'username': username})

    # Get data from database
    author = get_object_or_404(User, username=username)

    # Delete follow object in db
    Follow.objects.filter(user=request.user, author=author).delete()

    return redirect(redirect_target)
