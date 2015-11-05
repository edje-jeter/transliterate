from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout, Div
from crispy_forms.bootstrap import FormActions
from main.models import DictCMU


class EnglishInputForm(forms.Form):
    english_input_f = forms.CharField(required=True,
                                      label="",
                                      widget=forms.Textarea(attrs={'placeholder': 'Input English Text'}),
                                      )

    def __init__(self, *args, **kwargs):
        super(EnglishInputForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = '/input_output/'
        self.helper.layout = Layout(
                    'english_input_f',
                    )
        self.helper.layout.append(
            FormActions(
                Submit('submit', 'Submit', css_class="btn-primary")
                )
            )
