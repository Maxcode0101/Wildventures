from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from booking.models import (
    Booking,
    BookingChangeRequest,
    BookingCancellationRequest,
)
from core.models import Campervan
from datetime import date, timedelta


class CancelBookingTest(TestCase):
    def setUp(self):
        # Test user
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
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

        # Refresh booking from the db
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "Cancelled")
        self.assertRedirects(response, reverse("my_bookings"))
        messages = list(response.wsgi_request._messages)
        # Check that the message contains "cancelled" and "successfully"
        self.assertTrue(
            any(
                "cancelled" in str(message).lower()
                and "successfully" in str(message).lower()
                for message in messages
            )
        )

    def test_cancel_past_booking(self):
        """Test that a user cannot cancel a booking in the past."""
        self.booking.start_date = date.today() - timedelta(days=10)
        self.booking.end_date = date.today() - timedelta(days=5)
        self.booking.save()

        url = reverse("cancel_booking", args=[self.booking.id])
        response = self.client.post(url, follow=True)

        self.booking.refresh_from_db()
        # Booking should remain Pending as it can't be cancelled in the past.
        self.assertEqual(self.booking.status, "Pending")
        messages = list(response.wsgi_request._messages)
        self.assertTrue(
            any(
                "already ended" in str(message).lower() for message in messages
            )
        )

    def test_cancel_already_canceled_booking(self):
        """Test that a user can't' cancel a booking
        that is already canceled."""
        self.booking.status = "Cancelled"
        self.booking.save()

        url = reverse("cancel_booking", args=[self.booking.id])
        response = self.client.post(url, follow=True)

        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "Cancelled")
        messages = list(response.wsgi_request._messages)
        # Check that the message contains "already cancelled"
        self.assertTrue(
            any(
                "already cancelled" in str(message).lower()
                for message in messages
            )
        )


class DateChangeTest(TestCase):
    def setUp(self):
        # Create test user and log them in
        self.user = User.objects.create_user(
            username="datechanger", password="password123"
        )
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
        """Test that a booking can be updated via self service."""
        new_start = date.today() + timedelta(days=11)
        new_end = date.today() + timedelta(days=16)
        response = self.client.post(
            reverse("edit_booking", args=[self.booking.id]),
            {
                "start_date": new_start.strftime("%Y-%m-%d"),
                "end_date": new_end.strftime("%Y-%m-%d"),
            },
            follow=True,
        )
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.start_date, new_start)
        self.assertEqual(self.booking.end_date, new_end)
        expected_price = (
            new_end - new_start
        ).days * self.campervan.price_per_day
        self.assertEqual(self.booking.total_price, expected_price)
        self.assertRedirects(response, reverse("my_bookings"))

    def test_edit_booking_invalid_dates(self):
        """Test that booking can't be updated if end date < start date."""
        new_start = date.today() + timedelta(days=16)
        new_end = date.today() + timedelta(days=11)
        response = self.client.post(
            reverse("edit_booking", args=[self.booking.id]),
            {
                "start_date": new_start.strftime("%Y-%m-%d"),
                "end_date": new_end.strftime("%Y-%m-%d"),
            },
            follow=True,
        )
        self.booking.refresh_from_db()
        # Booking dates should remain unchanged
        self.assertNotEqual(self.booking.start_date, new_start)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(
            any(
                "end date must be after start date" in str(message).lower()
                for message in messages
            )
        )

    def test_edit_booking_overlapping(self):
        """Test that a pending booking can't
        be updated if the new dates overlap
        with another active booking."""
        # Create another booking that overlaps with the proposed new dates.
        other_booking = Booking.objects.create(
            user=self.user,
            campervan=self.campervan,
            start_date=date.today() + timedelta(days=12),
            end_date=date.today() + timedelta(days=14),
            total_price=200.00,
            status="Confirmed",
        )
        new_start = date.today() + timedelta(days=11)
        new_end = date.today() + timedelta(days=16)
        response = self.client.post(
            reverse("edit_booking", args=[self.booking.id]),
            {
                "start_date": new_start.strftime("%Y-%m-%d"),
                "end_date": new_end.strftime("%Y-%m-%d"),
            },
            follow=True,
        )
        messages = list(response.wsgi_request._messages)
        self.assertTrue(
            any(
                "not available" in str(message).lower() for message in messages
            )
        )

    def test_request_date_change_for_confirmed_booking(self):
        """Test that a user can request
        a date change for a confirmed booking."""
        self.booking.status = "Confirmed"
        self.booking.save()
        new_start = date.today() + timedelta(days=20)
        new_end = date.today() + timedelta(days=25)
        response = self.client.post(
            reverse("request_date_change", args=[self.booking.id]),
            {
                "start_date": new_start.strftime("%Y-%m-%d"),
                "end_date": new_end.strftime("%Y-%m-%d"),
            },
            follow=True,
        )
        self.assertRedirects(response, reverse("my_bookings"))
        self.assertTrue(
            self.booking.change_requests.filter(
                requested_start_date=new_start, requested_end_date=new_end
            ).exists()
        )


class AdminActionTest(TestCase):
    def setUp(self):
        # Create a staff user and log them in.
        self.staff = User.objects.create_user(
            username="admin", password="adminpass"
        )
        self.staff.is_staff = True
        self.staff.save()
        self.client.force_login(self.staff)

        # Create a normal user.
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )

        # Create a test campervan.
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

        # Create a confirmed booking for the normal user.
        self.booking = Booking.objects.create(
            user=self.user,
            campervan=self.campervan,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=10),
            total_price=500.00,
            status="Confirmed",
        )

        # Create a pending date change request for that booking.
        self.bcr = self.booking.change_requests.create(
            requested_start_date=date.today() + timedelta(days=7),
            requested_end_date=date.today() + timedelta(days=12),
            status="Pending",
        )

        # Create a pending cancellation request for that booking.
        self.cancellation_request = self.booking.cancellation_requests.create(
            status="Pending"
        )

    def test_approve_date_change_request(self):
        """Test that an admin can approve a
        date change request and update
        the booking accordingly."""
        url = reverse("approve_change_request", args=[self.bcr.id])
        response = self.client.get(url)
        self.booking.refresh_from_db()
        self.bcr.refresh_from_db()
        self.assertEqual(
            self.booking.start_date, self.bcr.requested_start_date
        )
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
        """Test that an admin can approve a cancellation request
        and that the booking becomes cancelled."""
        self.cancellation_request.status = "Approved"
        self.cancellation_request.save()
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "Cancelled")

    def test_reject_cancellation_request(self):
        """Test that an admin can reject a cancellation request
        and that the booking remains confirmed."""
        self.cancellation_request.status = "Rejected"
        self.cancellation_request.save()
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "Confirmed")


#####################
# Email confirmations
#####################


def send_booking_confirmation_email(booking):
    """
    Sends confirmation email on sucessfull bookings
    """
    subject = "Booking Confirmation"
    message = (
        f"Dear {booking.user.username},\n\n"
        f"Your booking for {booking.campervan.name} is confirmed.\n"
        f"Start Date: {booking.start_date}\n"
        f"End Date: {booking.end_date}\n"
        f"Total Price: ${booking.total_price:.2f}\n\n"
        f"Thank you for choosing Us!\n\n"
        f"Best regards\n\n"
        f"Your Wildventures Team"
    )

    send_mail(
        subject,
        message,
        "no-reply@wildventures.com",
        [booking.user.email],
        fail_silently=False,
    )


def send_cancellation_email(booking):
    """
    Sends confirmation email on cancelled bookings
    """
    subject = "Booking Cancellation"
    message = (
        f"Dear {booking.user.username},\n\n"
        f"Your booking for {booking.campervan.name} from {booking.start_date} to {booking.end_date} for ${booking.total_price:.2f} has been cancelled.\n"  # noqa
        f"Thank you for your visit, we hope to see you soon again.\n\n"
        f"Best regards\n\n"
        f"Your Wildventures Team"
    )

    send_mail(
        subject,
        message,
        "no-reply@wildventures.com",
        [booking.user.email],
        fail_silently=False,
    )


def send_booking_changed_email(booking):
    """
    Email confirmation after user changed booking via self service
    """
    subject = "Your booking has been sucessfully updated"
    message = (
        f"Dear {booking.user.username},\n\n"
        f"Your booking for {booking.campervan.name} has been updated.\n"
        f"New Start Date: {booking.start_date}\n"
        f"New End Date: {booking.end_date}\n"
        f"New Total Price: ${booking.total_price:.2f}\n\n"
        f"Thank you for your visit, we hope to see you soon again.\n\n"
        f"Best regards\n\n"
        f"Your Wildventures Team"
    )

    send_mail(
        subject,
        message,
        "no-reply@wildventures.com",
        [booking.user.email],
        fail_silently=False,
    )


def send_date_change_request_received_email(booking, bcr):
    """
    Inform user that date change request needs admin approval
    """
    subject = "Date change request received"
    message = (
        f"Dear {booking.user.username},\n\n"
        f"We have received your date-change request for Booking #{booking.id}.\n"  # noqa
        f"Requested Start: {bcr.requested_start_date}\n"
        f"Requested End: {bcr.requested_end_date}\n\n"
        f"Our team will review your request and notify you once it's approved or rejected."  # noqa
    )

    send_mail(
        subject,
        message,
        "no-reply@wildventures.com",
        [booking.user.email],
        fail_silently=False,
    )


def send_date_change_request_notification_to_admin(booking, bcr):
    """
    Notification for admin about pending date change request
    """
    admin_email = getattr(settings, "DEFAULT_ADMIN_EMAIL", None)
    if not admin_email:
        return

    subject = (
        f"New date change request is awaiting approval (Booking #{booking.id})"
    )
    message = (
        f"Hello Admin, \n\n"
        f"User {booking.user.username} is requesting a date change for Booking #{booking.id}.\n"  # noqa
        f"Requested Start: {bcr.requested_start_date}\n"
        f"Requested End: {bcr.requested_end_date}\n\n"
        f"Please review this request in the admin panel."
    )

    send_mail(
        subject,
        message,
        "no-reply@wildventures.com",
        [booking.user.email],
        fail_silently=False,
    )


def send_change_approval_email(booking, bcr):

    subject = "Your Date Change Request Was Approved"
    message = (
        f"Dear {booking.user.username},\n\n"
        f"Your date change request for Booking #{booking.id} has been approved.\n"  # noqa
        f"Here are your updated booking details:\n"
        f"Campervan: {booking.campervan.name}\n"
        f"New Start Date: {booking.start_date.strftime('%Y-%m-%d')}\n"
        f"New End Date: {booking.end_date.strftime('%Y-%m-%d')}\n"
        f"New Total Price: ${booking.total_price:.2f}\n\n"
        f"Thank you for booking with us!"
        f"Best regards,\n"
        f"Your Wildventures Team"
    )

    send_mail(
        subject,
        message,
        "no-reply@wildventures.com",
        [booking.user.email],
        fail_silently=False,
    )


def send_change_rejection_email(booking, bcr):

    subject = "Your Date Change Request Was Rejected"
    message = (
        f"Dear {booking.user.username},\n\n"
        f"Your date change request for Booking #{booking.id} has been rejected.\n"  # noqa
        f"Your booking remains as follows:\n"
        f"Campervan: {booking.campervan.name}\n"
        f"Start Date: {booking.start_date.strftime('%Y-%m-%d')}\n"
        f"End Date: {booking.end_date.strftime('%Y-%m-%d')}\n"
        f"Total Price: ${booking.total_price:.2f}\n\n"
        f"In case you need further assistance, please contact our service team."  # noqa
        f"Best regards,\n"
        f"Your Wildventures Team"
    )

    send_mail(
        subject,
        message,
        "no-reply@wildventures.com",
        [booking.user.email],
        fail_silently=False,
    )


def send_cancellation_approval_email(booking, cancellation_request):
    """
    Email confirmation for the user if cancellation request
    has been approved by admin
    """
    subject = "Your cancelation request has been approved"
    message = (
        f"Dear {booking.user.username},\n\n"
        f"your cancellation request for Booking #{booking.id} has been approved.\n"  # noqa
        f"Your booking is now cancelled.\n\n"
        f"Thank you for your visit. We hope to see you soon again\n\n"
        f"Best regards,\n\n"
        f"Your Wildventures Team"
    )

    send_mail(
        subject,
        message,
        "no-reply@wildventures.com",
        [booking.user.email],
        fail_silently=False,
    )


def send_cancellation_rejection_email(booking, cancellation_request):
    """
    Email confirmation for the user if cancellation request
    has been rejected by admin
    """
    subject = "Your cancelation request has been rejected"
    message = (
        f"Dear {booking.user.username},\n\n"
        f"Your cancellation request for Booking #{booking.id} has been rejected.\n"  # noqa
        f"Your booking remains confirmed.\n\n"
        f"In case you need further assistance, please contact our service team.\n\n"  # noqa
        f"Best regards,\n\n"
        f"Your Wildventures Team"
    )

    send_mail(
        subject,
        message,
        "no-reply@wildventures.com",
        [booking.user.email],
        fail_silently=False,
    )


def send_cancellation_request_notification_to_admin(
    booking, cancellation_request
):
    """
    Notify Admin about pending cancellation request
    """
    admin_email = getattr(settings, "DEFAULT_ADMIN_EMAIL", None)
    if admin_email:
        subject = f"Cancellation Request for Booking #{booking.id}"
        message = (
            f"User {booking.user.username} is requesting cancellation for Booking #{booking.id}.\n"  # noqa
            "Please review this request in the admin dashboard."
        )
        send_mail(
            subject,
            message,
            "no-reply@wildventures.com",
            [admin_email],
            fail_silently=False,
        )


#################
# Edge case tests
#################


class EdgeCaseTest(TestCase):
    def setUp(self):
        # Create two test users.
        self.user1 = User.objects.create_user(
            username="user1", password="pass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="pass123"
        )

        # Create a test campervan.
        self.campervan = Campervan.objects.create(
            name="EdgeCase Campervan",
            description="Campervan for edge case testing.",
            price_per_day=100.00,
            image="edge_test.jpg",
            capacity=4,
            location="Edge Location",
            brand="Edge Brand",
            model="Edge Model",
            availability_status=True,
        )

    def test_invalid_date_format_on_booking_creation(self):
        """
        Test that attempting to book with an invalid date format returns an error.  # noqa
        """
        # Log in as user1.
        self.client.login(username="user1", password="pass123")
        url = reverse("book_campervan", args=[self.campervan.id])
        # Pass an invalid date format for start_date.
        response = self.client.post(
            url,
            {
                "start_date": "invalid-date",
                "end_date": (date.today() + timedelta(days=10)).strftime(
                    "%Y-%m-%d"
                ),
            },
        )
        self.assertContains(response, "Invalid date format.", status_code=200)

    def test_overlapping_bookings_across_multiple_users(self):
        """
        Test that if one user has an active booking,
        another user cannot create an overlapping booking.
        """
        # Log in as user1 and create a booking.
        self.client.login(username="user1", password="pass123")
        start_date = date.today() + timedelta(days=5)
        end_date = start_date + timedelta(days=5)
        url = reverse("book_campervan", args=[self.campervan.id])
        response1 = self.client.post(
            url,
            {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
            },
            follow=True,
        )
        # Verify the booking was created.
        booking1 = self.campervan.bookings.get(user=self.user1)
        self.assertEqual(booking1.status, "Pending")

        # Log in as user2 and try to create an overlapping booking.
        self.client.logout()
        self.client.login(username="user2", password="pass123")
        overlapping_start = start_date + timedelta(days=2)
        overlapping_end = end_date + timedelta(days=2)
        response2 = self.client.post(
            url,
            {
                "start_date": overlapping_start.strftime("%Y-%m-%d"),
                "end_date": overlapping_end.strftime("%Y-%m-%d"),
            },
        )
        # The view should return an error about availability.
        self.assertContains(
            response2,
            "The campervan is not available for the selected dates.",
            status_code=200,
        )

    def test_non_overlapping_bookings_across_multiple_users(self):
        """
        Test that two users can book the same campervan
        if their dates do not overlap.
        """
        # Log in as user1 and create a booking.
        self.client.login(username="user1", password="pass123")
        start_date1 = date.today() + timedelta(days=5)
        end_date1 = start_date1 + timedelta(days=5)
        url = reverse("book_campervan", args=[self.campervan.id])
        response1 = self.client.post(
            url,
            {
                "start_date": start_date1.strftime("%Y-%m-%d"),
                "end_date": end_date1.strftime("%Y-%m-%d"),
            },
            follow=True,
        )
        booking1 = self.campervan.bookings.get(user=self.user1)
        self.assertEqual(booking1.status, "Pending")

        # Log in as user2 and try to create a booking that does not overlap.
        self.client.logout()
        self.client.login(username="user2", password="pass123")
        # For example, a booking starting after user1's booking ends.
        start_date2 = end_date1 + timedelta(days=1)
        end_date2 = start_date2 + timedelta(days=5)
        response2 = self.client.post(
            url,
            {
                "start_date": start_date2.strftime("%Y-%m-%d"),
                "end_date": end_date2.strftime("%Y-%m-%d"),
            },
            follow=True,
        )
        # Verify that booking creation succeeded
        # by checking for a redirect to the confirmation page.
        self.assertEqual(response2.status_code, 200)
        booking2 = self.campervan.bookings.get(user=self.user2)
        self.assertEqual(booking2.status, "Pending")


class OngoingBookingTest(TestCase):
    def setUp(self):
        # Create test user and log them in
        self.user = User.objects.create_user(
            username="ongoinguser", password="password123"
        )
        self.client.login(username="ongoinguser", password="password123")
        # Create test campervan
        self.campervan = Campervan.objects.create(
            name="Ongoing Campervan",
            description="Campervan for ongoing booking testing.",
            price_per_day=100.00,
            image="test_image.jpg",
            capacity=4,
            location="Test Location",
            brand="Test Brand",
            model="Test Model",
            availability_status=True,
        )
        # Create an ongoing booking
        # (start date in the past, end date in the future)
        self.booking = Booking.objects.create(
            user=self.user,
            campervan=self.campervan,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=1),
            total_price=200.00,
            status="Pending",
        )

    def test_cancel_ongoing_booking(self):
        """Test that a user cannot cancel an ongoing booking."""
        url = reverse("cancel_booking", args=[self.booking.id])
        response = self.client.post(url, follow=True)
        self.booking.refresh_from_db()
        # The booking should remain unchanged
        # (still Pending) because it is ongoing.
        self.assertEqual(self.booking.status, "Pending")
        messages = list(response.wsgi_request._messages)
        self.assertTrue(
            any(
                "cannot be cancelled" in str(message).lower()
                or "ongoing" in str(message).lower()
                for message in messages
            )
        )

    def test_request_date_change_ongoing_booking(self):
        """Test that a user can't request a date change for an ongoing booking."""  # noqa
        url = reverse("request_date_change", args=[self.booking.id])
        new_start = date.today() + timedelta(days=1)
        new_end = date.today() + timedelta(days=3)
        response = self.client.post(
            url,
            {
                "start_date": new_start.strftime("%Y-%m-%d"),
                "end_date": new_end.strftime("%Y-%m-%d"),
            },
            follow=True,
        )
        self.booking.refresh_from_db()
        # No new BookingChangeRequest should have been created
        # for an ongoing booking.
        self.assertFalse(self.booking.change_requests.exists())
        messages = list(response.wsgi_request._messages)
        self.assertTrue(
            any(
                "ongoing or past booking" in str(message).lower()
                for message in messages
            )
        )
