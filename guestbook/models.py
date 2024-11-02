from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating timestamp fields.
    
    This model is used as a base class for all models that need to track
    creation and modification times.
    
    Attributes:
        created_at (DateTimeField): Automatically set when object is created
        updated_at (DateTimeField): Automatically updated when object is saved
    """
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        editable=False
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
        editable=False
    )

    class Meta:
        abstract = True


class GuestbookUser(TimeStampedModel):
    """
    Model to store guestbook users.
    
    This model represents users who create entries in the guestbook.
    Each user is uniquely identified by their name.
    
    Attributes:
        name (CharField): Unique name identifier for the user
        created_at (DateTimeField): Inherited from TimeStampedModel
        updated_at (DateTimeField): Inherited from TimeStampedModel
    
    Indexes:
        - name: For faster lookups by username
    """
    name = models.CharField(
        _('name'),
        max_length=255,
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name = _('guestbook user')
        verbose_name_plural = _('guestbook users')
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class GuestbookEntry(TimeStampedModel):
    """
    Model to store guestbook entries.
    
    This model represents individual entries in the guestbook.
    Each entry is associated with a user and contains a subject and message.
    
    Attributes:
        user (ForeignKey): Reference to GuestbookUser who created the entry
        subject (CharField): Entry subject/title
        message (TextField): Main content of the entry
        created_at (DateTimeField): Inherited from TimeStampedModel
        updated_at (DateTimeField): Inherited from TimeStampedModel
    
    Indexes:
        - created_at: For sorting entries by creation time
        - user + created_at: For efficiently retrieving user's entries
        - subject: For subject-based searches
    """
    user = models.ForeignKey(
        GuestbookUser,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='entries'
    )
    subject = models.CharField(
        _('subject'),
        max_length=255
    )
    message = models.TextField(
        _('message')
    )

    class Meta:
        verbose_name = _('guestbook entry')
        verbose_name_plural = _('guestbook entries')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['subject']),
        ]

    def __str__(self):
        return f"{self.subject} - {self.user.name}"
