DEBUG = True

SECRET_KEY = '***********'

ALLOWED_HOSTS = ['django']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '*******',
        'NAME': '*********',
        'USER': '********',
        'PASSWORD': '********',
    }
} 

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'exim'
EMAIL_PORT = 25
EMAIL_USE_TLS = False
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

