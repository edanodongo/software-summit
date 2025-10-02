from rest_framework import serializers
from .models import (
    Event, Track, Session,
    Speaker, Exhibitor, Sponsor,
    Registration, Ticket, Order, Payment,
    ConnectionRequest, ChatMessage,
    Poll, PollOption, PollResponse,
    Question, Feedback, Notification
)

# --- Event / Agenda ---
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    speakers = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Session
        fields = '__all__'


# --- People / Companies ---
class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = '__all__'


class ExhibitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exhibitor
        fields = '__all__'


class SponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sponsor
        fields = '__all__'


# --- Attendees / Tickets ---
class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        exclude = ['unsubscribe_token']  # don’t expose sensitive field


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


# --- Networking ---
class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectionRequest
        fields = '__all__'


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'


# --- Engagement ---
class PollSerializer(serializers.ModelSerializer):
    options = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Poll
        fields = '__all__'


class PollOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollOption
        fields = '__all__'


class PollVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollResponse
        fields = '__all__'


class QnASerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

# ---------------------------