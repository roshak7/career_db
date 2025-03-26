
from django.conf.urls import url
from django.urls import path, include, re_path

from career import views, upload
from api.views import career_cards_view
from api import views_v2

urlpatterns = [


    # url(r'^file_upload$',   views.file_upload),
    # url(r'^career$', views.career_list),
    #
    # url(r'^career_create_new$', views.career_create_new),
    # url(r'^career/(?P<pk>[0-9]+)$', views.career_detail),
    url(r'^career_map/(?P<pk>[0-9]+)$', views_v2.career_map),
    url(r'^career_map_check/(?P<pk>[0-9]+)$', views_v2.career_map_check),
    # url(r'^career_stat/(?P<pk>[0-9]+)$', career_cards_stat),
    url(r'^career_map_save$', views_v2.career_map_save),
    # url(r'^profile$', views.career_profile),
    # url(r'^photo_upload$', views.profile_photo_upload),
    # url(r'^change_card$', views.change_card),
    url(r'^cardlist$', views_v2.card_list),
    url(r'^cardlistree$', views_v2.card_list_tree),
    url(r'^cardlistree_add_maps$', views_v2.card_list_tree_add_maps),
    #url(r'^cardlistree_add_maps$', views_v2.FileUploadView.as_view()),
    url(r'^cardlistree_new_maps$', views_v2.card_list_tree_new_map),
    url(r'^info$', views_v2.information),
    url(r'^search_position$', views_v2.position_search),
    url(r'^search_person$', views_v2.person_search),
    url(r'^person_data$', views_v2.get_person_data),
    url(r'^position_data$', views_v2.get_position_data),
    url(r'^sorganization$', views_v2.s_organization),
    url(r'^sdepartment$', views_v2.s_department),
    url(r'^sposition$', views_v2.s_position),
    url(r'^sperson$', views_v2.s_person),
    url(r'^spersonget$', views_v2.s_person_get),
    url(r'^screate$', views_v2.s_create),
    url(r'^sdataget$', views_v2.s_data_get),
    url(r'^personprofile$', views_v2.person_profile),
    url(r'^personprofile_get$', views_v2.person_profile_get),
    url(r'tpl-1$', views_v2.get_tpl),
    url(r'manual$', views_v2.get_manual),



    # url(r'^test_auth$', views.card_list_auth)

]