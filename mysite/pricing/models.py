from django.db import models

# Create your models here.
class data(models.Model):
    title = models.CharField(unique = True, max_length= 1000)
    ncchomelearning_url = models.CharField(max_length=2000)
    ncchomelearning_price = models.CharField(max_length=20)
    mydistance_learning_college_url = models.CharField(max_length=2000)
    mydistance_learning_college_price = models.CharField(max_length=20)
    distance_learning_centre_url = models.CharField(max_length=2000)
    distance_learning_centre_price = models.CharField(max_length=20)
    openstudycollege_url = models.CharField(max_length=2000)
    openstudycollege_price = models.CharField(max_length=20)
    ukopencollege_url = models.CharField(max_length=2000)
    ukopencollege_price = models.CharField(max_length=20)
    edistancelearning_url = models.CharField(max_length=2000)
    edistancelearning_price = models.CharField(max_length=20)
    avg_comp_price = models.CharField(max_length=2000)