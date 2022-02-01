from datetime import timedelta
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils import timezone
from .forms import PostForm, CommentForm
from .models import Post


@login_required
def index(request):
    timesince = timezone.now() - timedelta(days=3)  # 최근 시간에서 3일을 뺀
    post_list = Post.objects.all()\
        .filter(
            Q(author=request.user) |
            Q(author__in=request.user.following_set.all())
        )\
        .filter(
            created_at__gte=timesince
        )
    # 작성자가 자기자신의 post list 또는
    # 유저`가 팔로우한 유저`의 Post List

    suggested_user_list = get_user_model().objects.all()\
        .exclude(pk=request.user.pk)\
        .exclude(pk__in=request.user.following_set.all())[:3]
        # 전체 유저중 login 한 유저는 제외하고
        # 유저`가 팔로우한 유저`는 제외한다.
    request.user.following_set.all()
    
    return render(
        request, 'instagram/index.html', 
        {"post_list": post_list,
         "suggested_user_list": suggested_user_list,}
    )


@login_required
def post_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            post.tag_set.add(*post.extract_tag_list())
            messages.success(request, "포스팅을 저장했습니다.")
            return redirect('/')  # TODO: get_absolute_url 활용
    else:
        form = PostForm()
        
    return render(
        request, 'instagram/post_form.html', 
        { "form": form, }
    )
    

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(
        request, "instagram/post_detail.html", 
        { 'post': post, }
    )
    

@login_required
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.like_user_set.add(request.user)
    messages.success(request, "포스팅#{}를 좋아합니다.".format(post.pk))
    redirect_url = request.META.get("HTTP_REFERER", "root")  # HTTP_REFERER: 요청온 주소 알아내기. 없으면 'root' 로 
    return redirect(redirect_url)
    

@login_required
def post_unlike(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.like_user_set.remove(request.user)
    messages.success(request, "포스팅#{} 좋아요를 취소합니다.".format(post.pk))
    redirect_url = request.META.get("HTTP_REFERER", "root")  # HTTP_REFERER: 요청온 주소 알아내기. 없으면 'root' 로 
    return redirect(redirect_url)


@login_required
def comment_new(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect(comment.post)
    else:
        form = CommentForm()

    return render(
        request, "instagram/comment_form.html", 
        {
            'form': form,
        }
    )
    


def user_page(request, username):
    page_user = get_object_or_404(
        get_user_model(), username=username, is_active=True
    )
    post_list = Post.objects.filter(author=page_user)
    post_list_count = post_list.count() # 실제 데이터베이스에 count 퀴리를 던지게 됨.
 
    if request.user.is_authenticated:
        # 로그인이 되어있을때
        is_follow = request.user.following_set.filter(pk=page_user.pk).exists()
        # 현재 유저의 following_set 중에 `조회한(페이지) 유저의 PK`가 존재하는 지 확인
    else:
        # 로그인이 안 되어있을때
        is_follow = False

    return render(
        request, 'instagram/user_page.html',
        {'page_user': page_user, 
         'post_list': post_list,
         'post_list_count': post_list_count,
         'is_follow': is_follow,}
    )