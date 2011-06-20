import calendar
import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _


from auth.models import User

MONTH = [ (str(i+1),m) for i,m in enumerate(calendar.month_name[1:]) ]
DAY = [ (str(i),str(i)) for i in range(1,32) ]

class BidderForm(forms.Form):
#    first_name = forms.CharField(label=_("First name"), max_length=50, required=True) 
#    last_name = forms.CharField(label=_("Last name"), max_length=50, required=True)
#    street_address = forms.CharField(label=_("Street address"), max_length=80, required=True)
#    city = forms.CharField(label=_("City"), max_length=80, required=True)
#    state = forms.CharField(label=_("State / Province"), max_length=80, required=True)
#    zip = forms.CharField(label=_("ZIP / Portal code"), max_length=30, required=True)
#    country = forms.CharField(label=_("Country or region"), max_length=50, required=True)
#    phone = forms.CharField(label=_("Telephone number"), max_length=50, required=True)
    

    username = forms.RegexField(label=_("User ID"), max_length=30, regex=r'^\w+$', required=False,
        help_text = _("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."),
        error_message = _("This value must contain only letters, numbers and underscores."))
    
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)

    email = forms.EmailField(required=True)
#    re_email = forms.EmailField(required=True)

#    month = forms.ChoiceField(choices=MONTH, label=_("Month"))    
#    day = forms.ChoiceField(choices=DAY, label=_("Day"))    
#    year = forms.CharField(label=_("Year"))    

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(BidderForm, self).__init__(*args, **kwargs)
    
    def clean_username(self):
        #TODO: check
        username = self.cleaned_data["username"]
        username = username.strip()
        if username == "":
            raise forms.ValidationError(_("Username field can't be blank."))
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("A user with that username already exists."))

    def clean_email(self):
        #TODO: check
        email = self.cleaned_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(_("A user with that email already exists."))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

#    def clean_re_email(self):
#        email = self.cleaned_data.get("email", "")
#        re_email = self.cleaned_data["re_email"]
#        if email != re_email:
#            raise forms.ValidationError(_("The two email fields didn't match."))
#        return re_email
#
#    def clean_year(self):
#        day = self.cleaned_data.get('day','')
#        month = self.cleaned_data.get('month','')
#        year = self.cleaned_data.get('year','')
#        
#        if year == '':
#            raise forms.ValidationError(_("This field is required."))
#        try:
#            datetime.date(int(year),int(month),int(day))
#        except:
#            raise forms.ValidationError(_("Day is out of range for month."))
#        return year