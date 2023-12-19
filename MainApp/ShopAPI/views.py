from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import PurchaseOrderMutateSerializer, PurchaseOrderSerializer, SupplierSerializer
from .models import PurchaseOrder
from drf_spectacular.utils  import extend_schema

class PurchaseOrderView(APIView):
    @extend_schema(request=PurchaseOrderMutateSerializer)
    def post(self, request, format=None):
        serializer = PurchaseOrderMutateSerializer(data=request.data)

        if serializer.is_valid():
            response_data = serializer.save()
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        supplier_name = request.query_params.get('supplier_name')
        item_name = request.query_params.get('item_name')

        queryset = PurchaseOrder.objects.all()

        if supplier_name:
            queryset = queryset.filter(supplier__name__icontains=supplier_name)

        if item_name:
            queryset = queryset.filter(line_items__item_name__icontains=item_name)

        serializer = PurchaseOrderSerializer(queryset, many=True)

        return Response(serializer.data)


class PurchaseOrderIDView(APIView):

    @extend_schema(responses=PurchaseOrderSerializer)
    def get(self, request, format=None, record_id= None):
        try:
            instance = PurchaseOrder.objects.get(id=record_id)
        except PurchaseOrder.DoesNotExist:
            return Response("Entry not found", status=status.HTTP_404_NOT_FOUND)
        serializer = PurchaseOrderSerializer(instance)
        return Response(serializer.data)

    @extend_schema(request=PurchaseOrderMutateSerializer)
    def put(self, request,record_id,*args, **kwargs):
        instance = PurchaseOrder.objects.get(id=record_id)
        serializer = PurchaseOrderMutateSerializer(instance,data=request.data, partial=True)
        if serializer.is_valid():
            response_data = serializer.save()
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request,record_id,*args, **kwargs):
        instance = PurchaseOrder.objects.get(id=record_id)
        instance.line_items.all().delete()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
