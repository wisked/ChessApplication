from .models import *
from django.forms import ModelForm, models

from django import forms


class PushPlayers(ModelForm):
    class Meta:
        model = RegisterPlayer
        fields = ['name', 'ello_rate']


class PushResults(forms.Form):
    MATCH_RESULT = (
        (1, 'Победа'),
        (0.5, 'Ничья'),
        (0, 'Проигрыш'),
    )
    first_result = forms.ChoiceField(choices=MATCH_RESULT)
    second_result = forms.ChoiceField(choices=MATCH_RESULT)


# class PushResults(ModelForm):
#     class Meta:
#         models = RegisterPlayer
#         fields = ['result']

