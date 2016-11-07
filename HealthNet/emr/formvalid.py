from django.utils import timezone
import datetime


def dict_has_keys(keys, dict):
    for key in keys:
        if not(key in dict):
            return False
    return True


def add_messages(form, error, help):
    for key in error:
        form.add_error(key, error[key])

    for key in help:
        form.fields[key].help_text = help[key]


def birthdayInPast(form, error, help):
    if not dict_has_keys(['birthday'], form.cleaned_data):
        return True
    if form.cleaned_data['birthday'] > timezone.now():
        return False
    return True

def ageIsLessThan(form, age, error, help):
    if not dict_has_keys(['birthday'], form.cleaned_data):
        return True
    if (timezone.now() - form.cleaned_data['birthday']) >= datetime.timedelta(years=age):
        return False
    return True

def prescriptionTimeIsPositive(form, delta, error, help):
    if not dict_has_keys(['startTime', 'endTime'], form.cleaned_data):
        return True
    if (form.cleaned_data['endTime'] - form.cleaned_data['startTime']) < delta:
        return False
    return True