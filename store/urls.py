from django.urls import path
from . import views
from django.urls import reverse_lazy
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

urlpatterns = [
    path('register/',views.registerPage,name="register"),
    path('login/',views.loginPage,name="login"),
    path('logout/',views.logoutUser,name="logout"),path('reset-password/', PasswordResetView.as_view(
        template_name= 'accounts/reset_password.html',
        success_url=reverse_lazy('password_reset_done'),
        email_template_name= 'accounts/reset_password_email.html'
    ), name='reset_password'),

    path('reset-password/done/',PasswordResetDoneView.as_view(
        template_name= 'accounts/reset_password_done.html'
    ),name= 'password_reset_done'),
    path('reset-password/confirm/<uidb64>/<token>/',PasswordResetConfirmView.as_view(
        template_name= 'accounts/reset_password_confirm.html',
         success_url=reverse_lazy('password_reset_complete'),
    ),name= 'password_reset_confirm' ),
    path('reset-password/complete/',PasswordResetCompleteView.as_view(
        template_name= 'accounts/reset_password_complete.html'
    ),name ='password_reset_complete'),
    path('account/',views.viewAccount,name='account'),
    path('account/edit/',views.accountSettings,name='edit_account'),
    path('change-password/',views.change_password,name = 'change_password'),
    path('',views.store,name="store"),
    path('cart/',views.cart,name="cart"),
    path('checkout/',views.checkout,name="checkout"),
    path('view/<str:pk>/',views.productView,name="view"),
    path('delete_review/<str:pk>/',views.deleteReview,name="delete_review"),
    path('update_item/',views.updateItem, name="update_item"),
    path('process_order/',views.processOrder, name="process_order"),
]