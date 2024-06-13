from django.contrib import admin

from .models import Trader, Market,  Participant, Trade, Instrument, Strategy, Plan

admin.site.register(Trader)
admin.site.register(Market)
admin.site.register(Trade)
admin.site.register(Participant)
admin.site.register(Instrument)
admin.site.register(Strategy)
admin.site.register(Plan)

