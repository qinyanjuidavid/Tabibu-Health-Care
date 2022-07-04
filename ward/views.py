from django.shortcuts import render, get_object_or_404
from rest_framework import generics, serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from accounts.models import Administrator
from accounts.permissions import IsAdministrator, IsDoctor, IsNurse, IsPatient, IsReceptionist
from ward.models import Ward

from ward.serializers import WardSerializer


class WardAPIView(ModelViewSet):
    serializer_class = WardSerializer
    permission_classes = (
        IsAuthenticated, IsAdministrator, IsDoctor,
        IsNurse, IsReceptionist, IsPatient
    )
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self):
        wardObj = Ward.objects.all()
        return wardObj

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.role == "Administrator":
            adminObj = Administrator.objects.get(user=request.user)
            serializer.save(added_by=adminObj)
        else:
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_object()
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid()
        if request.user.role == "Administrator":
            adminObj = Administrator.objects.get(user=request.user)
            serializer.save(added_by=adminObj)
        else:
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        if request.user.role == "Administrator":
            queryset.delete()
        else:
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": "Ward was successfully deleted."},
            status=status.HTTP_204_NO_CONTENT
        )
