from rest_framework.response import Response


class ApiResponse:

    @classmethod
    def success(
        cls,
        data=None,
        message="Success",
        paginator=None,
        status_code=200,
        meta=None,
        trace_id=None,
    ):
        return Response({
            "success"   : True,
            "message"   : message,
            "data"      : data,
            "paginator" : paginator, 
            "meta"      : meta or {},
            "trace_id"  : trace_id,
        }, status=status_code)

    @classmethod
    def error(
        cls,
        message="Error",
        errors=None,
        status_code=400,
        error_code=None,
        trace_id=None,
    ):
        return Response({
            "success"    : False,
            "message"    : message,
            "errors"     : errors or {},
            "error_code" : error_code,
            "trace_id"   : trace_id,
        }, status=status_code)