from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
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




@require_http_methods(["GET", "PUT"])
def profile(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)


    user = request.user
    if request.method == 'GET':
        return JsonResponse({
            'email': user.email,
            'username': user.username,
            'display_name': getattr(user, 'display_name', ''),
            'gender': getattr(user, 'gender', ''),
            'birthday': user.birthday.strftime('%Y-%m-%d') if getattr(user, 'birthday', None) else None,
            'phone_number': getattr(user, 'phone_number', ''),
            'avatar_url': (request.build_absolute_uri(user.avatar.url) if getattr(user, 'avatar', None) and user.avatar else None),
        })


    # PUT update
    try:
        data = json.loads(request.body or '{}')
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


    email = data.get('email')
    display_name = data.get('display_name')
    gender = data.get('gender')
    birthday = data.get('birthday')
    phone_number = data.get('phone_number')


    # Basic validation
    if email and get_user_model().objects.exclude(id=user.id).filter(email=email).exists():
        return JsonResponse({'error': 'Email already exists'}, status=400)


    if gender and gender not in ['male', 'female', 'other']:
        return JsonResponse({'error': 'Invalid gender'}, status=400)


    parsed_birthday = None
    if birthday:
        parsed_birthday = parse_date(birthday)
        if not parsed_birthday:
            return JsonResponse({'error': 'Invalid birthday, expected YYYY-MM-DD'}, status=400)


    # Apply updates
    if email:
        user.email = email
        # 同步 username 為 email（你的登入以 email 為主）
        user.username = email
    if display_name is not None:
        user.display_name = display_name
    if gender is not None:
        user.gender = gender
    if parsed_birthday is not None:
        user.birthday = parsed_birthday
    if phone_number is not None:
        user.phone_number = phone_number


    user.save()


    return JsonResponse({'message': 'Profile updated successfully'})




@csrf_exempt
@require_http_methods(["POST"])
def upload_avatar(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)


    if 'avatar' not in request.FILES:
        return JsonResponse({'error': 'No file provided. Use form field name "avatar"'}, status=400)


    file_obj = request.FILES['avatar']
    user = request.user
    user.avatar = file_obj
    user.save()
    return JsonResponse({
        'message': 'Avatar uploaded',
        'avatar_url': request.build_absolute_uri(user.avatar.url)
    })




