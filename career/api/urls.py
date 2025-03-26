
from django.conf.urls import url
from django.urls import path, include
from career import views, upload
from api.views import career_cards_view
from career.views import get_image

urlpatterns = [


    url(r'^file_upload$',   views.file_upload),
    url(r'^career$', views.career_list),

    url(r'^career_create_new$', views.career_create_new),
    url(r'^career/(?P<pk>[0-9]+)$', views.career_detail),
    url(r'^career_new/(?P<pk>[0-9]+)$', career_cards_view),
    # url(r'^career_stat/(?P<pk>[0-9]+)$', career_cards_stat),
    url(r'^careersave$', views.career_save),
    url(r'^profile$', views.career_profile),
    url(r'^profile_file$', views.career_profile_file),
    url(r'^photo_upload$', views.profile_photo_upload),
    url(r'^change_card$', views.change_card),
    url(r'^cardlist$', views.card_list),
    url(r'^upload_zip$', views.map_zip_upload), # загрузить архивную карту с фото
    url(r'^download_zip/((?P<id>\w+)/)?$', views.map_zip_download), # выгрузить карту в архив с фото
    path("img/<slug:id>/", get_image),
    path("profile_file/<slug:personId>/", views.career_profile_file),

    # url(r'^test_auth$', views.card_list_auth)

]