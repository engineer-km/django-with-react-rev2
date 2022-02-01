from django import template


# 커스텀 템플릿 만들기
register = template.Library()


@register.filter
def is_like_user(post, user):
    return post.is_like_user(user)