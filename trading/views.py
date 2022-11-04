import datetime

#from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from .models import Market, Trade, Instrument, Plan

import pandas as pd 
import json
from django.contrib.auth.models import User

from django.forms.models import model_to_dict
from django.http import HttpResponse


class IndexView(generic.ListView):
    """
    """
    template_name = "index.html"
    context_object_name = ""

    def get_queryset(self):
        """
        """
        return Market.objects.all()

class MarketIndexView(generic.ListView):
    """
    Index view for the markets
    """
    template_name = "markets/index.html"
    context_object_name = "global_markets_list"

    def get_queryset(self):
        """
        Return all markets
        """
        return Market.objects.all()

class MarketDetailView(generic.DetailView):
    """
    Detail view for markets (this is where the order book will be displayed)
    """
    model = Market
    template_name = "markets/detail.html"

    def get_context_data(self, **kwargs):
        # get default context data
        context = super(MarketDetailView, self).get_context_data(**kwargs)
        
        # add order list to context data
        market_id = context["market"].id
        context["orders"] = Order.objects.filter(market=market_id, active=True).order_by("-type")

        return context

class TradeIndexView(generic.ListView):
    """
    """
    template_name = "trades/index.html"
    context_object_name = "global_trades_list"

    def get_queryset(self):
        """
        Return all active orders, newest to oldest
        """
        return Trade.objects.all().filter(owner_id=self.request.user).order_by("-last_modified")

class TradeDetailView(generic.DetailView):
    """
    Detail view for orders, displays information on particular order
    """
    model = Trade
    template_name = "trades/detail.html"

class TradeUpdateView(generic.UpdateView):
    model = Trade
    fields = ["owner", "market", "trade_date","strategy","code","derivative","type", "price", "quantity"]
    template_name = "trades/trade_form.html"
    #print(reverse('abcd:trades_list', args=(model.id)))
    success_url = reverse_lazy('trading:trades_list')

class TradeCreateView(generic.CreateView):
    """
    """
    model = Trade
    fields = ["market", "trade_date","strategy","code","derivative","type", "price", "quantity"]
    template_name = "trades/trade_form.html"
    success_url = reverse_lazy('trading:trades_list')

    def form_valid(self, form):
        print("form_valid")
        form.instance.owner=self.request.user
        return super().form_valid(form)


class TradeDeleteView(generic.DeleteView):
    model = Trade
    template_name = "trades/trade_confirm_delete.html"
    success_url = reverse_lazy('trading:trades_list')
    
    #def form_valid(self, form):
    #    print("form_valid")
    #    return super().form_valid(form)

class PlanIndexView(generic.ListView):
    """
    """
    template_name = "trades/plan_list.html"
    context_object_name = "global_plans_list"

    def get_queryset(self):
        """
        Return all active orders, newest to oldest
        """
        return Plan.objects.all().filter(owner_id=self.request.user).order_by("-last_modified")

class PlanCreateView(generic.CreateView):
    """
    """
    model = Plan
    fields = [ "market", "plan_date","strategy","code","details"]
    template_name = "trades/plan_form.html"
    success_url = reverse_lazy('trading:plans_list')

    def form_valid(self, form):
        print("form_valid")
        form.instance.owner=self.request.user
        return super().form_valid(form)


class PlanDeleteView(generic.DeleteView):
    model = Plan
    template_name = "trades/trade_confirm_delete.html"
    success_url = reverse_lazy('trading:plans_list')
    
    #def form_valid(self, form):
    #    print("form_valid")
    #    return super().form_valid(form)


def show_portfolio(request):

    df = pd.DataFrame(list(Trade.objects.all().filter(owner_id=request.user).order_by("-trade_date").values()))
    arr = []
    if df.empty:
        pass
    else:
        print(df)
        mask = (df.type=='S')
        df.loc[mask,'quantity'] = -1*df.loc[mask,'quantity']
        costs = pd.to_numeric(df['quantity']*df['price'])

        df= pd.concat([df, costs.rename("cost")], axis=1)
        print(df)
        grouped_df = df.groupby(by=['code_id','derivative'])['quantity','cost'].sum(numeric_only=True)
        grouped_df = grouped_df[grouped_df.quantity>0]
        print(grouped_df)

        ins_df = pd.DataFrame(list(Instrument.objects.all().values()))
        flatten_df = grouped_df.reset_index()
        print(flatten_df)

        # look up code by id and merge to df
        flatten_df['code'] = flatten_df.merge(ins_df, left_on='code_id', right_on='id')['code']

        json_records = flatten_df.to_json(orient ='records')
        print(flatten_df)
        arr = json.loads(json_records)
    contextt = {'d': arr}
    return  render(request,'trades/portfolio_list.html',contextt)


def gen_sample_data(request):

    start_amount = 100000
    stat_html = './temp/profit.html'
    np.random.seed(8)
    win_loss_df = pd.DataFrame(
        np.random.choice([1000, -1000], 543),
        index=pd.date_range("2020-01-01", "2022-01-30", freq="B"),
        columns=["win_loss_amount"]
    )
    win_loss_df["total_profit"] = win_loss_df.win_loss_amount.cumsum() + start_amount
    return win_loss_df

def get_portfolio_winloss(request):
    df = pd.DataFrame(list(Trade.objects.all().filter(owner_id=request.user).order_by("-trade_date").values()))
    # mask = (df.type=='S')
    # df.loc[mask,'quantity'] = -1*df.loc[mask,'quantity']
    amounts = pd.to_numeric(df['quantity']*df['price'])
    
    df= pd.concat([df, amounts.rename("amount")], axis=1)
    print(df)
    buy_df = df.groupby(by=['code_id','derivative','type'])['quantity','amount'].sum(numeric_only=True)
    agg_df['avg'] =agg_df['amount']/agg_df['quantity']

    grouped_df = grouped_df[grouped_df.quantity>0]
    print(grouped_df)

    ins_df = pd.DataFrame(list(Instrument.objects.all().values()))
    flatten_df = grouped_df.reset_index()
    print(flatten_df)


def get_stat(request):
    import quantstats as qs
    import numpy as np

    #win_loss_df = get_sample_data(request)
    win_loss_df = get_portfolio_winloss(request)
    profit = win_loss_df.total_profit

    # Save to image file, this image can also be seen in full report.
    qs.plots.yearly_returns(profit, savefig='./temp/yearly_return.png')

    print(f'montly returns:\n{qs.stats.monthly_returns(profit)}')
    print(f'sharpe ratio: {qs.stats.sharpe(profit)}')
    print(f'max markdown: {qs.stats.max_drawdown(profit)}')

    # Print full report in html.
    qs.reports.html(profit, figfmt='jpg',title='Porfolio stat', output='', download_filename=stat_html)
    contextt = {}
    html_content = open(stat_html)
    return HttpResponse(html_content)