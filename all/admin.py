from django.contrib import admin
from .models import User, Ombor, Kategoriya, Birlik, Mahsulot, Purchase, PurchaseItem, Sotuv, SotuvItem, Payment, Qarz
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('User Type', {'fields': ('user_type',)}),
    )


@admin.register(Ombor)
class OmborAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'responsible_person')


@admin.register(Kategoriya)
class KategoriyaAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Birlik)
class BirlikAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Mahsulot)
class MahsulotAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'birlik', 'kategoriya', 'narx')


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('ombor', 'sana', 'yetkazib_beruvchi', 'status')
    inlines = [PurchaseItemInline]


class SotuvItemInline(admin.TabularInline):
    model = SotuvItem
    extra = 1


@admin.register(Sotuv)
class SotuvAdmin(admin.ModelAdmin):
    list_display = ('from_ombor', 'to_ombor', 'sana', 'sotib_oluvchi')
    inlines = [SotuvItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('sotuv', 'sana', 'summa')


@admin.register(Qarz)
class QarzAdmin(admin.ModelAdmin):
    list_display = ('user', 'qarz_summasi', 'tolangan_summa', 'qoldiq_qarz', 'sana', 'eslatma', 'qarzdorlik_muddati')
    list_filter = ('user', 'sana', 'eslatma')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ('qoldiq_qarz', 'qarzdorlik_muddati')