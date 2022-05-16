from django.shortcuts import render

from accounts.permissions import (
    IsAdministrator, IsDoctor, IsLabtech,
    IsNurse, IsPatient, IsPharmacist,
    IsReceptionist)
