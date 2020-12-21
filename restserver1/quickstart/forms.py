from bootstrap_datepicker_plus import DatePickerInput
from django import forms


class dateForm(forms.Form):
	start = forms.DateField()
	end = forms.DateField()


