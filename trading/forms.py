from django import forms
from .models import Plan, Trade

class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ["market", "plan_date", "strategy", "code", "stoploss", "targetprice", "quantity", "current_price", "details"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notional'] = forms.CharField(
            label='Notional',
            widget=forms.TextInput(attrs={'readonly': True}),
            initial=self.instance.notional if self.instance else None, required=False
        )

    def clean_notional(self):
        # If this instance has already been saved, return the existing value
        if self.instance and self.instance.pk:
            return self.instance.notional

        # Otherwise, return the default value
        return self.fields['notional'].initial

class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = ["market", "trade_date","strategy","code","derivative","type", "price", "quantity"]
        
