from django.contrib import admin
from .models import *

admin.site.register(Profile)
admin.site.register(AuthToken)
admin.site.register(Case)
admin.site.register(TruthBullet)