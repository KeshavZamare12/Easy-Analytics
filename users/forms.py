# users/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Profile  # Ensure you have a Profile model defined

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize error messages for the username field
        self.fields['username'].error_messages = {
            'required': "This field is required.",
            'invalid': "Enter a valid username.",
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    mobile_no = forms.CharField(max_length=15, required=False)
    profile_pic = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'mobile_no', 'profile_pic']
    
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your first name'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your last name'})
        self.fields['mobile_no'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your mobile number'})
        self.fields['profile_pic'].widget.attrs.update({'class': 'form-control','placeholder': "Add Profile Pic",
                                                        'label':'Add Profile Pic'})

class UploadFileForm(forms.Form):
    FILE_TYPE_CHOICES = [
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('xlsx', 'XLSX'),
    ]
    file_type = forms.ChoiceField(choices=FILE_TYPE_CHOICES, label="File Type")
    file = forms.FileField(label="Upload File",widget=forms.ClearableFileInput(attrs={'accept': '.json,.xlsx,.csv'}))
    #drive_link=forms.URLField(label="Drive Link")
    sheet_name = forms.CharField(max_length=100, required=True if file_type=='xlsx' else False, label="Sheet Name (if XLSX)")
    key_name = forms.CharField(max_length=100, required=True if file_type=='json' else False, label="Key Name (if JSON)")
    
    def clean(self):
        cleaned_data = super().clean()
        file_type = cleaned_data.get("file_type")
        sheet_name = cleaned_data.get("sheet_name")
        key_name = cleaned_data.get("key_name")

        # Make fields required based on file type
        if file_type == 'xlsx' and not sheet_name:
            self.add_error('sheet_name', "This field is required if the file type is XLSX.")
        
        return cleaned_data