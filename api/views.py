from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import time
import random

from .models import UserProfile

def generate_invite_code():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))

class SendCodeView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        if not phone:
            return Response({"error": "Phone required."}, status=status.HTTP_400_BAD_REQUEST)
        user, created = UserProfile.objects.get_or_create(phone_number=phone)
        time.sleep(random.uniform(1, 2))
        code = ''.join(random.choices('0123456789', k=4))
        user.auth_code = code
        user.auth_code_sent_time = timezone.now()
        user.save()
        print(f"Code for {phone}: {code}")
        return Response({"message": "Code sent."})

class VerifyCodeView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        code = request.data.get('code')
        if not phone or not code:
            return Response({"error": "Phone and code are required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = UserProfile.objects.get(phone_number=phone)
        except UserProfile.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Проверка кода
        if user.auth_code != code:
            return Response({"error": "Invalid code."}, status=status.HTTP_400_BAD_REQUEST)


        if not user.invite_code:
            user.invite_code = generate_invite_code()
            user.save()

        return Response({
            "message": "Verified.",
            "invite_code": user.invite_code,
            "phone": user.phone_number,
            "user_id": user.id,
        })

class ProfileView(APIView):
    def get(self, request):
        phone = request.query_params.get('phone')
        if not phone:
            return Response({"error": "Phone parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = UserProfile.objects.get(phone_number=phone)
        except UserProfile.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        invited_by_me = UserProfile.objects.filter(used_invite_code=user.invite_code) if user.invite_code else []
        invited_numbers = [u.phone_number for u in invited_by_me]

        return Response({
            "phone": user.phone_number,
            "invite_code": user.invite_code,
            "used_invite_code": user.used_invite_code,
            "invited_users": invited_numbers,
        })

    def post(self, request):
        # Ввод чужого инвайт-кода
        phone = request.data.get('phone')
        invite_code_input = request.data.get('invite_code')

        if not phone or not invite_code_input:
            return Response({"error": "Phone and invite_code are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserProfile.objects.get(phone_number=phone)
            inviter = UserProfile.objects.get(invite_code=invite_code_input)
        except UserProfile.DoesNotExist:
            return Response({"error": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)

        if user.used_invite_code:

            return Response({
                "message": "Already used invite code.",
                "used_invite_code": user.used_invite_code
            })


        user.used_invite_code = invite_code_input
        user.inviter = inviter
        user.save()

        return Response({"message": "Invite code accepted.", "used_invite_code": invite_code_input})
