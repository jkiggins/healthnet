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
    obj = None
    if type == "patient":
        obj = EventCreationFormPatient
    elif type == "doctor":
        obj = EventCreationFormDoctor
    elif type == 'nurse':
        obj = EventCreationFormNurse
    elif type == 'hosAdmin':
        obj = EventCreationFormHadmin

    return obj(**kwargs)


def doctor_nurse_shared_validation(event_form):
    valid = True

    #TODO: Clerify
    # hours = 1
    # valid &= EventCreationFormValidator.startDateInXhoursFuture(event_form, hours, {
    #     'startTime': "Start Time must be at least "+ str(hours) +" hours in the future"}, {})

    if event_form.instance is None:
        valid &= EventCreationFormValidator.eventValidateRequestTimeingOffset(event_form, 2, 0, {'startTime': "Events cannot start in the past"}, {})

    valid &= EventCreationFormValidator.eventPositiveDuration(event_form, datetime.timedelta(minutes=15),
                                                             {'duration': "Duration must be at least 15 minutes"},
                                                             {})
    return valid


class EventForm(forms.ModelForm):
    startTime = forms.SplitDateTimeField(widget=forms.SplitDateTimeWidget(attrs={'id': "dateTimeId"}), initial=timezone.now()+datetime.timedelta(days=1, minutes=30),
                                         label="Start", input_time_formats=['%H:%M', '%I:%M%p', '%I:%M %p', '%H:%M:%S'])
    duration = forms.DurationField(initial=datetime.timedelta(minutes=30), label="Duration")
    description = forms.CharField(widget=forms.Textarea(), label="Description/Comments", required=False)

    def setStart(self, dt):
        self.fields['startTime'].initial = dt

    def save(self, commit=False):
        m = super(EventForm, self).save(commit=False)
        m.endTime = m.startTime + self.cleaned_data['duration']

        if commit:
            m.save()

        return m





class EventCreationFormPatient(EventForm):

    def __init__(self, *args, **kwargs):
        super(EventCreationFormPatient, self).__init__(*args, **kwargs)
        self.fields['duration'].disabled=True

        self.order_fields(['startTime', 'duration', 'description']) # Change Field order so they are displayed properly


    def is_valid(self):
        valid = super(EventCreationFormPatient, self).is_valid()
        if not valid:
            return valid

        if self.instance is None:
            valid &= EventCreationFormValidator.startDateInXhoursFuture(self, 24, {'startTime': "Start Time must be atleast 24 hours in the future"}, {})

        return valid

    class Meta:
        model = Event
        fields = ['startTime', 'description']


class EventCreationFormDoctor(EventForm):

    def __init__(self, *args, **kwargs):
        super(EventCreationFormDoctor, self).__init__(*args, **kwargs)
        self.order_fields(['type', 'patient', 'hospital', 'startTime', 'duration', 'description'])
        self.fields['patient'].widget.attrs = {'onchange': "resolve_pd_dependancy(this)", 'data-key': "patient"}
        self.fields['hospital'].widget.attrs = {'onchange': "resolve_pd_dependancy(this)", 'data-key': "hospital"}


    def is_valid(self):
        valid = super(EventCreationFormDoctor, self).is_valid()
        if not valid:
            return valid


        valid &= doctor_nurse_shared_validation(self)
        valid &= EventCreationFormValidator.patientMatchesHospitalDoctor(self,
                                                                   {'hospital': "The patient isn't at that hospital"},
                                                                   {})

        return valid


    def save(self, commit=False):
        m = super(EventCreationFormDoctor, self).save(commit=False)
        if m.patient is None:
            m.appointment = False

        if commit:
            m.save()

        return m


    def set_hospital_patient_queryset(self, hqset, pqset):
        self.fields['hospital'].queryset = hqset
        self.fields['patient'].queryset = pqset
        self.fields['hospital'].required = False
        self.fields['patient'].required = False


    class Meta:
        model = Event
        fields = ["patient", "hospital", "startTime", "description"]


class EventCreationFormNurse(EventForm):

    def __init__(self, *args, **kwargs):
        super(EventCreationFormNurse, self).__init__(*args, **kwargs)
        self.elevated = False
        self.fields['patient'].widget.attrs = {'onchange': "resolve_pd_dependancy(this)"}
        self.fields['doctor'].widget.attrs = {'onchange': "resolve_pd_dependancy(this)"}
        self.fields['patient'].required = False
        self.fields['doctor'].required = False


    def is_valid(self):
        valid = super(EventCreationFormNurse, self).is_valid()
        if not valid:
            return valid

        valid &= doctor_nurse_shared_validation(self)
        if not self.elevated:
            valid &= EventCreationFormValidator.eventIsAppointment(self, {'patient': "This field is required"}, {})

        return valid

    def save(self, commit=False):
        m = super(EventCreationFormNurse, self).save(commit=False)

        if m.patient is None:
            m.appointment = False

        if commit:
            m.save()

        return m


    def set_patient_doctor_queryset(self, patient_qset, doctor_qset):
        self.fields['patient'].queryset = patient_qset
        self.fields['doctor'].queryset = doctor_qset


    def elevate_permissions(self):
        self.elivated = True

    class Meta:
        model = Event
        fields = ["patient", "doctor", "startTime", "description"]


class EventCreationFormHadmin(EventForm):
    type = forms.ChoiceField(widget=forms.RadioSelect, choices=(('1', 'Generic'), ('2', 'Appointment')))

    def set_patient_doctor_queryset(self, patient_qset, doctor_qset):
        self.fields['patient'].queryset = patient_qset
        self.fields['doctor'].queryset = doctor_qset
        self.fields['patient'].required = False
        self.fields['doctor'].required = True

    def save(self, commit=False):
        m = super(EventCreationFormHadmin, self).save(commit=False)

        if m.patient is None:
            m.appointment = False

        if commit:
            m.save()

        return m

    class Meta:
        model = Event
        fields = ["patient", "doctor", "startTime", "description"]


class EditProfileForm(forms.Form):
    first_name = forms.CharField(max_length=20, required=False)
    last_name = forms.CharField(max_length=20, required=False)
    email = forms.CharField(max_length=50, required=False)
    phone = forms.CharField(max_length=10, label="Phone Number", required=False)
    address = forms.CharField(max_length=50, label="Your Address", required=False)

    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=False)
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required=False)

    emuser = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    full_name = forms.CharField(max_length=50, required=False)
    emphone = forms.CharField(max_length=10, label="Phone Number", required=False)

    def filterUserQuerySet(self, user):
        self.fields['emuser'].queryset = User.objects.all().exclude(pk = user.pk)

    def is_valid(self):
        self.fields['doctor'].required = True
        self.fields['hospital'].required = True
        valid = super(EditProfileForm, self).is_valid()
        if not valid:
            return valid

        if self.cleaned_data['emuser'] is None:
            valid &= not((self.cleaned_data['full_name'] is None) or (self.cleaned_data['phone'] is None))
            if not valid:
                EventCreationFormValidator.add_messages(self, {'full_name': "Field Required", 'phone': "Field Required"}, {'user': "alternativly select a user from the system"})

        return valid

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['doctor'].widget.attrs = {'onchange': "resolve_pd_dependancy(this)"}
        self.fields['hospital'].widget.attrs = {'onchange': "resolve_pd_dependancy(this)"}


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
        self.fields['docs'].queryset = qset

class messagingForm(forms.Form):
    userTO = forms.ModelChoiceField(queryset=Doctor.objects.all(), label="To:", required=True)
    messageContent = forms.CharField(widget=forms.Textarea, max_length=None, label="Message", min_length=1, required=True)

    def staff_queryset(self, staff_qset):
        self.fields['userTO'].queryset = staff_qset

    def is_valid(self):
        self.fields['userTO'].required = True
        self.fields['messageContent'].required = True
        valid = super(messagingForm, self).is_valid()
        if not valid:
            return valid

        return valid


class statsForm(forms.Form):
    kw_admit = forms.CharField(
        widget=forms.TextInput(attrs={'class': "toolbar_item_kw", 'placeholder': "Keywords..."}), required=False)
    kw_dis = forms.CharField(
        widget=forms.TextInput(attrs={'class': "toolbar_item_kw", 'placeholder': "Keywords..."}),
        required=False)
    kw_pre = forms.CharField(
        widget=forms.TextInput(attrs={'class': "toolbar_item_kw", 'placeholder': "Keywords..."}),
        required=False)
    kw_patient = forms.CharField(
        widget=forms.TextInput(attrs={'class': "toolbar_item_kw", 'placeholder': "Keywords..."}),
        required=False)

    start = forms.SplitDateTimeField(widget=forms.SplitDateTimeWidget(attrs={'id': "dateTimeIds"}),
                                         initial=timezone.now() + datetime.timedelta(days=1, minutes=30),
                                         label="Start", input_time_formats=['%H:%M', '%I:%M%p', '%I:%M %p', '%H:%M:%S'])

    end = forms.SplitDateTimeField(widget=forms.SplitDateTimeWidget(attrs={'id': "dateTimeIde"}),
                                         initial=timezone.now() + datetime.timedelta(days=1, minutes=30),
                                         label="End", input_time_formats=['%H:%M', '%I:%M%p', '%I:%M %p', '%H:%M:%S'])

    filter_choices = (
        ('ave_patient', "Average Number of patients visiting the hospital each day"),
        ('ave_visits', "Average Visits for the selected patients"),
        ('comm_admit', "Most common reasons for admission"),
        ('comm_pres', "Most common prescriptions"),
    )

    filters = forms.MultipleChoiceField(required=False, choices=filter_choices,
                                          widget=forms.CheckboxSelectMultiple(attrs={'class': 'toolbar_item_checkbox'}))