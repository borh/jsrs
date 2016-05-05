from django import forms
from django.forms import ModelForm
from django.core.urlresolvers import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Rater

class RaterForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(RaterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-raterForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('users:rater_update').__str__()

        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Rater
        # fields = ('a_gt_b',)
        # widgets = {
        #     'a_gt_b': forms.RadioSelect(choices=BOOL_CHOICES),
        # }
