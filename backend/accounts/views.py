from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
import json

User = get_user_model()

# Create your views here.

@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)
            
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)
            
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        
        # 自動登入新註冊的用戶
        login(request, user)
        
        return JsonResponse({
            'message': 'User registered successfully',
            'user': {
                'email': user.email,
                'username': user.username
            }
        }, status=201)
    except Exception as e:
        print(f"Registration error: {str(e)}")  # 添加服務器端日誌
        return JsonResponse({'error': 'Registration failed. Please try again.'}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)
        
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                'message': 'Login successful',
                'user': {
                    'email': user.email,
                    'username': user.username
                }
            })
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    except Exception as e:
        print(f"Login error: {str(e)}")  # 添加服務器端日誌
        return JsonResponse({'error': 'Login failed. Please try again.'}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    try:
        logout(request)
        return JsonResponse({'message': 'Logout successful'})
    except Exception as e:
        print(f"Logout error: {str(e)}")  # 添加服務器端日誌
        return JsonResponse({'error': 'Logout failed'}, status=400)

@require_http_methods(["GET"])
def check_auth(request):
    if request.user.is_authenticated:
        return JsonResponse({
            'is_authenticated': True,
            'user': {
                'email': request.user.email,
                'username': request.user.username
            }
        })
    return JsonResponse({'is_authenticated': False}, status=401)
