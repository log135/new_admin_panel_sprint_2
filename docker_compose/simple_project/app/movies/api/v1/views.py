from enum import Enum

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.models import FilmWork


class Roles(Enum):
    ACTOR = 'actor'
    DIRECTOR = 'director'
    WRITER = 'writer'


class FilmWorkApiMixin:
    model = FilmWork
    http_method_names = ['get']

    def get_queryset(self):
        annotations = {}

        for role in Roles:
            annotations[f'{role.value}s'] = ArrayAgg('persons__full_name', filter=Q(personfilmwork__role=role.value), distinct=True)

        annotations['genres'] = ArrayAgg('genres__name', distinct=True)

        return (self.model.objects.all()
                .prefetch_related('genres', 'persons')
                .values('id', 'title', 'description', 'creation_date', 'rating', 'type')
                .annotate(**annotations))

    def render_to_response(self, context: dict, **response_kwargs):
        return JsonResponse(context)


class FilmWorkListApi(FilmWorkApiMixin, BaseListView):
    def get_context_data(self, *, object_list=None, **kwargs):
        results_qs = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(results_qs, 50)
        context = {
            'count': paginator.count,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'total_pages': paginator.num_pages,
            'results': list(queryset),
        }
        return context


class FilmWorkDetailApi(FilmWorkApiMixin, BaseDetailView):
    def get_context_data(self, *, object_list=None, **kwargs):
        return self.get_queryset().get(id=self.kwargs.get('pk'))
