from django.conf import settings
from django.db import models, transaction
from django.db.models import Count, OuterRef, Subquery
from django.db.models.functions import Concat
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import GuestbookUser, GuestbookEntry
from .serializers import GuestbookEntrySerializer, UserDataSerializer

class GuestbookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling guestbook entries and user data.
    
    This ViewSet provides the following endpoints:
    - POST /api/entries/: Create a new entry
    - GET /api/entries/: List all entries with pagination
    - GET /api/users-data/: Get aggregated user data
    
    Pagination:
        - Page size: 3 items per page
        - Ordering: Created date descending
    
    Optimization:
        - Uses select_related for user data
        - Implements database-level aggregation
        - Uses atomic transactions for data consistency
    """

    serializer_class = GuestbookEntrySerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        """
        Returns queryset of all entries ordered by creation date.
        Optimizes database queries using select_related.
        """
        return GuestbookEntry.objects.select_related('user').order_by('-created_at')

    def get_paginated_response(self, data):
        """
        Customizes the pagination response format.
        
        Returns:
            Response with the following structure:
            {
                'count': total number of items,
                'page_size': items per page,
                'total_pages': total number of pages,
                'current_page_number': current page number,
                'links': {
                    'next': URL for next page,
                    'previous': URL for previous page
                },
                'entries': serialized entries data
            }
        """
        return Response({
            'count': self.paginator.page.paginator.count,
            'page_size': settings.REST_FRAMEWORK['PAGE_SIZE'],
            'total_pages': self.paginator.page.paginator.num_pages,
            'current_page_number': self.paginator.page.number,
            'links': {
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link()
            },
            'entries': data
        })

    @transaction.atomic
    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def users_data(self, request):
        """
        Retrieves aggregated data for all users.
        
        Performs efficient database-level aggregation to get:
        - Total message count per user
        - User's last entry (subject and message combined)
        
        Returns:
            Response with the following structure:
            {
                'users': [
                    {
                        'username': user's name,
                        'last_entry': 'subject | message'
                    },
                    ...
                ]
            }
        """
        latest_entries = GuestbookEntry.objects.filter(
            user=OuterRef('pk')
        ).order_by('-created_at')

        users = GuestbookUser.objects.annotate(
            message_count=Count('entries', distinct=True),
            last_entry=Subquery(
                latest_entries.values('subject', 'message')
                .annotate(
                    combined=Concat(
                        'subject',
                        models.Value(' | '),
                        'message',
                        output_field=models.CharField()
                    )
                )
                .values('combined')[:1]
            )
        )

        serializer = UserDataSerializer(users, many=True)
        return Response({
            'users': [{
                'username': user['name'],
                'last_entry': user['last_entry']
            } for user in serializer.data]
        })
