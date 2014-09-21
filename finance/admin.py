from django.contrib import admin

# Register your models here.
from finance.models import Extract, TypeLaunch, Provider


#class TypeLaunchInline(admin.StackedInline):
class TypeLaunchInline(admin.TabularInline):
    model = TypeLaunch
    extra = 0
    raw_id_fields = ('id', 'type_name', )


class ExtractAdmin(admin.ModelAdmin):
    #fields = ['launch', 'date_launch']
    # fieldsets = [
    #     (None,               {'fields': ['launch']}),
    #     ('Date information', {'fields': ['date_launch'], 'classes': ['collapse']}),
    # ]
    # inlines = (TypeLaunchInline,)
    # raw_id_fields = ('date_launch', 'launch', 'date_purchase', 'value_debit', 'value_credit', 'value_balance' )
    search_fields = ('date_launch', 'launch',)
    list_display = ('date_launch', 'launch', 'date_purchase', 'value_debit', 'value_credit', 'value_balance' )


class TypeLaunchAdmin(admin.ModelAdmin):
	search_fields = ('id', 'type_name',)
	list_display = ('id', 'type_name',)


class ProviderAdmin(admin.ModelAdmin):
	search_fields = ('type_launch', 'date_last_purchase', 'value_total', 'description',)
	list_display = ('type_launch', 'date_last_purchase', 'value_total', 'description',)


admin.site.register(Extract, ExtractAdmin)
admin.site.register(TypeLaunch, TypeLaunchAdmin)
admin.site.register(Provider, ProviderAdmin)