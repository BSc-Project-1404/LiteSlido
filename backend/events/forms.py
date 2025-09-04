from django import forms
from .models import Event, Question, Poll, PollOption, Profile

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title']

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

# Form for creating a poll
class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['question']

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