import datetime
from django.utils import timezone

def dict_has_keys(keys, dict):
    for key in keys:
        if not(key in dict):
            return False
    return True

class EventCreationFormValidator:

    @staticmethod
    def add_messages(form, error, help):
        for key in error:
            form.add_error(key, error[key])

        for key in help:
            form.fields[key].help_text = help[key]

    @staticmethod
    def startDateInXhoursFuture(form, x, error, help):
        if not dict_has_keys(['startTime'], form.cleaned_data):
            return True
        if (form.cleaned_data['startTime'] - timezone.now()) < datetime.timedelta(hours=x):
            EventCreationFormValidator.add_messages(form, error, help)
            return False
        return True

    @staticmethod
    def eventIsAppointment(form, error, help):
        if not dict_has_keys(['patient'], form.cleaned_data):
            return True

        if form.cleaned_data['patient'] is None:
            EventCreationFormValidator.add_messages(form, error, help)
            return False
        return True

    @staticmethod
    def eventPositiveDuration(form, min, error, help):
        if not dict_has_keys(['duration'], form.cleaned_data):
            return True

        if(form.cleaned_data['duration'] < min):
            EventCreationFormValidator.add_messages(form, error, help)
            return False
        return True

    @staticmethod
    def eventDurationBounded(form, low, high, error, help):
        if not dict_has_keys(['duration'], form.cleaned_data):
            return True
        if not(datetime.timedelta(minutes=15) <= form.cleaned_data['duration'] <= datetime.timedelta(minutes=30)):
            EventCreationFormValidator.add_messages(form, error, help)
            return False
        return True

    @staticmethod
    def patientMatchesHospitalDoctor(form, error, help):
        if not dict_has_keys(['patient', 'hospital'], form.cleaned_data):
            return True

        p = form.cleaned_data['patient']
        h = form.cleaned_data['hospital']

        if p != None and h != None:
            if (p.hospital != h) or not(h in p.doctor.hospitals.all()):
                EventCreationFormValidator.add_messages(form, error, help)
                return False
        return True


    @staticmethod
    def eventValidateRequestTimeingOffset(form, min, sec, error, help):
        if not dict_has_keys(['startTime'], form.cleaned_data):
            return True
        if (timezone.now() - form.cleaned_data['startTime']) > datetime.timedelta(minutes=min, seconds=sec):
            EventCreationFormValidator.add_messages(form, error, help)
            return False
        return True
