from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('diller', 'Diller'),
        ('sotuv_agent', 'Sotuv Agent'),
        ('klient', 'Klient'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='klient')
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username


class Ombor(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    responsible_person = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_warehouses')

    def __str__(self):
        return self.name


class Kategoriya(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Birlik(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Mahsulot(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=255, unique=True)
    birlik = models.ForeignKey(Birlik, on_delete=models.SET_NULL, null=True)
    kategoriya = models.ForeignKey(Kategoriya, on_delete=models.SET_NULL, null=True)
    narx = models.DecimalField(max_digits=10, decimal_places=2)
    rasm = models.ImageField(upload_to='mahsulotlar/', blank=True, null=True)  # Rasm maydoni

    def __str__(self):
        return self.name


class OmborMahsulot(models.Model):
    ombor = models.ForeignKey(Ombor, on_delete=models.CASCADE)
    mahsulot = models.ForeignKey(Mahsulot, on_delete=models.CASCADE)
    soni = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('ombor', 'mahsulot')  # Bir omborda bir xil mahsulot faqat bir marta bo'lishi mumkin

    def __str__(self):
        return f"{self.ombor.name} - {self.mahsulot.name} - {self.soni}"


class Purchase(models.Model):
    ombor = models.ForeignKey(Ombor, on_delete=models.CASCADE)
    sana = models.DateField()
    yetkazib_beruvchi = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='Yaratilgan')
    total_sum = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Purchase #{self.pk} - {self.ombor.name} - {self.sana}"


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    mahsulot = models.ForeignKey(Mahsulot, on_delete=models.CASCADE)
    soni = models.PositiveIntegerField()
    narx = models.DecimalField(max_digits=10, decimal_places=2)
    yaroqlilik_muddati = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.mahsulot.name} - {self.soni}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.purchase.total_sum = self.purchase.calculate_total_sum()
        self.purchase.save()


class Sotuv(models.Model):
    from_ombor = models.ForeignKey(Ombor, on_delete=models.CASCADE, related_name='sotuvlar_chiqish')
    to_ombor = models.ForeignKey(Ombor, on_delete=models.CASCADE, related_name='sotuvlar_kirish')
    sana = models.DateField()
    sotib_oluvchi = models.ForeignKey(User, on_delete=models.CASCADE)
    total_sum = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Sotuv #{self.pk} - {self.from_ombor.name} -> {self.to_ombor.name} - {self.sana}"


class SotuvItem(models.Model):
    sotuv = models.ForeignKey(Sotuv, on_delete=models.CASCADE, related_name='items')
    mahsulot = models.ForeignKey(Mahsulot, on_delete=models.CASCADE)
    soni = models.PositiveIntegerField()
    narx = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.mahsulot.name} - {self.soni}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sotuv.total_sum = self.sotuv.calculate_total_sum()
        self.sotuv.save()


class Payment(models.Model):
    sotuv = models.ForeignKey(Sotuv, on_delete=models.CASCADE, related_name='payments')
    sana = models.DateField()
    summa = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Payment #{self.pk} - {self.sotuv.pk} - {self.summa}"


class Qarz(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='qarzlari')
    sotuv = models.ForeignKey('Sotuv', on_delete=models.CASCADE, related_name='qarzlari')
    qarz_summasi = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tolangan_summa = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sana = models.DateField(auto_now_add=True)
    eslatma = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.qarz_summasi}"

    def qoldiq_qarz(self):
        return self.qarz_summasi - self.tolangan_summa
    qoldiq_qarz.short_description = "Qoldiq qarz"

    def qarzdorlik_muddati(self):
        vaqt_farqi = timezone.now().date() - self.sana
        return vaqt_farqi.days
    qarzdorlik_muddati.short_description = "Qarzdorlik muddati"