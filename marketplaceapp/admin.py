from django.contrib import admin
from marketplaceapp.models import Farmer,Customer,Product,Delivery,Contact

# Register your models here.
admin.site.register(Farmer)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Delivery)
admin.site.register(Contact)
