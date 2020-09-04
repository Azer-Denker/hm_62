"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from webapp.views import *
# from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', ProjectsView.as_view(), name='index_project'),
    path('project/<int:pk>/update', ProjectUpdateView.as_view(), name='project_update'),
    path('project/<int:pk>/', ProjectView.as_view(), name='project_view'),
    path('project/add/', ProjectCreateView.as_view(), name='project_create_view'),
    path('project/<int:pk>/delete/', ProjectDeleteView.as_view(), name='project_delete'),

    path('issues/', IssuesView.as_view(), name='index_issue'),
    path('project/<int:pk>/issue/add/', IssueCreateView.as_view(), name='issue_add_view'),
    path('project/<int:pk>/issue/', IssueView.as_view(), name='issue_view'),
    path('project/<int:pk>/issue/delete/', IssueDeleteView.as_view(), name='issue_delete_view'),
    path('project/<int:pk>/issue/update/', IssueUpdateView.as_view(), name='issue_update_view'),

    path('multi_delete/', multi_delete, name='multi_delete'),
    path('multi_delete_issue/', multi_delete_issue, name='multi_delete_issue'),

    path('accounts/', include('accounts.urls'))
]
