from django.urls import path
from . import views

urlpatterns = [
    path("", views.crew_list),
    path("<int:crew_id>/", views.crew_detail),
    path("<int:crew_id>/join/", views.crew_join),
    path("<int:crew_id>/favorite/", views.crew_favorite),
    path("opened/top6/", views.crew_opened_top6),
    path("<int:crew_id>/reviews/", views.crew_review_list_create),
    path("<int:crew_id>/reviews/<int:review_id>/", views.crew_review_update_delete),
    path("manage/create/", views.crew_create),
    path("manage/<int:crew_id>/", views.crew_detail),
    path("manage/<int:crew_id>/update/", views.crew_update),
    path("manage/<int:crew_id>/members/", views.crew_member_list),
    path("manage/<int:crew_id>/members/<int:member_id>/", views.crew_member_update),
]