from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from booking.models import Booking
from core.models import Campervan
from datetime import date, timedelta

class CancelBookingTest(TestCase):
    def setUp(self):
        # Test user
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")

        # Test campervan
        self.campervan = Campervan.objects.create(
            name="Test Campervan",
            description="Perfect for cross-country journey's.",
            price_per_day=100.00,
            image="test_image.jpg",
            capacity=4,
            location="Test Location",
            brand="Test Brand",
            model="Test Model",
            availability_status=True,
        )

        # Test booking
        self.booking = Booking.objects.create(
            user=self.user,
            campervan=self.campervan,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=10),
            total_price=500.00,
            status="Pending",
        )

    def test_cancel_booking(self):
        """Test that a user can cancel a booking successfully."""
        url = reverse("cancel_booking", args=[self.booking.id])
        response = self.client.post(url)

        # Get a booking from the db and refresh it
        self.booking.refresh_from_db()

        # Check if booking status = "Canceled"
        self.assertEqual(self.booking.status, "Canceled")

        # Check if redirection of the user to "My Bookings" works proper
        self.assertRedirects(response, reverse("my_bookings"))

        # Check if displaying the success message works proper
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("successfully canceled" in str(message) for message in messages))

    def test_cancel_past_booking(self):
        """Test that a user cannot cancel a booking in the past."""
        self.booking.start_date = date.today() - timedelta(days=10)
        self.booking.end_date = date.today() - timedelta(days=5)
        self.booking.save()

        url = reverse("cancel_booking", args=[self.booking.id])
        response = self.client.post(url)

        # Refresh the booking from the db
        self.booking.refresh_from_db()

        # Check if the booking status is still "Pending"
        self.assertEqual(self.booking.status, "Pending")

        # Check if displaying an error message works proper
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("already ended" in str(message) for message in messages))

    def test_cancel_already_canceled_booking(self):
        """Test that a user cannot cancel a booking that is already canceled."""
        self.booking.status = "Canceled"
        self.booking.save()

        url = reverse("cancel_booking", args=[self.booking.id])
        response = self.client.post(url)

        # Refresh the booking from the db
        self.booking.refresh_from_db()

        # Check if the booking status is still "Canceled"
        self.assertEqual(self.booking.status, "Canceled")

        # Check if displaying an error message works proper
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("already been canceled" in str(message) for message in messages))