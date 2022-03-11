from django.urls import path, include
from dashboard.views import * 
urlpatterns = [

    path('', dashboard, name='dashboard'),
    path('client_listing',ClientListing.as_view(), name='client_listing'),
    path('client',Client.as_view(), name='client'),
    path('update_client/<id>',update.as_view(), name='client_updated'),  
    path('assesment/<id>',assesment.as_view(), name='assesment'), 
    path('stassesment_table/<id>',STassesmentTable.as_view(), name='stassesment_table'),
    path('otassesment_table/<id>',OTAssesmentTable.as_view(), name='otassesment_table'),
    path('assesment_listing',AssessmentListing.as_view(), name='assesment_listing'),
    path('create_user',CreateUser.as_view(), name='create_user'),
    path('user_listing',UserListing.as_view(), name='user_listing'),
    path('update_btassesment/<id>',UpdateBtAssessment.as_view(), name='update_btassesment'),
    path('update_stassesment/<id>',UpdateStAssessment.as_view(), name='update_stassesment'),
    path('update_otassesment/<id>',UpdateOtAssessment.as_view(), name='update_otassesment'),
    path('login',login_user, name='login'),
    path('logout',logout_user, name='logout'),
    path('update_user/<id>',UpdateUser.as_view(), name='update_user'),
    path("download_pdf_file/<id>", download_pdf_file, name="download_pdf_file")

]