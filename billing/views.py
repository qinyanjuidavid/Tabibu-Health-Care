from django.shortcuts import render, get_object_or_404
from accounts.permissions import IsAdministrator, IsPatient, IsReceptionist
from billing.models import Invoice, Payment
from billing.serializers import InvoiceSerializer
from records.views import PatientAPIView
from rest_framework import generics, serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


class PaymentAPIView(ModelViewSet):
    serializer_class = PatientAPIView
    permission_classes = (IsAuthenticated, IsAdministrator,
                          IsReceptionist, IsPatient)
    http_method_names = ["get", "put", "delete"]

    def get_queryset(self):
        paymentObj = Payment.objects.all()
        return paymentObj

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        if (request.user.is_administrator or
                request.user.is_receptionist):
            if queryset.paid == True:
                if request.user.is_administrator:
                    queryset.status = "Cancelled"
                    queryset.save()
                else:
                    return Response({"message": "Cannot cancel a paid payment"},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                queryset.status = "Cancelled"
                queryset.save()
        else:
            return Response(
                {"message": "You are not authorized to perform this action"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(
            {"message": "Invoice has been cancelled"},
            status=status.HTTP_204_NO_CONTENT
        )


class InvoiceAPIView(ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = (IsAuthenticated, IsAdministrator,
                          IsReceptionist)
    http_method_names = ["get", "put", "delete"]

    def get_queryset(self):
        invoiceObj = Invoice.objects.all()
        return invoiceObj

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        queryset.status = "Cancelled"
        queryset.save()
        return Response(
            {"message": "Invoice has been cancelled"},
            status=status.HTTP_204_NO_CONTENT
        )
