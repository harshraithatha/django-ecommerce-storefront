from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # Honeypot: real visitors leave this empty; bots tend to fill every field.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in ('name', 'email', 'subject'):
            self.fields[field_name].widget.attrs['class'] = 'input'

        self.fields['message'].widget.attrs['class'] = 'textarea'
        self.fields['message'].widget.attrs['rows'] = 5

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Spam detected.')
        return self.cleaned_data['website']
