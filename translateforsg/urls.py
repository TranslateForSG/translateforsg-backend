"""translateforsg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from translations.views import PhraseViewSet, LanguageViewSet, CategoryViewSet, TranslationViewSet, ContributorViewSet, \
    UserTypeViewSet, TranslationFeedbackViewsSet, ContactViewsSet, DownloadableViewSet, SectionViewSet

router = SimpleRouter()

router.register('phrases', PhraseViewSet, 'phrase')
router.register('languages', LanguageViewSet, 'language')
router.register('categories', CategoryViewSet, 'category')
router.register('translations', TranslationViewSet, 'translation')
router.register('contributors', ContributorViewSet, 'contributor')
router.register('userTypes', UserTypeViewSet, 'user_type')
router.register('translationFeedbacks', TranslationFeedbackViewsSet, 'translation_feedback')
router.register('contacts', ContactViewsSet, 'contact')
router.register('downloadables', DownloadableViewSet, 'downloadable')
router.register('sections', SectionViewSet, 'section')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls))
]
