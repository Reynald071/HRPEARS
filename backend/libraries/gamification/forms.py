from django import forms

from backend.libraries.gamification.models import GamifyLevels, GamifyActivities


class GamifyLevelsForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'autocomplete': 'off'}))
    value = forms.IntegerField()
    file = forms.FileField(label="Badge")
    status = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = GamifyLevels
        exclude = ('upload_by',)


class GamifyActivitiesForm(forms.ModelForm):
    activity = forms.CharField(
        widget=forms.TextInput(
            attrs={'autocomplete': 'off'}))
    points = forms.IntegerField()
    limit_per_day = forms.IntegerField(label="Max times per day")
    status = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = GamifyActivities
        exclude = ('upload_by',)
