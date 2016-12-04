from django.utils import timezone
import datetime
from user.models import Doctor, Patient
from django.contrib.auth.models import User
from hospital.models import *
from HealthNet.mixins import ModelDiffMixin
from django.db import models


class EMRItem(models.Model, ModelDiffMixin):
    """"This is generic item which can be stored in the EMR, other models will extend this"""

    PRIORITY_CHOICES = ((0, 'LOW'), (1, "MEDIUM"), (2, "HIGH"))

    patient = models.ForeignKey(Patient, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    content = models.CharField(max_length=200)
    priority = models.PositiveSmallIntegerField(choices=PRIORITY_CHOICES)

    def getTitle(self):
        for subtype in ['emrvitals', 'emrprofile', 'emrtest', 'emrprescription', 'emradmitstatus']:
            if hasattr(self, subtype):
                return getattr(self, subtype).getTitle()
        return 'Note'

    def getType(self):
        for subtype in ['emrvitals', 'emrprofile', 'emrtest', 'emrprescription', 'emradmitstatus']:
            if hasattr(self, subtype):
                return getattr(self, subtype).getType()
        return 'note'

    def getPriorityStr(self):
        index = int(self.priority)
        if index <= 2:
            return self.PRIORITY_CHOICES[index][1]
        else:
            return self.PRIORITY_CHOICES[-1][1]


class EMRVitals(EMRItem):
    """This model will store a set of vital sign readings as well as height, weight ...etc"""
    restingBPM = models.IntegerField(default=0)  # Resting pulse in beats/min
    bloodPressure = models.CharField(max_length=10, default="")  # Blood pressure in format ###/###
    height = models.FloatField(default=0)  # Height of the patient in inches
    weight = models.FloatField(default=0)  # Weight of a person in Lbs

    @property
    def emritem(self):
        return EMRItem.objects.get(pk=self.emritem_ptr_id)

    def getType(self):
        return 'vitals'

    def getTitle(self):
        return "Vitals"


class EMRAdmitStatus(EMRItem):
    hospital = models.ForeignKey(Hospital, null=True, blank=True)
    admit = models.BooleanField(default=True, editable=False)

    @property
    def emritem(self):
        return EMRItem.objects.get(pk=self.emritem_ptr_id)

    def getType(self):
        if self.admit:
            return 'admit'
        return 'discharge'

    def getTitle(self):
        if self.admit:
            return "Admission"
        else:
            return "Discharge"


class EMRProfile(models.Model, ModelDiffMixin):
    patient = models.OneToOneField(Patient, blank=True, null=True)
    birthdate = models.DateTimeField(default=timezone.now)
    gender = models.CharField(max_length=10, default="")
    blood_type = models.CharField(max_length=3, default="")
    family_history = models.CharField(max_length=200, default="")
    comments = models.CharField(max_length=200, default="")

    admit_status = models.OneToOneField(EMRAdmitStatus, blank=True, null=True)


    def getInumber(self):
        return self.patient.insuranceNum

    def getAge(self):
        years = timezone.now().year - self.birthdate.year
        months = timezone.now().month - self.birthdate.month
        days = timezone.now().day - self.birthdate.day

        inc = (months>=0) and (days>=0)
        if inc:
            years += 1

        return years

    def getType(self):
        return 'profile'


class EMRTest(EMRItem, ModelDiffMixin):
    images = models.ImageField(null=True, blank=True)
    released = models.BooleanField(default=False)

    @property
    def emritem(self):
        items = EMRItem.objects.all().filter(pk=self.emritem_ptr_id)
        if items.count() > 0:
            return items[0]
        return None

    def getType(self):
        return 'test'

    def getTitle(self):
        if bool(self.released):
            return "Test"
        else:
            return "Test (Pending)"


class FilterForm(models.Model):
    user = models.OneToOneField(User, blank=True, null=True)
    keywords = models.CharField(max_length=100, default="", blank=True, null=True)
    filters = models.CharField(max_length=20, default="", blank=True, null=True)
    sort = models.CharField(max_length=20, default="", blank=True, null=True)


"""
This Prescription class holds all the information relating to a single prescription

Extending EMRItem for created DateTime and linked to a emr
"""
class EMRPrescription(EMRItem):
    # Created DateTimeField is found in EMRItem
    proivder = models.ForeignKey(User, null=True, blank=True)
    medication = models.CharField(max_length=50, default="")
    dosage = models.CharField(max_length=50, default="", null=False)
    amountPerDay = models.CharField(max_length=50, default="", null=False)
    startDate = models.DateField(default=datetime.date.today)
    endDate = models.DateField(default=(timezone.now() + datetime.timedelta(days=30)))
    deactivated = models.BooleanField(default=False)

    @property
    def emritem(self):
        return EMRItem.objects.get(pk=self.emritem_ptr_id)

    def getType(self):
        return 'prescription'

    def getTitle(self):
        return "Prescription"


def isTest(item):
    return hasattr(item, 'emrtest') or isinstance(item, EMRTest)

def isVital(item):
    return hasattr(item, 'emrvitals') or isinstance(item, EMRVitals)

def isAdmit(item):
    return hasattr(item, 'emradmitstatus') or isinstance(item, EMRAdmitStatus)

def isPrescription(item):
    return hasattr(item, 'emrprescription') or isinstance(item, EMRPrescription)

def isNote(item):
    return not(isAdmit(item) or isTest(item) or isVital(item) or isPrescription(item))

def emrItemType(item):
    if isTest(item):
        return 'test'
    elif isVital(item):
        return 'vitals'
    elif isPrescription(item):
        return 'prescription'
    elif isAdmit(item):
        return 'admitdischarge'

    return 'note'