from django.db import models

class Patient(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    STATUS_CHOICES = [
        ('Normal', 'Normal'),
        ('Emergency', 'Emergency'),
    ]

    ISSUE_CHOICES = [
        ('Headache', 'Headache'),
        ('Fever', 'Fever'),
        ('Migraine', 'Migraine'),
        ('Typhoid', 'Typhoid'),
        ('Diarrhea', 'Diarrhea'),
        ('Jaundice', 'Jaundice'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=5)
    issue = models.CharField(max_length=20, choices=ISSUE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    treated = models.BooleanField(default=False)

    def __str__(self):
        return self.name