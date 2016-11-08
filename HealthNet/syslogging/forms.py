from django import forms
from .models import *
from django.contrib.admin import widgets
from django.utils import timezone
import datetime


class DateSearchForm(forms.Form):
    startTime = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime(attrs={'id': "dateTimeId"}),
                                         label="Start Time (m/d/y)")
    endTime = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime(attrs={'id': "dateTimeId"}),
                                         label="End Time (m/d/y)")
    def is_valid(self):
        valid = super(DateSearchForm, self).is_valid()
        if not valid:
            return valid

        # todo add date validity checks

        return valid