from django import forms
from django.utils import timezone
import datetime


class DateSearchForm(forms.Form):
    start = forms.SplitDateTimeField(widget=forms.SplitDateTimeWidget(attrs={'id': "dateTimeIds"}),
                                     initial=timezone.now() + datetime.timedelta(days=1, minutes=30),
                                     label="Start", input_time_formats=['%H:%M', '%I:%M%p', '%I:%M %p', '%H:%M:%S'])

    end = forms.SplitDateTimeField(widget=forms.SplitDateTimeWidget(attrs={'id': "dateTimeIde"}),
                                   initial=timezone.now() + datetime.timedelta(days=1, minutes=30),
                                   label="End", input_time_formats=['%H:%M', '%I:%M%p', '%I:%M %p', '%H:%M:%S'])
    keywords = forms.CharField(
        widget=forms.TextInput(attrs={'class': "toolbar_searchbar", 'placeholder': "Keywords..."}), required=False)