from django import forms
from User.models import *
from hospital.models import *
from django.utils import timezone
from syslogging.models import *
import datetime
import logging
from emr.models import *

# Get an instance of a logger
logger = logging.getLogger(__name__)


"""This will create and update a user profile
class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(initial="")
    last_name = forms.CharField(initial="")
    email = forms.EmailField()

    def save(self, commit=True):
        m=super(ProfileForm, self).save(commit=False)
        m.user.first_name = self.cleaned_data['first_name']
        m.user.last_name = self.cleaned_data['last_name']
        m.user.email = self.cleaned_data['email']
        m.user.save()
        m.save()

    class Meta:
        model = Patient
        #first_name = forms.CharField()
        #last_name = forms.CharField()
        #hospital = forms.ModelChoiceField()
        #doctor = forms.ModelChoiceField()
        address = forms.CharField()
        #email = forms.CharField()
        phone = forms.CharField()
        fields = ['address', 'phone']"""



class EventCreationFormPatient(forms.ModelForm):

    duration = forms.IntegerField(label="Duration (min)", initial=30)

    def save_with_patient(self, p, commit=True):
        m = super(EventCreationFormPatient, self).save(commit=False)

        m.appointment = True
        m.endTime = m.startTime + datetime.timedelta(minutes=self.cleaned_data['duration'])
        m.hospital = p.hospital
        m.patient = p
        m.doctor = p.doctor

        if commit:
            m.save()
        return m

    class Meta:
        model = Event
        # hospital = forms.ModelChoiceField(queryset=Hospital.objects.all())
        # startTime = forms.DateTimeField(initial=timezone.now, label="Start Time")
        # endTime = forms.DateTimeField(label="End Time (min)")
        # description = forms.CharField(max_length=200, label="Description")
        fields = ['description', 'startTime']
        exclude = ['hospital', 'endTime']


class EventCreationFormNurse(forms.ModelForm):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=True)
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), required=False, empty_label="Not an Appointment")

    def is_valid(self):
        valid = super(EventCreationFormNurse, self).is_valid()
        if not valid:
            return valid

        if self.cleaned_data['patient'] != None:
            return self.cleaned_data['patient'].hospital == self.cleaned_data['doctor'].hospital

    def save_with_hosptial(self, h, commit=True):
        m = super(EventCreationFormNurse, self).save(commit=False)

        if (self.cleaned_data['patient'] != None):
            m.appointment = True
            m.hospital = h
            m.patient = self.cleaned_data['patient']
            m.save()
        elif commit:
            m.save()

        return m

    class Meta:
        model = Event
        fields = ['startTime', 'endTime', 'description', 'hospital']


class EventCreationFormDoctor(forms.ModelForm):
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), empty_label="Not an Appointment", required=False)

    def save_with_doctor(self, doctor, commit=True):
        m = super(EventCreationFormDoctor, self).save(commit=False)

        if(self.cleaned_data['patient'] != None):
            m.appointment = True
            m.patient = self.cleaned_data['patient']
            m.doctor = doctor
            m.save()
        elif commit:
            m.save()
        return m

    class Meta:
        model=Event
        fields = ['startTime', 'endTime', 'description', 'hospital']


class EventUpdateForm(forms.ModelForm):

    delete = forms.BooleanField(label="Delete?", initial=False)

    def save(self):
        pass

    class Meta:
        model=Event
        fields = ['startTime', 'endTime', 'description']


class EditProfileForm(forms.Form):
    first_name = forms.CharField(max_length=20, required=False)
    last_name = forms.CharField(max_length=20, required=False)
    email = forms.CharField(max_length=50, required=False)
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=False)
    phone = forms.CharField(max_length=10, label="Phone Number", required=False)
    address = forms.CharField(max_length=50, label="Your Address", required=False)
    emergency = forms.CharField(max_length=10, label="Emergency", required=False)

    height = forms.IntegerField(label="Height in Inches", required=False)
    weight = forms.IntegerField(label="Weight in Lbs", required=False)
    age = forms.IntegerField(label="Age in Years", required=False)
    restingBpm = forms.IntegerField(label="Usual Resting BPM", required=False)
    bloodPressure = forms.CharField(max_length=20, label="Blood pressure (###/###)", required=False)
    comments = forms.CharField(label="Comments", widget=forms.Textarea(), required=False)

    def save(self, commit=True):
        pass

    def set_defaults(self, user):
        self.fields['first_name'].initial = user.user.first_name
        self.fields['last_name'].initial = user.user.last_name
        self.fields['email'].initial = user.user.email

        if(user.doctor != None):
            self.fields['doctor'].initial = user.doctor
            self.fields['doctor'].disabled=True

        self.fields['phone'].initial = user.phone
        self.fields['address'].initial = user.address

        if(user.emr.emergency != None):
            self.fields['emergency'].initial = user.emr.emergency

        if(user.emr.emrvitals_set.all().count() != 0):
            self.fields['height'].disabled = True
            self.fields['weight'].disabled = True
            self.fields['age'].disabled = True
            self.fields['restingBpm'].disabled = True
            self.fields['bloodPressure'].disabled = True


    def save_user(self, m):
        m.user.first_name = self.cleaned_data['first_name']
        m.user.last_name = self.cleaned_data['last_name']
        m.user.email = self.cleaned_data['email']
        #m.doctor = self.cleaned_data['doctor']
        #m.hospital = m.doctor.hosptial
        m.address = self.cleaned_data['address']
        m.phone = self.cleaned_data['phone']
        m.emr.emergency = self.cleaned_data['emergency']
        m.emr.save()
        m.user.save()
        m.save()

        emrItem = EMRVitals.objects.create(emr = m.emr,
                                           height=self.cleaned_data['height'],
                                           weight=self.cleaned_data['weight'],
                                           age=self.cleaned_data['age'],
                                           bloodPressure=self.cleaned_data['bloodPressure'],
                                           restingBpm=self.cleaned_data['restingBpm'],
                                           comments=self.cleaned_data['comments']
        )

