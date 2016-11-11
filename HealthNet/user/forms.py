from django import forms
from .models import *
import logging

from django import forms
from django.contrib.admin import widgets

from HealthNet.formvalid import *
from emr.models import *
from .models import *

# Get an instance of a logger
logger = logging.getLogger(__name__)

def get_dthtml(dt):
    return'{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}'.format(dt.year, dt.month, dt.day,
                                                               dt.hour, dt.minute)


def getEventFormByUserType(type, **kwargs):
    if type == "patient":
        obj = EventCreationFormPatient
    elif type == "doctor":
        obj = EventCreationFormDoctor
    elif type == 'nurse':
        obj = EventCreationFormNurse
    elif type == 'hosAdmin':
        obj = EventCreationFormHadmin

    if not('mode' in kwargs):
        kwargs['mode'] = 'create'


    return obj(**kwargs)




def doctor_nurse_shared_validation(event_form):
    valid = True

    #TODO: Clerify
    # hours = 1
    # valid &= EventCreationFormValidator.startDateInXhoursFuture(event_form, hours, {
    #     'startTime': "Start Time must be at least "+ str(hours) +" hours in the future"}, {})

    if event_form.mode == 'create':
        valid &= EventCreationFormValidator.eventValidateRequestTimeingOffset(event_form, 2, 0, {'startTime': "Events cannot start in the past"}, {})

    valid &= EventCreationFormValidator.eventPositiveDuration(event_form, datetime.timedelta(minutes=15),
                                                             {'duration': "Duration must be at least 15 minutes"},
                                                             {})
    return valid


class EventForm(forms.ModelForm):
    title = forms.CharField(label="Title", required=False)
    startTime = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime(attrs={'id': "dateTimeId"}), initial=timezone.now()+datetime.timedelta(days=1, minutes=30),
                                         label="Start Time")
    duration = forms.DurationField(initial=datetime.timedelta(minutes=30), label="Duration")
    description = forms.CharField(widget=forms.Textarea(), label="Description/Comments", required=False)

    def __init__(self, *args, **kwargs):

        if 'mode' in kwargs:
            self.mode = kwargs['mode']
            kwargs.pop('mode')

        super(EventForm, self).__init__(*args, **kwargs)




    def getModel(self):
        m = self.save(commit=False)
        m.endTime = m.startTime + self.cleaned_data['duration']

        return m


class EventCreationFormPatient(EventForm):

    def __init__(self, *args, **kwargs):
        super(EventCreationFormPatient, self).__init__(*args, **kwargs)
        self.order_fields(['title', 'startTime', 'duration', 'endTime', 'description']) # Change Field order so they are displayed properly

    def getModel(self):
        m = super(EventCreationFormPatient, self).getModel()
        m.appointment = True

        return m


    def is_valid(self):
        valid = super(EventCreationFormPatient, self).is_valid()
        if not valid:
            return valid

        valid &= EventCreationFormValidator.eventDurationBounded(self, 15, 30, {'duration': "Duration must be between 15 and 30 minutes"},{})

        if self.mode == 'create':
            valid &= EventCreationFormValidator.startDateInXhoursFuture(self, 24, {'startTime': "Start Time must be atleast 24 hours in the future"}, {})

        return valid

    class Meta:
        model = Event
        fields = ['startTime', 'description', 'title']


class EventCreationFormDoctor(EventForm):

    def __init__(self, *args, **kwargs):
        super(EventCreationFormDoctor, self).__init__(*args, **kwargs)
        self.order_fields(['title', 'type', 'patient', 'hospital', 'startTime', 'duration', 'description'])
        self.fields['patient'].widget.attrs = {'onchange': "resolve_dependancy(this)"}
        self.fields['hospital'].widget.attrs = {'onchange': "resolve_dependancy(this)"}

    def getModel(self):
        m = super(EventCreationFormDoctor, self).getModel()
        m.appointment = not(self.fields['patient'] is None)

        return m


    def is_valid(self):
        valid = super(EventCreationFormDoctor, self).is_valid()
        if not valid:
            return valid


        valid &= doctor_nurse_shared_validation(self)
        valid &= EventCreationFormValidator.patientMatchesHospitalDoctor(self,
                                                                   {'hospital': "The patient isn't at that hospital"},
                                                                   {})

        return valid


    def set_hospital_patient_queryset(self, hqset, pqset):
        self.fields['hospital'].queryset = hqset
        self.fields['patient'].queryset = pqset
        self.fields['hospital'].required = False
        self.fields['patient'].required = False


    class Meta:
        model = Event
        fields = ["title", "patient", "hospital", "startTime", "description"]


class EventCreationFormNurse(EventForm):

    def __init__(self, *args, **kwargs):
        super(EventCreationFormNurse, self).__init__(*args, **kwargs)
        self.elevated = False
        self.fields['patient'].widget.attrs = {'onchange': "resolve_dependancy(this)"}
        self.fields['doctor'].widget.attrs = {'onchange': "resolve_dependancy(this)"}
        self.fields['patient'].required = False
        self.fields['doctor'].required = False


    def getModel(self):
        m = super(EventCreationFormNurse, self).getModel()
        m.appointment = not(self.fields['patient'] is None)

        return m


    def is_valid(self):
        valid = super(EventCreationFormNurse, self).is_valid()
        if not valid:
            return valid

        valid &= doctor_nurse_shared_validation(self)
        if not self.elevated:
            valid &= EventCreationFormValidator.eventIsAppointment(self, {'patient': "This field is required"}, {})

        return valid


    def set_patient_doctor_queryset(self, patient_qset, doctor_qset):
        self.fields['patient'].queryset = patient_qset
        self.fields['doctor'].queryset = doctor_qset


    def elevate_permissions(self):
        self.elivated = True

    class Meta:
        model = Event
        fields = ["title", "patient", "doctor", "startTime", "description"]


class EventCreationFormHadmin(EventForm):
    type = forms.ChoiceField(widget=forms.RadioSelect, choices=(('1', 'Generic'), ('2', 'Appointment')))

    def set_patient_doctor_queryset(self, patient_qset, doctor_qset):
        self.fields['patient'].queryset = patient_qset
        self.fields['doctor'].queryset = doctor_qset
        self.fields['patient'].required = False
        self.fields['doctor'].required = False
        self.fields['patient'].widget.attrs = {'onchange': "resolve_dependancy(this)"}
        self.fields['doctor'].widget.attrs = {'onchange': "resolve_dependancy(this)"}

    class Meta:
        model = Event
        fields = ["patient", "doctor", "startTime", "description"]


class EditProfileForm_basic(forms.Form):
    first_name = forms.CharField(max_length=20, required=False)
    last_name = forms.CharField(max_length=20, required=False)
    email = forms.CharField(max_length=50, required=False)
    phone = forms.CharField(max_length=10, label="Phone Number", required=False)
    address = forms.CharField(max_length=50, label="Your Address", required=False)

    basic = forms.CharField(widget=forms.HiddenInput(), initial="HOLD")


class EditProfileForm_emergency(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    full_name = forms.CharField(max_length=50, required=False)
    phone = forms.CharField(max_length=10, label="Phone Number", required=False)
    emergency = forms.CharField(widget=forms.HiddenInput(), initial="HOLD")

    def is_valid(self):
        valid = super(EditProfileForm_emergency, self).is_valid()
        if not valid:
            return valid

        if self.cleaned_data['user'] is None:
            valid &= not((self.cleaned_data['full_name'] is None) or (self.cleaned_data['phone'] is None))
            if not valid:
                EventCreationFormValidator.add_messages(self, {'full_name': "Field Required", 'phone': "Field Required"}, {'user': "alternativly select a user from the system"})

        return valid


class EditProfileForm_medical(forms.Form):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=False)
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required=False)
    medical = forms.CharField(widget=forms.HiddenInput(), initial="HOLD")

    def __init__(self, *args, **kwargs):
        super(EditProfileForm_medical, self).__init__(*args, **kwargs)
        self.fields['doctor'].widget.attrs = {'onchange': "resolve_dependancy(this)"}
        self.fields['hospital'].widget.attrs = {'onchange': "resolve_dependancy(this)"}

    def is_valid(self):
        self.fields['doctor'].required = True
        self.fields['hospital'].required = True
        valid = super(EditProfileForm_medical, self).is_valid()
        if not valid:
            return valid

        return valid


class HosAdminSearchForm(forms.Form):
    keywords = forms.CharField(max_length=50, label="Keywords", required=False)
    choices = (('event', 'Events'), ('patient', 'Patients'), ('doctor', 'Doctors'), ('nurse', 'Nurses'), ('pending', 'Pending Staff'))
    filterBy = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), choices=choices, required=False, label="")


class SearchForm(forms.Form):
    keywords = forms.CharField(max_length=50, label="Keywords", required=False)
    choices = (('event', 'Events'), ('patient', 'Patients'), ('doctor', 'Doctors'))
    filterBy = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), choices=choices, required=False, label="")

    def setSearchForm(self, utype):
        if utype == 'doctor':
            choices = (
                ('event', 'Events'),
                ('patient', 'Patients'),
                ('doctor', 'Doctors'),
                ('mpatient', 'My Patients')
            )


class ApproveForm(forms.Form):
    approved = forms.BooleanField(label="Approved")

class RemoveApproval(forms.Form):
    remove = forms.BooleanField(label="Remove From Hospital")

class TrustedNurses(forms.Form):
    docs = forms.ModelChoiceField(queryset=Doctor.objects.none(), label="Doctors")

    def setQuerySet(self , qset):
        self.fields['docs'].queryset = qset