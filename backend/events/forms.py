from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import Event, Question, Poll, PollOption, Profile

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full border rounded px-3 py-2 focus:outline-none focus:ring',
                'placeholder': 'Enter event title...'
            })
        }

# Form for creating a question
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']   # Only include the question text
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'w-full border rounded px-3 py-2 focus:outline-none focus:ring',
                'rows': 3,
                'placeholder': 'Your question...'
            })
        }

class AnonymousQuestionForm(forms.Form):
    """Form for anonymous users to ask questions"""
    username = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full border rounded px-3 py-2 focus:outline-none focus:ring',
            'placeholder': 'Your name (optional)'
        })
    )
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full border rounded px-3 py-2 focus:outline-none focus:ring',
            'rows': 3,
            'placeholder': 'Your question...'
        })
    )

# Form for creating a poll
class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['question']
        widgets = {
            'question': forms.TextInput(attrs={
                'class': 'w-full border rounded px-3 py-2 focus:outline-none focus:ring',
                'placeholder': 'Enter poll question...'
            })
        }

# Form for creating poll options
class PollOptionForm(forms.ModelForm):
    class Meta:
        model = PollOption
        fields = ['text']  # Only include the option text field

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        option_number = kwargs.get('prefix', '').split('_')[-1]
        
        # Set custom labels for the first two options
        if option_number == '0':
            self.fields['text'].label = 'Option 1:'
        elif option_number == '1':
            self.fields['text'].label = 'Option 2:'
        else:
            self.fields['text'].label = f'Option {int(option_number) + 1}:'

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'email', 'bio', 'avatar']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2 focus:outline-none focus:ring'}),
            'email': forms.EmailInput(attrs={'class': 'w-full border rounded px-3 py-2 focus:outline-none focus:ring', 'placeholder': 'Enter your email address'}),
            'bio': forms.Textarea(attrs={'class': 'w-full border rounded px-3 py-2 focus:outline-none focus:ring', 'rows': 4}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email is already used by another user
            if Profile.objects.filter(email=email).exclude(user=self.instance.user).exists():
                raise forms.ValidationError('This email address is already in use by another user.')
        return email



# Custom styled forms for authentication
class StyledUserCreationForm(UserCreationForm):
    """UserCreationForm with custom styling"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply custom styling to all fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    'class': 'w-full border-2 border-gray-200 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
                    'placeholder': field.label,
                    'id': f'id_{field_name}'
                })
            elif isinstance(field.widget, forms.PasswordInput):
                field.widget.attrs.update({
                    'class': 'w-full border-2 border-gray-200 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
                    'placeholder': field.label,
                    'id': f'id_{field_name}'
                })

class StyledAuthenticationForm(AuthenticationForm):
    """AuthenticationForm with custom styling"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply custom styling to username field
        self.fields['username'].widget.attrs.update({
            'class': 'pl-10 w-full border-2 border-gray-200 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Username'
        })

        # Apply custom styling to password field
        self.fields['password'].widget.attrs.update({
            'class': 'pl-10 w-full border-2 border-gray-200 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Password'
        })


class StyledPasswordChangeForm(PasswordChangeForm):
    """PasswordChangeForm with custom styling"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply custom styling to all password fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.PasswordInput):
                field.widget.attrs.update({
                    'class': 'w-full border rounded px-3 py-2 focus:outline-none focus:ring',
                    'placeholder': field.label
                })