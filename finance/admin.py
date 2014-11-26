from django.contrib import admin
from finance.models import Extract, TypeLaunch, Provider


class ProviderInline(admin.TabularInline):
    model = Provider
    raw_id_fields = ('type_launch', )


class ExtractAdmin(admin.ModelAdmin):
    #fields = ['launch', 'date_launch']
    # fieldsets = [
    #     (None,               {'fields': ['launch']}),
    #     ('Date information', {'fields': ['date_launch'], 'classes': ['collapse']}),
    # ]
    # inlines = (TypeLaunchInline,)
    # raw_id_fields = ('date_launch', 'launch', 'date_purchase', 'value_debit', 'value_credit', 'value_balance' )
    search_fields = ('date_launch', 'launch',)
    list_display = ('id', 'date_launch', 'launch', 'date_purchase', 'value_debit', 'value_credit', 'value_balance')


class TypeLaunchAdmin(admin.ModelAdmin):
    #inlines = [ProviderInline, ]
    search_fields = ('id', 'type_name',)
    list_display = ('id', 'type_name',)


class ProviderAdmin(admin.ModelAdmin):
    search_fields = ('id', 'type_launch__type_name', 'date_last_purchase', 'description',)
    list_display = ('id', 'type_name', 'date_last_purchase', 'description',)
    #raw_id_fields = ('type_launch', )

    def type_name(self, instance):
        obj = instance.type_launch
        if not obj is None:
            return obj.type_name


admin.site.register(Extract, ExtractAdmin)
admin.site.register(TypeLaunch, TypeLaunchAdmin)
admin.site.register(Provider, ProviderAdmin)