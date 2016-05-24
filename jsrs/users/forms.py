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
        self.helper.form_action = reverse('users:rater_survey').__str__()

        self.helper.add_input(Submit('submit', 'Submit'))

    def get_form(self, request, obj=None, **kwargs):
        form = super(RaterForm, self).get_form(request, obj=obj, **kwargs)
        form.request = request
        return form

    class Meta:
        model = Rater
        fields = [
            'age',
            'gender',
            'volunteer_experience_time',
            'time_abroad',
            'job',
            'place_of_birth',
            'current_address',
            'language_use_information',
            'dialect_used',
            'best_foreign_language',
            'usual_foreign_language_use',
            'speaking_with_foreigners'
        ]

        # widgets = {
        #     'a_gt_b': forms.RadioSelect(choices=BOOL_CHOICES),
        # }
