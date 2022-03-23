from typing import Tuple

from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.http import HttpRequest

from yatube.settings import POSTS_ON_PAGE


def get_paginator_and_amount_all_posts(request: HttpRequest,
                                       post_list: QuerySet
                                       ) -> Tuple[Paginator, int]:
    """Возвращает объект Paginator и общее количество постов."""
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number), paginator.count