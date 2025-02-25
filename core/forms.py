from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Your Name")
    email = forms.EmailField(required=True, label="Your Email")
    subject = forms.CharField(max_length=150, required=True, label="Subject")
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"rows": 5}),
        label="Message",
    )
