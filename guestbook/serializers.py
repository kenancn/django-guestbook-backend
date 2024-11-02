from rest_framework import serializers
from .models import GuestbookUser, GuestbookEntry
from django.utils import timezone


class GuestbookUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestbookUser
        fields = ['name']


class GuestbookEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for guestbook entries.
    
    Handles both serialization and creation of entries.
    Automatically creates or retrieves user based on provided name.
    
    Fields:
        user: Read-only field showing user's name
        name: Write-only field for user identification
        subject: Entry subject
        message: Entry content
    """
    user = serializers.SerializerMethodField()
    name = serializers.CharField(
        write_only=True,
        min_length=2,
        max_length=255,
        error_messages={
            'min_length': 'Name must be at least 2 characters long.',
            'max_length': 'Name cannot exceed 255 characters.',
            'blank': 'Name cannot be blank.',
            'required': 'Name field is required.'
        }
    )
    subject = serializers.CharField(
        min_length=3,
        max_length=255,
        error_messages={
            'min_length': 'Subject must be at least 3 characters long.',
            'max_length': 'Subject cannot exceed 255 characters.',
            'blank': 'Subject cannot be blank.',
            'required': 'Subject field is required.'
        }
    )
    message = serializers.CharField(
        min_length=10,
        error_messages={
            'min_length': 'Message must be at least 10 characters long.',
            'blank': 'Message cannot be blank.',
            'required': 'Message field is required.'
        }
    )

    class Meta:
        model = GuestbookEntry
        fields = ['user', 'subject', 'message', 'name']

    def validate_name(self, value):
        """
        Custom name validation.
        """
        if any(char.isdigit() for char in value):
            raise serializers.ValidationError("Name cannot contain numbers.")
        
        # Özel karakterleri kontrol et (sadece harfler, boşluk ve tire izin ver)
        if not all(char.isalpha() or char.isspace() or char == '-' for char in value):
            raise serializers.ValidationError("Name can only contain letters, spaces, and hyphens.")
        
        return value.strip()

    def validate_subject(self, value):
        """
        Custom subject validation.
        """
        # Müstehcen kelimeleri kontrol et (örnek olarak)
        forbidden_words = ['spam', 'inappropriate', 'offensive']
        if any(word in value.lower() for word in forbidden_words):
            raise serializers.ValidationError("Subject contains inappropriate content.")
        
        return value.strip()

    def validate(self, data):
        """
        Object-level validation that uses multiple fields.
        """
        if 'subject' in data and 'message' in data:
            if data['subject'].lower() == data['message'].lower():
                raise serializers.ValidationError({
                    'message': 'Message cannot be identical to subject.'
                })
            
            # Spam kontrolü - aynı mesajın tekrarlanmasını engelle
            if GuestbookEntry.objects.filter(
                message=data['message'],
                created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
            ).exists():
                raise serializers.ValidationError({
                    'message': 'Please wait 5 minutes before posting the same message again.'
                })

        return data

    def get_user(self, obj):
        return obj.user.name

    def create(self, validated_data):
        name = validated_data.pop('name')
        user, _ = GuestbookUser.objects.get_or_create(name=name)
        validated_data['user'] = user
        return super().create(validated_data)


class UserDataSerializer(serializers.ModelSerializer):
    """
    Serializer for aggregated user data.
    
    Handles serialization of user statistics and their last entry.
    
    Fields:
        name: User's name
        message_count: Total number of entries by user
        last_entry: Combined subject and message of user's latest entry
    """
    message_count = serializers.IntegerField()
    last_entry = serializers.CharField()

    class Meta:
        model = GuestbookUser
        fields = ['name', 'message_count', 'last_entry'] 