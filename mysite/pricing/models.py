from django.db import models

# Create your models here.
class data(models.Model):
    title = models.CharField(unique = True, max_length= 1000)
    ncchomelearning_url = models.CharField(max_length=2000)
    mydistance_learning_college_url = models.CharField(max_length=2000)
    distance_learning_centre_url = models.CharField(max_length=2000)
    openstudycollege_url = models.CharField(max_length=2000)
    ukopencollege_url = models.CharField(max_length=2000)
    edistancelearning_url = models.CharField(max_length=2000)
    avg_comp_price = models.CharField(max_length=2000)