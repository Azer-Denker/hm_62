from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, \
    UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View

from webapp.forms import SimpleSearchForm, ProjectForm
from webapp.models import Project


class ProjectMassActionView(PermissionRequiredMixin, View):
    redirect_url = 'webapp:index_project'
    permission_required = 'webapp.delete_article'
    queryset = None  # изначально queryset = None

    def has_permission(self):
        if super().has_permission():
            return True  # админы и модеры могут удалять
        articles = self.get_queryset()
        author_ids = articles.values('author_id')
        for item in author_ids:
            if item['author_id'] != self.request.user.pk:
                return False  # остальные могут удалять, только если среди выбранных статей
        return True           # нет чужих статей

    # метод 'post' проверяет наличие ключа 'delete' в запросе,
    # и тогда удаляет
    def post(self, request, *args, **kwargs):
        if 'delete' in self.request.POST:
            return self.delete(request, *args, **kwargs)
        return redirect(self.redirect_url)

    # метод 'delete' не проверяет наличие ключа 'delete' в запросе,
    # и все равно удаляет
    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.delete()
        return redirect(self.redirect_url)

    # "кэширующий" метод.
    # при первом доступе к свойству queryset находит и сохраняет его в self.queryset
    # при повторном доступе не ищет, возвращает сохранённое значение.
    def get_queryset(self):
        if self.queryset is None:
            ids = self.request.POST.getlist('selected_projects', [])
            self.queryset = self.get_queryset().filter(id__in=ids)
        return self.queryset


class ProjectsView(ListView):
    template_name = 'project/view.html'
    context_object_name = 'projects_list'
    model = Project
    form = SimpleSearchForm
    paginate_by = 3
    paginate_orphans = 1

    def get_queryset(self):
        data = self.model.objects.filter(is_deleted=False)
        form = SimpleSearchForm(data=self.request.GET)
        if form.is_valid():
            search = form.cleaned_data['search']
            if search:
                data = data.filter(Q(name__icontains=search) | Q(description__icontains=search))
        return data.order_by('starts_date')


class ProjectView(DetailView):
    template_name = 'project/index.html'
    model = Project
    paginate_issue_by = 3
    paginate_issue_orphans = 0

    def get_queryset(self):
        data = self.model.objects.filter(is_deleted=False)
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        issues, page, is_paginated = self.paginate_comments(self.object)
        context['issues'] = issues
        context['page_obj'] = page
        context['is_paginated'] = is_paginated
        return context

    def paginate_comments(self, project):
        issues = project.issue.all()
        if issues.count() > 0:
            paginator = Paginator(issues, self.paginate_issue_by, orphans=self.paginate_issue_orphans)
            page = paginator.get_page(self.request.GET.get('page', 1))
            is_paginated = paginator.num_pages > 1
            return page.object_list, page, is_paginated
        else:
            return issues, None, False


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'project/create.html'
    form_class = ProjectForm

    def get_success_url(self):
        return reverse('webapp:project_view', kwargs={'pk': self.object.pk})


class ProjectUpdateView(PermissionRequiredMixin, UpdateView):
    model = Project
    template_name = 'project/update.html'
    form_class = ProjectForm
    permission_required = 'webapp.change_project'

    def get_queryset(self):
        data = self.model.objects.filter(is_deleted=False)
        return data

    def get_success_url(self):
        return reverse('webapp:project_view', kwargs={'pk': self.object.pk})


class ProjectDeleteView(UserPassesTestMixin, DeleteView):
    model = Project
    template_name = 'project/delete.html'
    success_url = reverse_lazy('webapp:index_project')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        project = get_object_or_404(self.model, pk=self.object.pk)
        project.is_deleted = True
        project.save()
        return HttpResponseRedirect(success_url)

    def test_func(self):
        return self.request.user.has_perm('webapp.delete_article') or \
               self.get_object().author == self.request.user
