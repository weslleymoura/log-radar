from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import uuid

class OnlyActiveManager(models.Manager):
    def get_queryset(self):
        return super(OnlyActiveManager, self).get_queryset().filter(is_active=True)

class DataPoint(models.Model):

    objects = OnlyActiveManager()

    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Origin
    origin = models.CharField('origin', max_length=100, blank=False, null=False)

    # Destination
    destination = models.CharField('destination', max_length=100, blank=False, null=False)

    # Dimension 1
    dim_1 = models.DecimalField('dim_1', blank=False, null=False, decimal_places=2,max_digits=10)

    # Dimension 2
    dim_2 = models.DecimalField('dim_2', blank=False, null=False, decimal_places=2,max_digits=10)

    # Business key
    business_key = models.CharField('business_key', max_length=100, blank=True, null=True)

    # 1 = Active, 0 = Inactive
    is_active = models.BooleanField('is_active', blank=False, null=False, default=True)

    # 1 = Active, 0 = Inactive
    is_train = models.BooleanField('is_train', blank=False, null=False, default=False)

    # Number of contours
    n_contours = models.IntegerField('n_contours', blank=False, null=False, default=-1)

    # Created date of this deal 
    date_created = models.DateTimeField('date_created', blank=False, null=False, auto_now_add=True)

    # Last modification of this deal
    date_modified = models.DateTimeField('date_modified', blank=False, null=False, auto_now=True)

    class Meta:
        verbose_name = 'Data Point'
        verbose_name_plural = 'Data Points'
        ordering = ['id']

    def __str__(self):
        return str(self.dim_1) + ' | ' + str(self.dim_1)

    def __init__(self, *args, **kwargs):
        super(DataPoint, self).__init__(*args, **kwargs)