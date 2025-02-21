import json
from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from booking.models import Booking, BookingChangeRequest, BookingCancellationRequest
from core.models import Campervan
import stripe

class StripePaymentTest(TestCase):
    def setUp(self):
        # Create a test user and log them in
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")
        
        # Create a campervan instance for the test
        self.campervan = Campervan.objects.create(
            name="Test Campervan",
            description="A perfect vehicle for your trip.",
            price_per_day=100.00,
            image="test_image.jpg",
            capacity=4,
            location="Test Location",
            brand="TestBrand",
            model="TestModel"
        )
        
        # Create a pending booking instance for the test user and campervan
        self.booking = Booking.objects.create(
            user=self.user,
            campervan=self.campervan,
            start_date=date.today() + timedelta(days=5),  # Booking starts 5 days from today
            end_date=date.today() + timedelta(days=10),  # Booking ends 10 days from today
            total_price=500.00,  # Total price for the booking
            status="Pending"  # Initial status of the booking
        )

    @patch('booking.views.stripe.checkout.Session.create')
    def test_create_checkout_session(self, mock_stripe_session_create):
        """
        Test the create_checkout_session view.
        This test verifies that the create_checkout_session view:
        - Returns a 302 redirect to Stripe's checkout page.
        - The redirect URL starts with 'http://stripe.test/checkout'.
        - Passes metadata to Stripe containing the booking id.
        """
        #  mock_stripe_session_create (Mock): Mock object for Stripe's session creation.
        mock_stripe_session_create.return_value = type('obj', (object,), {
            'url': 'http://stripe.test/checkout',
            'id': 'cs_test_dummy'
        })
        
        url = reverse('create_checkout_session', args=[self.booking.id])
        response = self.client.get(url)
        
        # Expect a 303 redirect to the Stripe checkout page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('http://stripe.test/checkout'))
        
        # Verify that the metadata passed to Stripe contains the correct booking id
        _, kwargs = mock_stripe_session_create.call_args
        self.assertEqual(str(kwargs['metadata']['booking_id']), str(self.booking.id))
    
    def test_create_checkout_session_invalid_status(self):
        """
        Ensure that the view redirects to the booking details page if the booking status is not pending.
        """
        self.booking.status = "Confirmed"
        self.booking.save()
        
        url = reverse('create_checkout_session', args=[self.booking.id])
        response = self.client.get(url)
        self.assertRedirects(response, reverse('booking_details', args=[self.booking.id]))
    
    @patch('booking.views.send_mail')
    def test_stripe_webhook_updates_booking_status(self, mock_send_mail):
        """
        Verify that the booking status is updated to 'Confirmed' when a checkout.session.completed event is received.
        """
        # Simulate a Stripe event payload with the booking id in metadata.
        event_payload = {
            'id': 'evt_test',
            'object': 'event',
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_dummy',
                    'metadata': {'booking_id': str(self.booking.id)}
                }
            }
        }
        payload = json.dumps(event_payload)
        sig_header = 'test_sig'
        
        # Mock the Stripe webhook event constructor to return the simulated event payload
        with patch('booking.views.stripe.Webhook.construct_event') as mock_construct:
            mock_construct.return_value = event_payload
            url = reverse('stripe_webhook')
            response = self.client.post(url, data=payload, content_type='application/json', HTTP_STRIPE_SIGNATURE=sig_header)
            self.assertEqual(response.status_code, 200)
        
        # Reload the booking from the database and check the status
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "Confirmed")
    
    @patch('booking.views.stripe.Webhook.construct_event')
    def test_stripe_webhook_invalid_payload(self, mock_construct):
        """
        Ensure the webhook returns a 400 status code when given an invalid payload.
        """
        mock_construct.side_effect = ValueError("Invalid payload")
        url = reverse('stripe_webhook')
        response = self.client.post(url, data="{}", content_type="application/json", HTTP_STRIPE_SIGNATURE="test")
        self.assertEqual(response.status_code, 400)
    
    @patch('booking.views.stripe.Webhook.construct_event')
    def test_stripe_webhook_invalid_signature(self, mock_construct):
        """
        Ensure the webhook returns a 400 status code when the signature verification fails.
        """
        from stripe.error import SignatureVerificationError
        mock_construct.side_effect = SignatureVerificationError("Invalid signature", None)
        url = reverse('stripe_webhook')
        response = self.client.post(url, data="{}", content_type="application/json", HTTP_STRIPE_SIGNATURE="test")
        self.assertEqual(response.status_code, 400)

    @patch('booking.views.stripe.checkout.Session.create')
    def test_create_checkout_session_block_for_past_booking(self, mock_stripe_session_create):
        """
        Ensure that a booking with a start date in the past is blocked from processing payment.
        """
        # Set booking start date in the past.
        self.booking.start_date = date.today() - timedelta(days=2)
        self.booking.end_date = date.today() + timedelta(days=2)
        self.booking.save()
        
        url = reverse('create_checkout_session', args=[self.booking.id])
        # Expect that the view prevents creating a checkout session (and thus no Stripe call)
        response = self.client.get(url, follow=True)
        
        # The Stripe session creation should not be called
        mock_stripe_session_create.assert_not_called()
        # Expect redirection to booking details page with an error message
        self.assertRedirects(response, reverse('booking_details', args=[self.booking.id]))
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("ongoing or in the past" in str(message).lower() for message in messages))
    
    @patch('booking.views.stripe.checkout.Session.create')
    def test_create_checkout_session_block_for_ongoing_booking(self, mock_stripe_session_create):
        """
        Ensure that a booking with a start date equal to today (ongoing booking) is blocked from processing payment.
        """
        # Set booking start date to today.
        self.booking.start_date = date.today()
        self.booking.end_date = date.today() + timedelta(days=3)
        self.booking.save()
        
        url = reverse('create_checkout_session', args=[self.booking.id])
        response = self.client.get(url, follow=True)
        
        mock_stripe_session_create.assert_not_called()
        self.assertRedirects(response, reverse('booking_details', args=[self.booking.id]))
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("ongoing or in the past" in str(message).lower() for message in messages))