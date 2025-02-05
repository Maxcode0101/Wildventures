from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from booking.models import Booking, BookingChangeRequest, BookingCancellationRequest
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
        response = self.client.post(url, follow=True)

        # Get a booking from the db and refresh it
        self.booking.refresh_from_db()

        # Check if booking status = "Cancelled"
        self.assertEqual(self.booking.status, "Cancelled")

        # Check if redirection of the user to "My Bookings" works proper
        self.assertRedirects(response, reverse("my_bookings"))

        # Check if displaying the success message works proper
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("successfully canceled" in str(message).lower() for message in messages)
                        or any("successfully cancelled" in str(message).lower() for message in messages))

    def test_cancel_past_booking(self):
        """Test that a user cannot cancel a booking in the past."""
        self.booking.start_date = date.today() - timedelta(days=10)
        self.booking.end_date = date.today() - timedelta(days=5)
        self.booking.save()

        url = reverse("cancel_booking", args=[self.booking.id])
        response = self.client.post(url, follow=True)

        # Refresh the booking from the db
        self.booking.refresh_from_db()

        # Check if the booking status is still "Pending"
        self.assertEqual(self.booking.status, "Pending")

        # Check if displaying an error message works proper
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("already ended" in str(message).lower() for message in messages))

    def test_cancel_already_canceled_booking(self):
        """Test that a user cannot cancel a booking that is already canceled."""
        self.booking.status = "Cancelled"
        self.booking.save()

        url = reverse("cancel_booking", args=[self.booking.id])
        response = self.client.post(url, follow=True)

        # Refresh the booking from the db
        self.booking.refresh_from_db()

        # Check if the booking status is still "Cancelled"
        self.assertEqual(self.booking.status, "Cancelled")

        # Check if displaying an error message works proper
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("already been canceled" in str(message).lower() or 
                            "already been cancelled" in str(message).lower() for message in messages))


class DateChangeTest(TestCase):
    def setUp(self):
        # Create test user and log them in
        self.user = User.objects.create_user(username="datechanger", password="password123")
        self.client.login(username="datechanger", password="password123")
        # Create test campervan
        self.campervan = Campervan.objects.create(
            name="Date Change Campervan",
            description="A campervan for date change testing.",
            price_per_day=100.00,
            image="test_image.jpg",
            capacity=4,
            location="Test Location",
            brand="Test Brand",
            model="Test Model",
            availability_status=True,
        )
        # Create a pending booking for date change tests
        self.booking = Booking.objects.create(
            user=self.user,
            campervan=self.campervan,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
            total_price=500.00,
            status="Pending",
        )

    def test_edit_booking_success(self):
        """Test that a pending booking can be updated with new valid dates via self service."""
        new_start = date.today() + timedelta(days=11)
        new_end = date.today() + timedelta(days=16)
        response = self.client.post(reverse("edit_booking", args=[self.booking.id]), {
            "start_date": new_start.strftime("%Y-%m-%d"),
            "end_date": new_end.strftime("%Y-%m-%d")
        }, follow=True)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.start_date, new_start)
        self.assertEqual(self.booking.end_date, new_end)
        expected_price = (new_end - new_start).days * self.campervan.price_per_day
        self.assertEqual(self.booking.total_price, expected_price)
        self.assertRedirects(response, reverse("my_bookings"))

    def test_edit_booking_invalid_dates(self):
        """Test that a pending booking cannot be updated if the end date is before the start date."""
        new_start = date.today() + timedelta(days=16)
        new_end = date.today() + timedelta(days=11)
        response = self.client.post(reverse("edit_booking", args=[self.booking.id]), {
            "start_date": new_start.strftime("%Y-%m-%d"),
            "end_date": new_end.strftime("%Y-%m-%d")
        }, follow=True)
        self.booking.refresh_from_db()
        # Booking dates should remain unchanged
        self.assertNotEqual(self.booking.start_date, new_start)
        self.assertContains(response, "End date must be after start date.")

    def test_edit_booking_overlapping(self):
        """Test that a pending booking cannot be updated if the new dates overlap with another active booking."""
        # Create another booking that overlaps with the proposed new dates
        other_booking = Booking.objects.create(
            user=self.user,
            campervan=self.campervan,
            start_date=date.today() + timedelta(days=12),
            end_date=date.today() + timedelta(days=14),
            total_price=200.00,
            status="Confirmed"
        )
        new_start = date.today() + timedelta(days=11)
        new_end = date.today() + timedelta(days=16)
        response = self.client.post(reverse("edit_booking", args=[self.booking.id]), {
            "start_date": new_start.strftime("%Y-%m-%d"),
            "end_date": new_end.strftime("%Y-%m-%d")
        }, follow=True)
        self.assertContains(response, "This campervan is not available for the requested dates.")

    def test_request_date_change_for_confirmed_booking(self):
        """Test that a user can request a date change for a confirmed booking."""
        # Change booking status to Confirmed
        self.booking.status = "Confirmed"
        self.booking.save()
        new_start = date.today() + timedelta(days=20)
        new_end = date.today() + timedelta(days=25)
        response = self.client.post(reverse("request_date_change", args=[self.booking.id]), {
            "start_date": new_start.strftime("%Y-%m-%d"),
            "end_date": new_end.strftime("%Y-%m-%d")
        }, follow=True)
        self.assertRedirects(response, reverse("my_bookings"))
        # Check that a BookingChangeRequest was created
        self.assertTrue(self.booking.change_requests.filter(requested_start_date=new_start,
                                                            requested_end_date=new_end).exists())


class AdminActionTest(TestCase):
    def setUp(self):
        # Create a staff user and log them in
        self.staff = User.objects.create_user(username="admin", password="adminpass")
        self.staff.is_staff = True
        self.staff.save()
        self.client.force_login(self.staff)

        # Create a normal user
        self.user = User.objects.create_user(username="testuser", password="password123")

        # Create a test campervan
        self.campervan = Campervan.objects.create(
            name="Admin Test Campervan",
            description="Admin test campervan.",
            price_per_day=100.00,
            image="test_image.jpg",
            capacity=4,
            location="Admin Test Location",
            brand="Test Brand",
            model="Test Model",
            availability_status=True,
        )

        # Create a confirmed booking for the normal user
        self.booking = Booking.objects.create(
            user=self.user,
            campervan=self.campervan,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=10),
            total_price=500.00,
            status="Confirmed",
        )

        # Create a pending date change request for that booking
        self.bcr = self.booking.change_requests.create(
            requested_start_date=date.today() + timedelta(days=7),
            requested_end_date=date.today() + timedelta(days=12),
            status="Pending"
        )

        # Create a pending cancellation request for that booking
        self.cancellation_request = self.booking.cancellation_requests.create(
            status="Pending"
        )

    def test_approve_date_change_request(self):
        """Test that an admin can approve a date change request and update the booking accordingly."""
        url = reverse("approve_change_request", args=[self.bcr.id])
        response = self.client.get(url)
        self.booking.refresh_from_db()
        self.bcr.refresh_from_db()
        self.assertEqual(self.booking.start_date, self.bcr.requested_start_date)
        self.assertEqual(self.booking.end_date, self.bcr.requested_end_date)
        self.assertEqual(self.bcr.status, "Approved")
        self.assertRedirects(response, reverse("view_change_requests"))

    def test_reject_date_change_request(self):
        """Test that an admin can reject a date change request."""
        url = reverse("reject_change_request", args=[self.bcr.id])
        response = self.client.get(url)
        self.bcr.refresh_from_db()
        self.assertEqual(self.bcr.status, "Rejected")
        self.assertRedirects(response, reverse("view_change_requests"))

    def test_approve_cancellation_request(self):
        """Test that an admin can approve a cancellation request and that the booking becomes cancelled."""
        # Simulate admin approval via admin view by calling the admin override
        # For this test, we simulate by updating the cancellation request via admin logic.
        url = reverse("admin:booking_bookingcancellationrequest_change", args=[self.cancellation_request.id])
        # Prepare data with status Approved
        data = {
            "booking": self.booking.id,
            "status": "Approved",
        }
        response = self.client.post(url, data, follow=True)
        self.booking.refresh_from_db()
        self.cancellation_request.refresh_from_db()
        self.assertEqual(self.booking.status, "Cancelled")
        # You might also check for a success message if desired.

    def test_reject_cancellation_request(self):
        """Test that an admin can reject a cancellation request and that the booking remains confirmed."""
        url = reverse("admin:booking_bookingcancellationrequest_change", args=[self.cancellation_request.id])
        data = {
            "booking": self.booking.id,
            "status": "Rejected",
        }
        response = self.client.post(url, data, follow=True)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "Confirmed")

