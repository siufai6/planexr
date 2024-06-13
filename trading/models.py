from datetime import datetime, date
from decimal import Decimal
from unittest.util import _MAX_LENGTH

from django.db import models

from django.contrib.auth.models import User

TRADE_TYPES = [
    ('B', 'Buy'),
    ('S', 'Sell'),
]

OPEN_CLOSE_TYPES = [
    ('O', 'Open'),
    ('C', 'Close'),
]



class Trader(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, unique=True)
    def __str__(self):
        return self.name


class Market(models.Model):
    """
    Represents a market to be traded in.

    Essentially wraps PyOBSim's Book class.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=5)
    last_modified = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Participant(models.Model):
    """
    Represents a trader in the marketplace.

    Essentially wraps PyOBSim's Participant class.
    """
    id = models.AutoField(primary_key=True)
    trader = models.ForeignKey(Trader, on_delete=models.CASCADE)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)

    name = models.CharField(max_length=32, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.IntegerField()

    def __str__(self):
        return self.name




class Instrument(models.Model):
    id = models.AutoField(primary_key=True)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    # metadata
    last_modified = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        s = "{0} - {1}".format(str(self.code),
                str(self.name))
        return s



class Strategy(models.Model):
    id = models.AutoField(primary_key=True)
    strategy = models.CharField(max_length=20, default='Dividend')

    def __str__(self) -> str:
        return self.strategy


class Plan(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    code = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    plan_date = models.DateField( default=date.today)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    stoploss = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    targetprice= models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    notional= models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    risk= models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    profit= models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    details = models.TextField()

    def calculate_risk(self):
        if self.current_price and self.stoploss and self.quantity:
            return (Decimal(self.current_price) - Decimal(self.stoploss)) * self.quantity

    def calculate_profit(self):
        if self.current_price and self.targetprice and self.quantity:
            return (Decimal(self.targetprice) - Decimal(self.current_price)) * self.quantity
        
    def calculate_notional(self):
        if self.current_price and self.quantity:
            return Decimal(self.current_price) * self.quantity
    notional = property(calculate_notional)  
    risk = property(calculate_risk)  
    profit = property(calculate_profit)  
    
    # metadata
    last_modified = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        s = "{0} - {1} - {2} -{3}".format(str(self.market),
                str(self.code), str(self.strategy), str(self.details))
        return s


class Trade(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    type = models.CharField(max_length=4, choices=TRADE_TYPES)
    openclose = models.CharField(max_length=4, choices=OPEN_CLOSE_TYPES, default='O')
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE, default=1)
    trade_date = models.DateField( default=date.today)
    code = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    derivative = models.CharField(max_length=20, default='-')
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    closes_trade_id = models.BigIntegerField(null=True)  # contains trade ID that the current trade closes

    # metadata
    last_modified = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.last_modified:
            self.last_modified = datetime.now()

        return super(Trade, self).save(*args, **kwargs)

    def get_type_display(self):
        return dict(TRADE_TYPES)[self.type]

    def __str__(self):
        s = "Trade ({0}, {1}, {2}, {3}, {4}, {5},{6})".format(str(self.owner),
                str(self.market), self.type, self.code, self.price, self.quantity, self.trade_date)
        return s

    def get_absolute_url(self):
        return "/trading/trades/%i" % self.id