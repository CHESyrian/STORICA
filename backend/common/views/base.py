from rest_framework import status, viewsets

from common.api_response import ApiResponse
from common.constants import SuccessMessages


class BaseModelViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        """
        Optional hook for future multi-tenant or soft-delete logic.
        """
        return super().get_queryset()

    def get_serializer_context(self):
        """
        Standard context extension for all serializers.
        """
        context = super().get_serializer_context()
        context["request"] = self.request
        context["user"] = self.request.user
        return context

    def list(self, request, *args, **kwargs):
        """
        Handles lists by routing through get_paginated_response if pages exist,
        or returning a flat ApiResponse array if pagination is bypassed.
        """
        """ Wraps standard listing responses within custom formatting 
            boundaries. """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginator = self.get_paginated_response(serializer.data)
            
            return ApiResponse.success(
                data=paginator.data['result'], 
                message=SuccessMessages.RETRIEVE,
                paginator=paginator.data['paginator']
            )

        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(
            data=serializer.data, 
            message=SuccessMessages.RETRIEVE
        )

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return ApiResponse.success(
            data=response.data,
            message=self.success_messages["retrieve"],
            status_code=response.status_code,
        )

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return ApiResponse.success(
            data=response.data,
            message=SuccessMessages.CREATE,
            status_code=response.status_code,
        )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return ApiResponse.success(
            data=response.data,
            message=SuccessMessages.UPDATE,
            status_code=response.status_code,
        )

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return ApiResponse.success(
            data=response.data,
            message=SuccessMessages.UPDATE,
            status_code=response.status_code,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        # Using HTTP 200 OK so clients can parse the "Deleted successfully" body text safely
        return ApiResponse.success(
            data=None,
            message=SuccessMessages.DESTROY,
            status_code=status.HTTP_200_OK,
        )


