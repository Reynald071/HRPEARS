import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOST").split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'mozilla_django_oidc',
    'django.contrib.humanize',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'colorfield',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_tracking',
    'dj_rest_auth',
    'crispy_forms',
    'qr_code',
    'backend.apps.BackendConfig',
    'frontend',
    'tracker',
    'epay',
    'approve_rito',
    'django_cleanup',
    'maintenance_mode',
    'admin_reorder',
    'landing',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'mozilla_django_oidc.middleware.SessionRefresh',
    # 'backend.middleware.OneSessionPerUser',
    'maintenance_mode.middleware.MaintenanceModeMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
]

ROOT_URLCONF = 'portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'maintenance_mode.context_processors.maintenance_mode',
            ],
            'libraries':{
                'tags': 'backend.templatetags.tags',
                'frontend_tags': 'frontend.templatetags.tags',
                'payroll_tags': 'backend.pas.payroll.tags',
                'welfare_tags': 'backend.welfare_intervention.intervention.tags'
            }
        },
    },
]

WSGI_APPLICATION = 'portal.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('PORTAL_DB_NAME'),
        'HOST': os.getenv('PORTAL_DB_HOST'),
        'USER': os.getenv('PORTAL_DB_USER'),
        'PASSWORD': os.getenv('PORTAL_DB_PASSWORD'),
        'PORT': os.getenv('PORTAL_DB_PORT'),
    },
    # 'payslip': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': os.getenv('CDO_PS_DB_NAME'),
    #     'HOST': os.getenv('CDO_PS_DB_HOST'),
    #     'USER': os.getenv('CDO_PS_DB_USER'),
    #     'PASSWORD': os.getenv('CDO_PS_DB_PASSWORD'),
    #     'PORT': os.getenv('DB_PORT'),
    # },
    # 'infimos20': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': os.getenv("IF20_DB_NAME"),
    #     'HOST': os.getenv("IF_DB_HOST"),
    #     'USER': os.getenv("IF_DB_USER"),
    #     'PASSWORD': os.getenv("IF_DB_PASSWORD"),
    #     'PORT': os.getenv('DB_PORT'),
    # },
    # 'infimos21': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': os.getenv("IF21_DB_NAME"),
    #     'HOST': os.getenv("IF_DB_HOST"),
    #     'USER': os.getenv("IF_DB_USER"),
    #     'PASSWORD': os.getenv("IF_DB_PASSWORD"),
    #     'PORT': os.getenv('DB_PORT'),
    # },
    # 'infimos22': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': os.getenv("IF22_DB_NAME"),
    #     'HOST': os.getenv("IF_DB_HOST"),
    #     'USER': os.getenv("IF_DB_USER"),
    #     'PASSWORD': os.getenv("IF_DB_PASSWORD"),
    #     'PORT': os.getenv('DB_PORT'),
    # },
    # 'infimos23': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': os.getenv("IF23_DB_NAME"),
    #     'HOST': os.getenv("IF_DB_HOST"),
    #     'USER': os.getenv("IF_DB_USER"),
    #     'PASSWORD': os.getenv("IF_DB_PASSWORD"),
    #     'PORT': os.getenv('DB_PORT'),
    # },
    # 'libraries': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': os.getenv("IFL_DB_NAME"),
    #     'HOST': os.getenv("IF_DB_HOST"),
    #     'USER': os.getenv("IF_DB_USER"),
    #     'PASSWORD': os.getenv("IF_DB_PASSWORD"),
    #     'PORT': os.getenv('DB_PORT'),
    # }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    }
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Manila'

USE_I18N = False

USE_L10N = False

USE_TZ = False

X_FRAME_OPTIONS = 'SAMEORIGIN'
#SESSION_EXPIRE_AT_BROWSER_CLOSE = True
#SESSION_COOKIE_AGE = 3600*8
#SESSION_SAVE_EVERY_REQUEST = True

MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE") == "True"

CRISPY_TEMPLATE_PACK = 'bootstrap3'

STATIC_URL = '/static/staticfiles/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static/staticfiles/'),]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# KEYCLOAK
OIDC_USERNAME_ALGO = 'mozilla_django_oidc.utils.generate_username'
OIDC_RP_SIGN_ALGO = 'RS256'
OIDC_RP_SCOPES = 'openid email'

LOGIN_URL = '/'

# OLD KEYCLOAK SETTING
# OIDC_RP_CLIENT_ID = 'caraga-portal'
# OIDC_RP_CLIENT_SECRET = '99aa7415-1670-4a61-a726-781ba727549b'
# OIDC_OP_JWKS_ENDPOINT = 'https://caraga-auth.dswd.gov.ph:8443/auth/realms/entdswd.local/protocol/openid-connect/certs'
# OIDC_OP_AUTHORIZATION_ENDPOINT = 'https://caraga-auth.dswd.gov.ph:8443/auth/realms/entdswd.local/protocol/openid-connect/auth'
# OIDC_OP_TOKEN_ENDPOINT = 'https://caraga-auth.dswd.gov.ph:8443/auth/realms/entdswd.local/protocol/openid-connect/token'
# OIDC_OP_USER_ENDPOINT = 'https://caraga-auth.dswd.gov.ph:8443/auth/realms/entdswd.local/protocol/openid-connect/userinfo'
# OIDC_OP_LOGOUT_ENDPOINT = 'https://caraga-auth.dswd.gov.ph:8443/auth/realms/entdswd.local/protocol/openid-connect/logout'
# OIDC_OP_LOGOUT_URL_METHOD = "backend.views.logout"


# NEW KEYCLOAK SETTING
OIDC_RP_CLIENT_ID = 'caraga-portal-staging'
OIDC_RP_CLIENT_SECRET = 'VKOBtKCNhE5Kva8RGD2LgjeruDosHdM5'
OIDC_OP_JWKS_ENDPOINT = 'https://caraga-auth-staging.dswd.gov.ph/auth/realms/entdswd.local/protocol/openid-connect/certs'
OIDC_OP_AUTHORIZATION_ENDPOINT = 'https://caraga-auth-staging.dswd.gov.ph/auth/realms/entdswd.local/protocol/openid-connect/auth'
OIDC_OP_TOKEN_ENDPOINT = 'https://caraga-auth-staging.dswd.gov.ph/auth/realms/entdswd.local/protocol/openid-connect/token'
OIDC_OP_USER_ENDPOINT = 'https://caraga-auth-staging.dswd.gov.ph/auth/realms/entdswd.local/protocol/openid-connect/userinfo'
OIDC_OP_LOGOUT_ENDPOINT = 'https://caraga-auth-staging.dswd.gov.ph/auth/realms/entdswd.local/protocol/openid-connect/logout'
OIDC_OP_LOGOUT_URL_METHOD = "backend.views.logout"


LOGIN_REDIRECT_URL = '/dashboard'
LOGOUT_REDIRECT_URL = '/'

# IMAGE RESIZE
DJANGORESIZED_DEFAULT_SIZE = [1920, 1080]
DJANGORESIZED_DEFAULT_QUALITY = 80
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_FORCE_FORMAT = 'JPEG'
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {'JPEG': ".jpg"}
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True

# GOOGLE CAPTCHA
GOOGLE_RECAPTCHA_SECRET_KEY = os.getenv('GOOGLE_RECAPTCHA_SECRET_KEY')

# DJANGO REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework_datatables.filters.DatatablesFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
}

# SMTP GMAIL
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

ADMIN_REORDER = (
    # Keep original label and models
    'sites',
    {'app': 'authtoken'},
    {'app': 'auth', 'models': ('auth.Group', 'auth.User', 'backend.AuthPermission', )},
    {
        'app': 'backend',
        'label': 'Awards',
        'models': ('backend.Awards', 'backend.Badges', 'backend.Classification', 'backend.Awlevels', 'backend.Awcategory')
    },
    {
        'app': 'backend',
        'label': 'Calendar',
        'models': ('backend.CalendarType',)
    },
    {
        'app': 'frontend',
        'label': 'Descriptive',
        'models': ('frontend.Bloodtype', 'frontend.Civilstatus', 'frontend.Hobbies')
    },
    {
        'app': 'backend',
        'label': 'Directory',
        'models': ('backend.DirectoryDetailType',)
    },
    {
        'app': 'backend',
        'label': 'Documents',
        'models': (
            'backend.Docs201Type',
            'backend.ClearanceContent',
            'frontend.DownloadableformsClass',
            'backend.DocsIssuancesType',
            'frontend.DownloadableformsSopClass',
        )
    },
    {
        'app': 'frontend',
        'label': 'Education',
        'models': (
            'frontend.Honors',
            'frontend.Degree',
            'frontend.Educationlevel',
            'frontend.Eligibility',
            'frontend.School',
        )
    },
    {
        'app': 'backend',
        'label': 'Employees',
        'models': (
            'backend.Fundsource',
            'backend.Aoa',
            'backend.Project',
            'backend.Position',
            'backend.Empstatus',
            'backend.Division',
            'backend.Section',
            'backend.Designation',
            'backend.HrppmsModeaccession',
            'backend.HrppmsModeseparation',
        )
    },
    {
        'app': 'backend',
        'label': 'Leave',
        'models': ('backend.LeaveType', 'backend.LeaveSubtype', 'backend.LeaveSpent', 'backend.LeavePermissions')
    },
    {
        'app': 'frontend',
        'label': 'Location',
        'models': ('frontend.Brgy', 'frontend.City', 'frontend.Province', 'frontend.Countries',)
    },
    {
        'app': 'frontend',
        'label': 'Others',
        'models': ('frontend.Organization', 'frontend.Nonacad',)
    },
    {
        'app': 'backend',
        'label': 'Payroll',
        'models': ('backend.PayrollIncharge', )
    },
    {
        'app': 'frontend',
        'label': 'Training',
        'models': ('frontend.Trainingtitle', 'frontend.Trainingtype',)
    },
    {
        'app': 'frontend',
        'label': 'Travel',
        'models': ('frontend.Claims', 'frontend.Mot')
    },
    {
        'app': 'landing',
        'label': 'Recruitment & Onboarding',
        'models': ('landing.AppStatus',)
    },
    {
        'app': 'backend',
        'label': 'Positions',
        'models': ('backend.PositionVacancy',)
    },
    {
        'app': 'backend',
        'label': 'Payroll',
        'models': ('backend.PayrollIncharge',)
    },
    {'app': 'rest_framework_tracking'},
)
