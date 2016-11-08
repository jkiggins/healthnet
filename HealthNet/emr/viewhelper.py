import re
from django.utils import timezone
import datetime

def try_parse(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def getPatientAdmitStatus(patient):
    if patient.emritem_set.all().exclude(emradmitstatus=None).order_by('date_created')[0].admit:
        return 'admit'
    return 'discharge'


# TODO: this would be relly cool, do it for real R2
# def parsePhrases(keywords):
#     """Parse phrases from keywords possibilites are:
#         r"last ([0-9]+) (days|months|years|hours|minutes|min)"
#     """
#
#     last = re.compile(r"last ([0-9]+) (days|months|years|hours|minutes|min)")
#     last_match = last.search(keywords)
#     dict = {}
#
#     if last_match:
#         keywords = keywords.replace(last_match.group(0), '')
#         dict['endTime'] = timezone.now()
#         dict['startTime'] =
