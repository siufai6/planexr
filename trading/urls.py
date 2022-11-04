from django.urls import path

from . import views

app_name = "trading"
urlpatterns = [path("", views.IndexView.as_view(),
                    name="index"),
                path("plans/", views.PlanIndexView.as_view(),
                    name="plans_list"),
                path("plans/create", views.PlanCreateView.as_view(),
                    name="plans_create"),
                path("trades/", views.TradeIndexView.as_view(),
                    name="trades_list"),
                path("plans/delete/<int:pk>", views.PlanDeleteView.as_view(),
                    name="plans_delete"),
                path("trades/<int:pk>", views.TradeDetailView.as_view(),
                    name="trades_detail"),
                path("trades/update/<int:pk>", views.TradeUpdateView.as_view(),
                    name="trades_update"),
#                path("trades/create/", views.TradeCreateView.as_view(success_url="/"),
                path("trades/create/", views.TradeCreateView.as_view(),
                    name="trades_create"),
                path("trades/delete/<int:pk>", views.TradeDeleteView.as_view(),
                    name="trades_delete"),
                path("portfolios/", views.show_portfolio,name="portfolio_list"),
                path("portfolios/stat", views.get_stat,name="portfolio_stat")
]

