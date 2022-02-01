from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import PostForm
from .models import Post


@login_required
def index(request):
    suggested_user_list = get_user_model().objects.all()\
        .exclude(pk=request.user.pk)\
        .exclude(pk__in=request.user.following_set.all())[:3]
        # 전체 유저중 login 한 유저는 제외하고
        # 유저`가 팔로우한 유저`는 제외한다.
    request.user.following_set.all()
    
    return render(
        request, 'instagram/index.html', 
        {"suggested_user_list": suggested_user_list,}
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
    

def user_page(request, username):
    page_user = get_object_or_404(
        get_user_model(), username=username, is_active=True
    )
    post_list = Post.objects.filter(author=page_user)
    post_list_count = post_list.count() # 실제 데이터베이스에 count 퀴리를 던지게 됨.
    return render(
        request, 'instagram/user_page.html',
        {'page_user': page_user, 
         'post_list': post_list,
         'post_list_count': post_list_count,}
    )