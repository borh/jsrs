from django import forms
from django.forms import ModelForm

from .models import Ratings, BOOL_CHOICES

class RatingsForm(ModelForm):
    class Meta:
        model = Ratings
        fields = ('a_gt_b',)
        widgets = {
            'a_gt_b': forms.RadioSelect(choices=BOOL_CHOICES),
        }

# class RatingForm(forms.Form):
#     a_or_b = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
