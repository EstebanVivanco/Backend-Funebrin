from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    stock = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image_url = models.TextField()
    material = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)
    type = models.ForeignKey('ProductType', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class ProductType(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
