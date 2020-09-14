from django.urls import path, include
from webapp.views import *

app_name = 'webapp'

urlpatterns = [
    path('', ProjectsView.as_view(), name='index_project'),

    path('project/', include([
        path('<int:pk>/', include([
            path('', ProjectView.as_view(), name='project_view'),
            path('update/', ProjectUpdateView.as_view(), name='project_update'),
            path('delete/', ProjectDeleteView.as_view(), name='project_delete'),
            path('issue/add/', IssueCreateView.as_view(),
                 name='issue_add_view'),
        ])),

        path('add/', ProjectCreateView.as_view(), name='project_create_view'),
        path('mass-project/', ProjectMassActionView.as_view(), name='project_mass_action'),
    ])),

    path('issue/', include([
        path('', IssuesView.as_view(), name='index_issue'),
        path('<int:pk>/', include([
            path('', IssueView.as_view(), name='issue_view'),
            path('update/', IssueUpdateView.as_view(), name='issue_update_view'),
            path('delete/', IssueDeleteView.as_view(), name='issue_delete_view'),
        ]))
    ]))
]
