from django import forms
from django.forms import ModelForm

from .models import Ratings, BOOL_CHOICES

class RatingsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(RatingsForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Ratings
        fields = ('a_gt_b', 'audio_a', 'audio_b')
        widgets = {
            'a_gt_b': forms.RadioSelect(choices=BOOL_CHOICES),
            'audio_a': forms.HiddenInput(),
            'audio_b': forms.HiddenInput(),
        }
