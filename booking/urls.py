from django.urls import path
from .views import (
    book_campervan,
    check_availability,
    cancel_booking,
    check_booking_status,
    booking_confirmation,
    booking_details,
    edit_booking,
    request_date_change,
    view_change_requests,
    approve_change_request,
    reject_change_request,
    request_cancellation,
    create_checkout_session,
    payment_success,
    payment_cancel,
    stripe_webhook,
)

urlpatterns = [
    path("book/<int:campervan_id>/", book_campervan, name="book_campervan"),
    path("check-availability/", check_availability, name="check_availability"),
    path("cancel/<int:booking_id>/", cancel_booking, name="cancel_booking"),
    path(
        "status/<int:booking_id>/",
        check_booking_status,
        name="check_booking_status",
    ),
    path(
        "booking-confirmation/<int:booking_id>/",
        booking_confirmation,
        name="booking_confirmation",
    ),
    path(
        "booking_details/<int:booking_id>/",
        booking_details,
        name="booking_details",
    ),
    path(
        "cancel_booking/<int:booking_id>/",
        cancel_booking,
        name="cancel_booking",
    ),
    path("edit/<int:booking_id>/", edit_booking, name="edit_booking"),
    path(
        "request_date_change/<int:booking_id>/",
        request_date_change,
        name="request_date_change",
    ),
    path(
        "change_requests/", view_change_requests, name="view_change_requests"
    ),
    path(
        "change_requests/<int:request_id>/approve/",
        approve_change_request,
        name="approve_change_request",
    ),
    path(
        "change_requests/<int:request_id>/reject/",
        reject_change_request,
        name="reject_change_request",
    ),
    path(
        "request_cancellation/<int:booking_id>/",
        request_cancellation,
        name="request_cancellation",
    ),
    path(
        "create-checkout-session/<int:booking_id>/",
        create_checkout_session,
        name="create_checkout_session",
    ),
    path("payment_success/", payment_success, name="payment_success"),
    path("payment_cancel/", payment_cancel, name="payment_cancel"),
    path("stripe-webhook/", stripe_webhook, name="stripe_webhook"),
]
