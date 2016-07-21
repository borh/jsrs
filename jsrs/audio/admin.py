# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Audio, Reader, Sentence

admin.site.register(Audio)
admin.site.register(Reader)
admin.site.register(Sentence)
