import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import timedelta


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# .env 파일의 경로 설정
dotenv_path = os.path.join(BASE_DIR, '.env')
# .env 파일 로드
load_dotenv(dotenv_path)

# .env.example 파일 참고바람.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG')

ALLOWED_HOSTS = ["*"]


# Application definition
INSTALLED_APPS = [
    'corsheaders', # cors 최상단에 위치
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # custom app for darlim
    'accounts',
    'boards',
    'crews',
    'promotions',
    'races',
    # install app
    'rest_framework',
    'rest_framework.authtoken', # 토큰 인증
    'rest_framework_simplejwt',
    'dj_rest_auth',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',
    'drf_spectacular',
    'multiselectfield'
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'), # 운영체제 호환을 위해 추가.
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "accounts.CustomUser"

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# dj-rest-auth
REST_USE_JWT = True # JWT 사용 여부
JWT_AUTH_COOKIE = 'my-app-auth' # 호출할 Cookie Key 값
JWT_AUTH_REFRESH_COOKIE = 'my-refresh-token' # Refresh Token Cookie Key 값
REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'accounts.serializers.CustomUserSerializer',
}

# django-allauth
SITE_ID = 1 # 해당 도메인 id
ACCOUNT_UNIQUE_EMAIL = True # User email unique 사용 여부
ACCOUNT_USERNAME_REQUIRED = False # User username 필수 여부
ACCOUNT_EMAIL_REQUIRED = True # User email 필수 여부
ACCOUNT_AUTHENTICATION_METHOD = 'email' # 로그인 인증 수단
ACCOUNT_EMAIL_VERIFICATION = 'none' # email 인증 필수 여부

# JWT 예시 (회의 후 수정하면 됩니다.)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# swagger 설정
SPECTACULAR_SETTINGS = {
    'TITLE': 'dalim_api',
    'DESCRIPTION': '오름캠프 final project <dalim> API',
    'VERSION': '1.0.0',
}