from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    """Form for booking a campervan."""
    class Meta:
        model = Booking
        fields = ['start_date', 'end_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_date'].widget.attrs.update({'class': 'datepicker'})
        self.fields['end_date'].widget.attrs.update({'class': 'datepicker'})