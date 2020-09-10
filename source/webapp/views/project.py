from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, \
    UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from webapp.forms import SimpleSearchForm, ProjectForm
from webapp.models import Project


def multi_delete(request):
    data = request.POST.getlist('id')
    projects = Project.objects.filter(pk__in=data)
    for project in projects:
        project.is_deleted = True
        project.save()
    return redirect('projects')


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
        return reverse('project_view', kwargs={'pk': self.object.pk})


class ProjectUpdateView(PermissionRequiredMixin, UpdateView):
    model = Project
    template_name = 'project/update.html'
    form_class = ProjectForm
    permission_required = 'webapp.change_project'

    def get_queryset(self):
        data = self.model.objects.filter(is_deleted=False)
        return data

    def get_success_url(self):
        return reverse('project_view', kwargs={'pk': self.object.pk})


class ProjectDeleteView(UserPassesTestMixin, DeleteView):
    model = Project
    template_name = 'project/delete.html'
    success_url = reverse_lazy('index_project')

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
