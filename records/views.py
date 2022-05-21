from tkinter.filedialog import test
from django.shortcuts import render, get_object_or_404
from accounts.models import Administrator, Departments
from rest_framework import generics, serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q
from accounts.permissions import (IsAdministrator, IsDoctor, IsLabtech,
                                  IsNurse, IsPatient, IsPharmacist,
                                  IsReceptionist)
from appointments.models import Lab_test, Medicine, Test
from records.serializers import MedicineSerializer, TestSerializer
from accounts.serializers import DepartmentsSerializer


class TestAPIView(ModelViewSet):
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self):
        testObj = Lab_test.objects.all()
        return testObj

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        adminObj = Administrator.objects.get(user=request.user)
        serializer.save(added_by=adminObj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        adminObj = Administrator.objects.get(user=request.user)
        serializer.save(added_by=adminObj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        queryset.delete()
        return Response(
            {"message": "Test was successfully deleted."},
            status=status.HTTP_204_NO_CONTENT
        )


class MedicineAPIView(ModelViewSet):
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self):
        medObj = Medicine.objects.all()
        return medObj

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        adminObj = Administrator.objects.get(user=request.user)
        serializer.save(added_by=adminObj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        adminObj = Administrator.objects.get(user=request.user)
        serializer.save(added_by=adminObj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        queryset.delete()
        return Response(
            {"message": "Medicine was successfully deleted"},
            status=status.HTTP_204_NO_CONTENT
        )


class DepartmentAPIView(ModelViewSet):
    serializer_class = DepartmentsSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self):
        departmentObj = Departments.objects.all()
        return departmentObj

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        adminObj = Administrator.objects.get(user=request.user)
        serializer.save(added_by=adminObj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        adminObj = Administrator.objects.get(user=request.user)
        serializer.save(added_by=adminObj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        queryset.delete()
        return Response(
            {"message": "Department was successfully deleted"},
            status=status.HTTP_204_NO_CONTENT
        )
