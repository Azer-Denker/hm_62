from django import forms
from django.forms import widgets
from webapp.models import Issue, Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'starts_date', 'finish_date']
        widgets = {
                    'starts_date': forms.widgets.SelectDateWidget,
                    'finish_date': forms.widgets.SelectDateWidget,
                   }


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['summary', 'description', 'status', 'type']
        widgets = {"type": widgets.CheckboxSelectMultiple}


class SimpleSearchForm(forms.Form):
    search = forms.CharField(max_length=100, required=False, label="Найти")
