from rest_framework import serializers
from .models import User, Ombor, Kategoriya, Birlik, Mahsulot, Purchase, PurchaseItem, Sotuv, SotuvItem, Payment, OmborMahsulot, Qarz
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'phone_number', 'user_type']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)

    def validate_email(self, value):
        """Email validatsiyasi"""
        if "@" not in value:
            raise serializers.ValidationError("Email manzilida @ belgisi bo'lishi kerak.")
        return value

from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework import exceptions

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username', None)
        password = data.get('password', None)

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise exceptions.AuthenticationFailed('User is inactive.')
            else:
                raise exceptions.AuthenticationFailed('Invalid credentials.')
        else:
            raise exceptions.AuthenticationFailed('Must include "username" and "password".')

        return data

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class QarzSerializer(serializers.ModelSerializer):
    qoldiq_qarz = serializers.ReadOnlyField()
    qarzdorlik_muddati = serializers.ReadOnlyField()

    class Meta:
        model = Qarz
        fields = '__all__'


class OmborSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ombor
        fields = '__all__'


class OmborMahsulotSerializer(serializers.ModelSerializer):
    mahsulot_name = serializers.ReadOnlyField(source='mahsulot.name')

    class Meta:
        model = OmborMahsulot
        fields = ['id', 'mahsulot', 'mahsulot_name', 'soni']

class KategoriyaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kategoriya
        fields = '__all__'


class BirlikSerializer(serializers.ModelSerializer):
    class Meta:
        model = Birlik
        fields = '__all__'


class MahsulotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mahsulot
        fields = '__all__'

    def validate_name(self, value):
        """Mahsulot nomi validatsiyasi"""
        if len(value) < 3:
            raise serializers.ValidationError("Mahsulot nomi juda qisqa bo'lishi mumkin emas.")
        return value

    def validate_narx(self, value):
        """Mahsulot narxi validatsiyasi"""
        if value <= 0:
            raise serializers.ValidationError("Mahsulot narxi 0 dan katta bo'lishi kerak.")
        return value


class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = '__all__'


class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True, read_only=True)

    class Meta:
        model = Purchase
        fields = '__all__'


class SotuvItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SotuvItem
        fields = '__all__'


class SotuvSerializer(serializers.ModelSerializer):
    items = SotuvItemSerializer(many=True, read_only=True)

    class Meta:
        model = Sotuv
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class TokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Qo'shimcha ma'lumotlarni tokenga qo'shish (ixtiyoriy)
        token['username'] = user.username
        # token['user_type'] = user.user_type

        return token