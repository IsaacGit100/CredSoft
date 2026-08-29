from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path("entity/<slug:slug>/pos_dashboard/", views.pos_dashboard, name="pos_dashboard"),
 #   path("entity/<slug:slug>/dashboard/", views.dashboard, name="dashboard"),
    
    
    path("entity/<slug:slug>/add-to-cart/", views.add_to_cart, name="add_to_cart"),
    path("entity/<slug:slug>/remove-from-cart/", views.remove_from_cart, name="remove_from_cart"),
    path("entity/<slug:slug>/checkout/", views.checkout, name="checkout"),
    
    

    path("entity/<slug:slug>/debtors/", views.debtor_list, name="debtor_list"),
    
    ## =========================== Products =================================
    path("entity/<slug:slug>/products/", views.product_list, name="product_list"),
    path("entity/<slug:slug>/products/add/", views.product_add, name="product_add"),
    path("entity/<slug:slug>/products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("entity/<slug:slug>/products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    
    ## ============================ Customers ==============================
    path("entity/<slug:slug>/customers/", views.customer_list, name="customer_list"),
    path("entity/<slug:slug>/customers/add/", views.customer_add, name="customer_add"),
    path("entity/<slug:slug>/customers/<int:pk>/edit/", views.customer_edit, name="customer_edit"),
    path("entity/<slug:slug>/customers/<int:pk>/delete/", views.customer_delete, name="customer_delete"),
    
    ## ===========================Sales Form ===============================
    path("entity/<slug:slug>/sales/", views.sales_form, name='sales_form'),
    path("entity/<slug:slug>/save-sale/", views.save_sale, name="save_sale"),
    path("entity/<slug:slug>/save-payment/", views.save_payment, name="save_payment"),

    path("entity/<slug:slug>/sale/<int:pk>/edit/", views.sale_edit, name="sale_edit"),
    path("entity/<slug:slug>/sale/<int:pk>/delete/", views.sale_delete, name="sale_delete"),
    



    path("entity/<slug:slug>/pending-sales/", views.pending_sales, name="pending_sales"),
    path("entity/<slug:slug>/post-sales/", views.post_selected_sales, name="post_selected_sales"),

]
