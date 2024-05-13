from django.urls import path, re_path
from loan.views import CreateLoanView, UpdatePaymentView, ListLoanView

urlpatterns = [
    path('', CreateLoanView.as_view(), name='create_loan'),  # post method
    re_path(r'^(?P<contract>[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12})/$',
            ListLoanView.as_view(),
            name='loan_payments',
            ),  # get method
    path('payment/<int:id>/', UpdatePaymentView.as_view(), name='payment'),  # post method
]
