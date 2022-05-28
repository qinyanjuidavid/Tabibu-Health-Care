## Accounts Models

### User Model

- username
- full_name
- email
- phone
- is_active
- is_admin
- is_staff
- role-- > Choice_field(doctor,nurse,pharmacist,labtech,receptionist,administrator,patient)

### Profile

- user
- bio
- profile_picture
- id_no
- nationality
- town
- estate
- gender (Male,Female, Other)
- date_of_birth
- timestamp
- marital_status (Single,Married,widowed,Divorced,Separated)

### Department

- dept (eg. General_Surgery,Neurology,Orthopedics,Gynacology,Microbiology,Anaesthetics,Dentistry)
- room_number
- date_added
- date_updated
- added_by

### Administrator

- department
- job_id

### Pharmacist

- department
- job_id

### Nurse

- department
- job_id

### Doctor

- department
- job_id

### Receptionist

- department
- job_id

### Patient

- blood_group
- weight
- height
- blood_pressure
- blood_sugar

### Labtech

- department
- job_id

## Appointment Application

### Appointment_ID

- unique_id

### Appointment

- Appointment_ID (unique_id)
- patient(FK)
- appointment_fee(100)
- paid (bool)
- appointment_date(default=current_date) is status is not admitted or discharged it Expires when the day ends
- Appointment_status (admitted,discharged, pending,treated,expired)
- added_by (Receptionist)
- department(FK)--> The department where the patient wants to visit
- signs
- findings
- department(FK)

### Lab_Test

- test_name(unique)
- price
- available
- description
- added_by (Admin and Labtech)

### Medicine

- name(unique)
- price
- in_stock(bool)
- description
- added_by(pharmacist or Admin)

### Test

- test(FK)
- appointment(FK)
- tested(Bool)
- date_tested
- paid(bool)

### Medication

- appointment
- medicine(FK)
- paid (bool)
- quantity
- notes
- doctor (FK)

### Tests

- appointment(FK)
- test(ManyToMany)
- paid(bool)
- tested(bool)
  > Total_method

### Prescription

- appointment(FK)
- medicine (ManyToMany)
- paid (bool)
  > Total_method

### Wards

- ward_name
- room_number
- bed_number
- Ward_type (ICU, Isolation,...)
- added_by (admin)

### Room Allotment

- appointment(FK)
- ward(Fk)
- doctor
- price_per_day
- allortment_date
- date_of_discharge
- discharge/admitted (FK)
  > Billing must be completed for discharge to take place...

## Billing Application

### Payment

> Create payment each time appointment is created,patient_test is initiated and medication is prescribed to patient

- Item (Appointment,medicine_name,test_name,ward)
- patient (FK)
- Quantity
- total_amount (Total_method)
- sub_unit
- payment_date
- tax (default=10%)
- paid_amount
  > paid_amount less total_amount == Partial, where paid_amount >= total_amount == completed
- payment_status (complete,pending,partial)
- payment_method (M-Pesa,NHIF,Credit_Card,Debit_card,Cash)

### Payment Invoice

> Create payment invoice for a certain appointment_id & add all the payments involved in that appointment_id

- payment(FK)
- Invoice_date
- added_by (appointment,lab,pharmacist)
- unit_cost
- quantity
- charges
- patient
- tax (10%)
  > Total Charges
  > VAT

### Todo's

- Avail all tests to the receptionist
- Avail all Medications to the receptionist
- Avail paid tests to the lab-tech
- Avail the results of the tests to the doctor
- Avail all paid Medications to the pharmacy
- Generate Bills for Appointment, Medication and Tests
- Avail the bills to the receptionist
- Avail all tests to the management records\*
- Avail all Medications to the Management records\*
- Avail all bills to the management
- Ensure Efficiency in the services
- Deploy first version

#### Ward Allortment

- Brainstorm on ward allortment
- Implement Feature

#### Real-time Ambulance Booking

- Brainstorm
- Implement Feature

#### Virtual Assistant(ML)

- Brainstorm
- Implement Feature
