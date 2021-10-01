from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from .models import Post, Comment, Profile
from .forms import EmailPostForm, CommentForm, CustomUserCreationForm, ProfileForm, UserForm, PostForm
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from blog.decorators import *


def post_list(request):
    posts = Post.published.all()
    return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request, year, month, day, post):

    post = get_object_or_404(Post, slug=post, status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    return render(request, 'blog/post/detail.html', {'post': post})


def post_list(request):

    object_list = Post.published.all()

    paginator = Paginator(object_list, 3)

    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


def post_detail(request, year, month, day, post):

    post = get_object_or_404(Post, slug=post, status='published',
                             publish__year=year, publish__month=month, publish__day=day)

    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()
        comment_form = CommentForm()
    else:
        comment_form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form})


def registerPage(request):
    if request.user.is_authenticated:
        return redirect('blog:post_list')

    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            messages.success(request, 'Account successfuly created!')

            user = authenticate(request, username=user.username,
                                password=request.POST['password1'])

            if user is not None:
                login(request, user)

            next_url = request.GET.get('next')
            if next_url == '' or next_url == None:
                next_url = 'blog:post_list'
            return redirect(next_url)
        else:
            messages.error(request, 'An error has occured with registration')
    context = {'form': form}
    return render(request, 'blog/register.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('blog:post_list')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Little Hack to work around re-building the usermodel
        try:
            user = User.objects.get(email=email)
            user = authenticate(
                request, username=user.username, password=password)
        except:
            messages.error(request, 'User with this email does not exists')
            next_url = 'blog:login'
            return redirect(next_url)

        if user is not None:
            next_url = 'blog:post_list'
            login(request, user)
            return redirect(next_url)
        else:
            messages.error(request, 'Email OR password is incorrect')

    context = {}
    return render(request, 'blog/login.html', context)


def logoutUser(request):
    logout(request)
    next_url = 'blog:post_list'
    return redirect(next_url)


@login_required(login_url="blog:login")
def userAccount(request):
    try:
        profile = request.user.profile
    except:
        new_profile = Profile.objects.create(
            user=request.user,
            username=request.user.username,
            email=request.user.email,
        )
        new_profile.save()
    profile = request.user.profile
    context = {'profile': profile}
    return render(request, 'blog/account.html', context)


@login_required(login_url="blog:login")
def updateProfile(request):
    user = request.user
    profile = user.profile
    form = ProfileForm(instance=profile)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()

        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('blog:profile')

    context = {'form': form}
    return render(request, 'blog/editaccount.html', context)


@admin_only
@login_required(login_url="blog:login")
def edit_post(request, post_id):
    post = Post.objects.get(id=post_id)
    form = PostForm(instance=post)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
        return redirect('blog:post_list')

    context = {'form': form, 'post': post}
    return render(request, 'blog/post/edit_post.html', context)
