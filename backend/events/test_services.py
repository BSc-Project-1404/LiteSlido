from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.db.models import Count
from unittest.mock import patch, MagicMock
from .models import Event, Question, Poll, PollOption, PollVote, Profile
from .forms import EventForm, QuestionForm, PollForm, PollOptionForm, ProfileForm
from . import services


class ServicesTestCase(TestCase):
    def setUp(self):
        """Set up test data for all tests"""
        self.factory = RequestFactory()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Create test event
        self.event = Event.objects.create(
            title='Test Event',
            creator=self.user1
        )
        
        # Create test question
        self.question = Question.objects.create(
            event=self.event,
            author=self.user2,
            text='Test question?'
        )
        
        # Create test poll
        self.poll = Poll.objects.create(
            event=self.event,
            question='Test poll question?'
        )
        
        # Create test poll options
        self.poll_option1 = PollOption.objects.create(
            poll=self.poll,
            text='Option 1'
        )
        self.poll_option2 = PollOption.objects.create(
            poll=self.poll,
            text='Option 2'
        )
        
        # Get the automatically created profile (created by signals.py)
        self.profile = self.user1.profile

    def test_get_event_list_data_success(self):
        """Test successful event list data retrieval"""
        request = self.factory.get('/events/')
        request.user = self.user1
        
        result = services.get_event_list_data(request)
        
        self.assertIn('my_events', result)
        self.assertIn('join_error', result)
        self.assertEqual(list(result['my_events']), [self.event])
        self.assertIsNone(result['join_error'])

    def test_get_event_list_data_with_valid_join_code(self):
        """Test joining event with valid code"""
        request = self.factory.post('/events/', {'event_code': self.event.code})
        request.user = self.user1
        
        result = services.get_event_list_data(request)
        
        self.assertIn('redirect', result)
        self.assertEqual(result['redirect'][0], 'event_detail')
        self.assertEqual(result['redirect'][1]['event_code'], self.event.code)

    def test_get_event_list_data_with_invalid_join_code(self):
        """Test joining event with invalid code"""
        request = self.factory.post('/events/', {'event_code': 'INVALID'})
        request.user = self.user1
        
        result = services.get_event_list_data(request)
        
        self.assertIn('join_error', result)
        self.assertEqual(result['join_error'], 'Invalid event code.')

    def test_create_event_success(self):
        """Test successful event creation"""
        request = self.factory.post('/events/create/', {'title': 'New Event'})
        request.user = self.user1
        
        result = services.create_event(request)
        
        self.assertIn('redirect', result)
        self.assertEqual(result['redirect'][0], 'event_list')
        
        # Verify event was created
        new_event = Event.objects.get(title='New Event')
        self.assertEqual(new_event.creator, self.user1)

    def test_create_event_get_request(self):
        """Test event creation form display"""
        request = self.factory.get('/events/create/')
        request.user = self.user1
        
        result = services.create_event(request)
        
        self.assertIn('form', result)
        self.assertIsInstance(result['form'], EventForm)

    def test_create_event_invalid_form(self):
        """Test event creation with invalid form"""
        request = self.factory.post('/events/create/', {'title': ''})  # Empty title
        request.user = self.user1
        
        result = services.create_event(request)
        
        self.assertIn('form', result)
        self.assertIsInstance(result['form'], EventForm)
        self.assertFalse(result['form'].is_valid())

    def test_add_question_to_event_success(self):
        """Test successful question addition"""
        request = self.factory.post('/events/question/', {'text': 'New question?'})
        request.user = self.user2
        
        result = services.add_question_to_event(request, self.event.code)
        
        self.assertIn('redirect', result)
        self.assertEqual(result['redirect'][0], 'event_detail')
        
        # Verify question was created
        new_question = Question.objects.get(text='New question?')
        self.assertEqual(new_question.event, self.event)
        self.assertEqual(new_question.author, self.user2)

    def test_add_question_to_event_get_request(self):
        """Test question form display"""
        request = self.factory.get('/events/question/')
        request.user = self.user2
        
        result = services.add_question_to_event(request, self.event.code)
        
        self.assertIn('form', result)
        self.assertIn('event', result)
        self.assertIsInstance(result['form'], QuestionForm)
        self.assertEqual(result['event'], self.event)

    def test_add_question_to_event_invalid_form(self):
        """Test question addition with invalid form"""
        request = self.factory.post('/events/question/', {'text': ''})  # Empty text
        request.user = self.user2
        
        result = services.add_question_to_event(request, self.event.code)
        
        self.assertIn('form', result)
        self.assertIsInstance(result['form'], QuestionForm)
        self.assertFalse(result['form'].is_valid())

    def test_add_poll_to_event_success(self):
        """Test successful poll creation"""
        request = self.factory.post('/events/poll/', {
            'question': 'New poll question?',
            'num_options': '2',
            'option_0-text': 'Option A',
            'option_1-text': 'Option B'
        })
        request.user = self.user1  # Event creator
        
        result = services.add_poll_to_event(request, self.event.code)
        
        self.assertIn('redirect', result)
        self.assertEqual(result['redirect'][0], 'event_detail')
        
        # Verify poll was created
        new_poll = Poll.objects.get(question='New poll question?')
        self.assertEqual(new_poll.event, self.event)
        
        # Verify options were created
        options = new_poll.options.all()
        self.assertEqual(options.count(), 2)
        self.assertIn('Option A', [opt.text for opt in options])
        self.assertIn('Option B', [opt.text for opt in options])

    def test_add_poll_to_event_unauthorized(self):
        """Test poll creation by non-creator"""
        request = self.factory.post('/events/poll/', {'question': 'New poll?'})
        request.user = self.user2  # Not event creator
        
        result = services.add_poll_to_event(request, self.event.code)
        
        self.assertIsInstance(result, HttpResponseForbidden)

    def test_add_poll_to_event_get_request(self):
        """Test poll form display"""
        request = self.factory.get('/events/poll/')
        request.user = self.user1
        
        result = services.add_poll_to_event(request, self.event.code)
        
        self.assertIn('form', result)
        self.assertIn('option_forms', result)
        self.assertIn('event', result)
        self.assertIn('num_options', result)
        self.assertIsInstance(result['form'], PollForm)
        self.assertEqual(result['num_options'], 2)

    def test_get_event_detail_data_open_event(self):
        """Test event detail data for open event"""
        request = self.factory.get('/events/detail/')
        request.user = self.user1
        
        result = services.get_event_detail_data(request, self.event.code)
        
        self.assertIn('event', result)
        self.assertIn('questions', result)
        self.assertIn('polls', result)
        self.assertEqual(result['event'], self.event)
        self.assertEqual(list(result['questions']), [self.question])
        self.assertEqual(list(result['polls']), [self.poll])

    def test_get_event_detail_data_closed_event_creator(self):
        """Test event detail data for closed event (creator access)"""
        self.event.is_closed = True
        self.event.save()
        
        request = self.factory.get('/events/detail/')
        request.user = self.user1  # Event creator
        
        result = services.get_event_detail_data(request, self.event.code)
        
        self.assertIn('event', result)
        self.assertNotIn('render', result)

    def test_get_event_detail_data_closed_event_non_creator(self):
        """Test event detail data for closed event (non-creator access)"""
        self.event.is_closed = True
        self.event.save()
        
        request = self.factory.get('/events/detail/')
        request.user = self.user2  # Not event creator
        
        result = services.get_event_detail_data(request, self.event.code)
        
        self.assertIn('render', result)
        self.assertEqual(result['render'][0], 'events/event_closed.html')
        self.assertEqual(result['render'][2], 404)

    def test_vote_for_poll_success(self):
        """Test successful poll voting"""
        request = self.factory.post('/events/vote/', {'poll_option': self.poll_option1.id})
        request.user = self.user2
        
        result = services.vote_for_poll(request, self.event.code, self.poll.id)
        
        self.assertIn('redirect', result)
        self.assertEqual(result['redirect'][0], 'event_detail')
        
        # Verify vote was created
        vote = PollVote.objects.get(user=self.user2, poll_option__poll=self.poll)
        self.assertEqual(vote.poll_option, self.poll_option1)

    def test_vote_for_poll_get_request(self):
        """Test poll voting form display"""
        request = self.factory.get('/events/vote/')
        request.user = self.user2
        
        result = services.vote_for_poll(request, self.event.code, self.poll.id)
        
        self.assertIn('poll', result)
        self.assertIn('options', result)
        self.assertIn('event_code', result)
        self.assertEqual(result['poll'], self.poll)
        self.assertEqual(result['event_code'], self.event.code)

    def test_vote_for_poll_duplicate_vote(self):
        """Test preventing duplicate votes"""
        # Create initial vote
        PollVote.objects.create(user=self.user2, poll_option=self.poll_option1)
        
        request = self.factory.post('/events/vote/', {'poll_option': self.poll_option2.id})
        request.user = self.user2
        
        result = services.vote_for_poll(request, self.event.code, self.poll.id)
        
        self.assertNotIn('redirect', result)
        self.assertIn('poll', result)
        
        # Verify only one vote exists
        votes = PollVote.objects.filter(user=self.user2, poll_option__poll=self.poll)
        self.assertEqual(votes.count(), 1)

    def test_get_poll_detail_data_success(self):
        """Test successful poll detail data retrieval"""
        request = self.factory.get('/events/poll/detail/')
        request.user = self.user2
        
        result = services.get_poll_detail_data(request, self.event.code, self.poll.id)
        
        self.assertIn('event', result)
        self.assertIn('poll', result)
        self.assertIn('user_has_voted', result)
        self.assertIn('option_votes_list', result)
        self.assertEqual(result['event'], self.event)
        self.assertEqual(result['poll'], self.poll)
        self.assertFalse(result['user_has_voted'])
        self.assertEqual(len(result['option_votes_list']), 2)

    def test_get_poll_detail_data_with_voting(self):
        """Test poll detail data with voting"""
        request = self.factory.post('/events/poll/detail/', {'poll_option': self.poll_option1.id})
        request.user = self.user2
        
        result = services.get_poll_detail_data(request, self.event.code, self.poll.id)
        
        self.assertIn('redirect', result)
        self.assertEqual(result['redirect'][0], 'poll_detail')
        
        # Verify vote was created
        vote = PollVote.objects.get(user=self.user2, poll_option__poll=self.poll)
        self.assertEqual(vote.poll_option, self.poll_option1)

    def test_get_poll_detail_data_already_voted(self):
        """Test poll detail data when user already voted"""
        # Create initial vote
        PollVote.objects.create(user=self.user2, poll_option=self.poll_option1)
        
        request = self.factory.post('/events/poll/detail/', {'poll_option': self.poll_option2.id})
        request.user = self.user2
        
        result = services.get_poll_detail_data(request, self.event.code, self.poll.id)
        
        self.assertNotIn('redirect', result)
        self.assertTrue(result['user_has_voted'])

    def test_register_user_success(self):
        """Test successful user registration"""
        # Mock the login function to avoid session issues
        with patch('events.services.login') as mock_login:
            request = self.factory.post('/register/', {
                'username': 'newuser',
                'password1': 'newpass123',
                'password2': 'newpass123'
            })
            
            result = services.register_user(request)
            
            self.assertIn('redirect', result)
            self.assertEqual(result['redirect'][0], 'event_list')
            
            # Verify user was created
            new_user = User.objects.get(username='newuser')
            self.assertIsNotNone(new_user)
            
            # Verify login was called
            mock_login.assert_called_once()

    def test_register_user_get_request(self):
        """Test user registration form display"""
        request = self.factory.get('/register/')
        
        result = services.register_user(request)
        
        self.assertIn('form', result)
        self.assertIsInstance(result['form'], UserCreationForm)

    def test_register_user_invalid_form(self):
        """Test user registration with invalid form"""
        request = self.factory.post('/register/', {
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'wrongpass'  # Mismatched passwords
        })
        
        result = services.register_user(request)
        
        self.assertIn('form', result)
        self.assertIsInstance(result['form'], UserCreationForm)
        self.assertFalse(result['form'].is_valid())

    def test_toggle_question_like_add_like(self):
        """Test adding a like to a question"""
        request = self.factory.post('/events/question/like/')
        request.user = self.user1
        request.META = {'HTTP_REFERER': '/events/detail/'}
        
        result = services.toggle_question_like(request, self.question.id)
        
        self.assertIsInstance(result, HttpResponseRedirect)
        self.assertIn(self.user1, self.question.likes.all())

    def test_toggle_question_like_remove_like(self):
        """Test removing a like from a question"""
        # Add initial like
        self.question.likes.add(self.user1)
        
        request = self.factory.post('/events/question/like/')
        request.user = self.user1
        request.META = {'HTTP_REFERER': '/events/detail/'}
        
        result = services.toggle_question_like(request, self.question.id)
        
        self.assertIsInstance(result, HttpResponseRedirect)
        self.assertNotIn(self.user1, self.question.likes.all())

    def test_toggle_event_close_status_success(self):
        """Test successful event close status toggle"""
        request = self.factory.post('/events/close/')
        request.user = self.user1  # Event creator
        
        result = services.toggle_event_close_status(request, self.event.code)
        
        self.assertIn('redirect', result)
        self.assertEqual(result['redirect'][0], 'event_detail')
        
        # Verify status was toggled
        self.event.refresh_from_db()
        self.assertTrue(self.event.is_closed)

    def test_toggle_event_close_status_unauthorized(self):
        """Test event close status toggle by non-creator"""
        request = self.factory.post('/events/close/')
        request.user = self.user2  # Not event creator
        
        result = services.toggle_event_close_status(request, self.event.code)
        
        self.assertIsInstance(result, HttpResponseForbidden)

    def test_get_user_profile(self):
        """Test user profile retrieval"""
        request = self.factory.get('/profile/')
        request.user = self.user1
        
        result = services.get_user_profile(request)
        
        self.assertIn('profile', result)
        self.assertEqual(result['profile'], self.profile)

    def test_edit_user_profile_success(self):
        """Test successful user profile editing"""
        request = self.factory.post('/profile/edit/', {
            'full_name': 'Updated Name',
            'bio': 'Updated bio'
        })
        request.user = self.user1
        
        result = services.edit_user_profile(request)
        
        self.assertIn('redirect', result)
        self.assertEqual(result['redirect'][0], 'profile')
        
        # Verify profile was updated
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.full_name, 'Updated Name')
        self.assertEqual(self.profile.bio, 'Updated bio')

    def test_edit_user_profile_get_request(self):
        """Test user profile edit form display"""
        request = self.factory.get('/profile/edit/')
        request.user = self.user1
        
        result = services.edit_user_profile(request)
        
        self.assertIn('form', result)
        self.assertIsInstance(result['form'], ProfileForm)

    def test_change_user_password_success(self):
        """Test successful password change"""
        # Mock the update_session_auth_hash function to avoid session issues
        with patch('events.services.update_session_auth_hash') as mock_update:
            request = self.factory.post('/profile/password/', {
                'old_password': 'testpass123',
                'new_password1': 'newpass123',
                'new_password2': 'newpass123'
            })
            request.user = self.user1
            
            result = services.change_user_password(request)
            
            self.assertIn('redirect', result)
            self.assertEqual(result['redirect'][0], 'profile')
            
            # Verify update_session_auth_hash was called
            mock_update.assert_called_once()

    def test_change_user_password_get_request(self):
        """Test password change form display"""
        request = self.factory.get('/profile/password/')
        request.user = self.user1
        
        result = services.change_user_password(request)
        
        self.assertIn('form', result)
        self.assertIsInstance(result['form'], PasswordChangeForm)

    def test_delete_event_question_success(self):
        """Test successful question deletion"""
        # Mock the messages.success function to avoid middleware issues
        with patch('events.services.messages.success') as mock_messages:
            request = self.factory.post('/events/question/delete/')
            request.user = self.user1  # Event creator
            
            result = services.delete_event_question(request, self.event.code, self.question.id)
            
            self.assertIn('redirect', result)
            self.assertEqual(result['redirect'][0], 'event_detail')
            
            # Verify question was deleted
            self.assertFalse(Question.objects.filter(id=self.question.id).exists())
            
            # Verify success message was called
            mock_messages.assert_called_once_with(request, "Question deleted.")

    def test_delete_event_question_unauthorized(self):
        """Test question deletion by non-creator"""
        request = self.factory.post('/events/question/delete/')
        request.user = self.user2  # Not event creator
        
        result = services.delete_event_question(request, self.event.code, self.question.id)
        
        self.assertIsInstance(result, HttpResponseForbidden)

    def test_delete_event_question_get_request(self):
        """Test question deletion form display (redirects)"""
        request = self.factory.get('/events/question/delete/')
        request.user = self.user1
        
        result = services.delete_event_question(request, self.event.code, self.question.id)
        
        self.assertIn('redirect', result)
        self.assertEqual(result['redirect'][0], 'event_detail')

    def test_questions_ordered_by_likes_and_date(self):
        """Test that questions are properly ordered by likes and creation date"""
        # Create questions with different like counts and dates
        question1 = Question.objects.create(
            event=self.event,
            author=self.user1,
            text='Question 1'
        )
        question2 = Question.objects.create(
            event=self.event,
            author=self.user2,
            text='Question 2'
        )
        
        # Add likes to question2 (more likes)
        question2.likes.add(self.user1, self.user2)
        
        request = self.factory.get('/events/detail/')
        request.user = self.user1
        
        result = services.get_event_detail_data(request, self.event.code)
        
        questions = list(result['questions'])
        # Question with more likes should come first
        self.assertEqual(questions[0], question2)
        self.assertEqual(questions[1], question1)

    def test_poll_vote_counting(self):
        """Test that poll vote counting works correctly"""
        # Create votes
        PollVote.objects.create(user=self.user1, poll_option=self.poll_option1)
        PollVote.objects.create(user=self.user2, poll_option=self.poll_option1)
        PollVote.objects.create(user=self.user1, poll_option=self.poll_option2)
        
        request = self.factory.get('/events/poll/detail/')
        request.user = self.user1
        
        result = services.get_poll_detail_data(request, self.event.code, self.poll.id)
        
        option_votes_list = result['option_votes_list']
        
        # Find option1 votes
        option1_votes = next((count for option, count in option_votes_list if option == self.poll_option1), 0)
        option2_votes = next((count for option, count in option_votes_list if option == self.poll_option2), 0)
        
        self.assertEqual(option1_votes, 2)  # user1 and user2 voted
        self.assertEqual(option2_votes, 1)  # only user1 voted
