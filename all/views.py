from rest_framework import viewsets, permissions, filters, status, views, response
from .models import User, Ombor, Kategoriya, Birlik, Mahsulot, Purchase, PurchaseItem, Sotuv, SotuvItem, Payment, OmborMahsulot, Qarz
from .serializers import UserSerializer, OmborSerializer, KategoriyaSerializer, BirlikSerializer, MahsulotSerializer, PurchaseSerializer, PurchaseItemSerializer, SotuvSerializer, SotuvItemSerializer, PaymentSerializer,LoginSerializer, OmborMahsulotSerializer, QarzSerializer, TokenSerializer, LogoutSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def sotuv_hisoboti(request):
    """Sotuvlar bo'yicha hisobot"""
    sotuvlar = Sotuv.objects.annotate(month=TruncMonth('sana')).values('month').annotate(total_sum=Sum('total_sum')).order_by('month')
    return Response(sotuvlar)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def xarid_hisoboti(request):
    """Xaridlar bo'yicha hisobot"""
    xaridlar = Purchase.objects.annotate(month=TruncMonth('sana')).values('month').annotate(total_sum=Sum('total_sum')).order_by('month')
    return Response(xaridlar)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ombor_hisoboti(request):
    """Omborlar bo'yicha hisobot"""
    omborlar = OmborMahsulot.objects.values('ombor__name').annotate(total_mahsulot=Sum('soni'))
    return Response(omborlar)


User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:  # Admin barcha userlarni ko'ra oladi
            return User.objects.all()
        return User.objects.filter(id=user.id)  # Oddiy user faqat o'zini ko'ra oladi

    def create(self, request, *args, **kwargs):
        """Admin user yaratadi"""
        if request.user.is_staff:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({"detail": "Sizda user yaratish huquqi yo'q."}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, pk=None):
        """Admin user ma'lumotlarini o'zgartiradi"""
        user = self.get_object()
        if request.user.is_staff:
            serializer = UserSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({"detail": "Sizda userni o'zgartirish huquqi yo'q."}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None):
        """Admin user o'chiradi"""
        user = self.get_object()
        if request.user.is_staff:
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Sizda userni o'chirish huquqi yo'q."}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['get'])
    def current_user(self):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_klient(self, request):
        """Diller va Sotuv agenti Klient yaratadi"""
        user = request.user
        if user.user_type in ['diller', 'sotuv_agent']:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                klient = serializer.save(user_type='klient')
                return Response(UserSerializer(klient).data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Sizda klient yaratish huquqi yo'q."}, status=status.HTTP_403_FORBIDDEN)


class LoginAPIView(views.APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return response.Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


class LogoutAPIView(views.APIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = serializer.validated_data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return response.Response(status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return response.Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)


class OmborViewSet(viewsets.ModelViewSet):
    queryset = Ombor.objects.all()
    serializer_class = OmborSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:  # Admin barcha omborlarni ko'ra oladi
            return Ombor.objects.all()
        return Ombor.objects.filter(responsible_person=user)  # Faqat o'ziga tegishli omborlar

    def create(self, request, *args, **kwargs):
        """Admin, Diller va Sotuv agenti ombor yaratadi"""
        user = request.user
        if user.is_staff or user.user_type in ['diller', 'sotuv_agent']:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({"detail": "Sizda ombor yaratish huquqi yo'q."}, status=status.HTTP_403_FORBIDDEN)

    def perform_create(self, serializer):
        serializer.save(responsible_person=self.request.user)


class KategoriyaViewSet(viewsets.ModelViewSet):
    queryset = Kategoriya.objects.all()
    serializer_class = KategoriyaSerializer
    permission_classes = [permissions.IsAuthenticated]


class BirlikViewSet(viewsets.ModelViewSet):
    queryset = Birlik.objects.all()
    serializer_class = BirlikSerializer
    permission_classes = [permissions.IsAuthenticated]


class MahsulotViewSet(viewsets.ModelViewSet):
    queryset = Mahsulot.objects.all()
    serializer_class = MahsulotSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'sku', 'kategoriya__name']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]


class PurchaseItemViewSet(viewsets.ModelViewSet):
    queryset = PurchaseItem.objects.all()
    serializer_class = PurchaseItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class SotuvViewSet(viewsets.ModelViewSet):
    queryset = Sotuv.objects.all()
    serializer_class = SotuvSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Ombordan omborga sotish"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sotuv = serializer.save()

        items_data = request.data.get('items', [])
        for item_data in items_data:
            mahsulot = item_data['mahsulot']
            soni = item_data['soni']

            # Ombordan mahsulotni olish
            from_ombor = sotuv.from_ombor
            from_ombor_mahsulot = OmborMahsulot.objects.filter(ombor=from_ombor, mahsulot=mahsulot).first()

            if not from_ombor_mahsulot or from_ombor_mahsulot.soni < soni:
                sotuv.delete()  # Sotuvni bekor qilish
                return Response({"detail": f"{mahsulot} omborda yetarli emas."}, status=status.HTTP_400_BAD_REQUEST)

            # Ombordan mahsulotni kamaytirish
            from_ombor_mahsulot.soni -= soni
            from_ombor_mahsulot.save()

            # Boshqa omborga mahsulotni qo'shish
            to_ombor = sotuv.to_ombor
            to_ombor_mahsulot, created = OmborMahsulot.objects.get_or_create(ombor=to_ombor, mahsulot=mahsulot)
            to_ombor_mahsulot.soni += soni
            to_ombor_mahsulot.save()

            # Sotuv itemini yaratish
            SotuvItem.objects.create(sotuv=sotuv, mahsulot=mahsulot, soni=soni, narx=Mahsulot.objects.get(id=mahsulot).narx)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SotuvItemViewSet(viewsets.ModelViewSet):
    queryset = SotuvItem.objects.all()
    serializer_class = SotuvItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()

        sotuv = payment.sotuv
        qarz = Qarz.objects.filter(user=sotuv.sotib_oluvchi, sotuv=sotuv).first()

        if qarz:
            qarz.tolangan_summa += payment.summa
            qarz.save()
        else:
            Qarz.objects.create(user=sotuv.sotib_oluvchi, sotuv=sotuv, qarz_summasi=sotuv.total_sum, tolangan_summa=payment.summa)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QarzViewSet(viewsets.ModelViewSet):
    queryset = Qarz.objects.all()
    serializer_class = QarzSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def eslatma_yaratish(self, request, pk=None):
        qarz = self.get_object()
        qarz.eslatma = True
        qarz.save()
        return Response({"detail": "Eslatma yaratildi"}, status=status.HTTP_200_OK)


class TokenAPIView(views.APIView):
    serializer_class = TokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return response.Response(serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)