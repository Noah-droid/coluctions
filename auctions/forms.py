from django import forms
from django.utils.safestring import mark_safe
from .models import User, Auction, Category, Comment, Bid

class CreateForm(forms.ModelForm):
    title = forms.CharField(label=mark_safe("<strong>Title</strong>"),
                            min_length=1,
                            max_length=100,
                            widget=forms.TextInput
                            (attrs={'class':'form-control',
				            'placeholder':'Title'
                            }))

    image = forms.URLField(label=mark_safe("<strong>Image URL</strong>"),
                            max_length=1000,
                            widget=forms.URLInput
                            (attrs={'class':'form-control',
                            'placeholder':'Image URL'
                            }))

    content = forms.CharField(label=mark_safe("<strong>Content</strong>"),
                            min_length=20,
                            max_length=1000,
                            widget=forms.Textarea
                            (attrs={'class':'form-control',
				            'placeholder':'Content'
                            }))

    starting_price = forms.DecimalField(label=mark_safe("<strong>Starting price (USD)</strong>"),
                            min_value=0.01,
                            widget=forms.NumberInput
                            (attrs={'class':'form-control',
				            'placeholder':'Starting price'
                            }))

    category = forms.ModelChoiceField(queryset=Category.objects.all(),
                            label=mark_safe("<strong>Category</strong>"),
                            required=True,
                            widget= forms.Select
                            (attrs={'class':'form-control'
                            }))
                            
    class Meta:
        model = Auction
        exclude = ["author", "date", "active", "current_price"]

class CommentForm(forms.ModelForm):
    content = forms.CharField(label=mark_safe("<strong>Type your comment below</strong>"),
                            min_length=1,
                            max_length=100,
                            widget=forms.TextInput
                            (attrs={'class':'form-control mb-2',
				            'placeholder':'Your comment'
                            }))
                            
    class Meta:
        model = Comment
        exclude = ["auction", "author", "date"]

class BidForm(forms.ModelForm):
    amount = forms.DecimalField(label=mark_safe("<strong>Place your bid</strong>"),
                            min_value=0.01,
                            widget=forms.NumberInput
                            (attrs={'class':'form-control',
				            'placeholder':'Bid amount'
                            }))
                            
    class Meta:
        model = Bid
        exclude = ["auction", "author", "date"]

class SearchForm(forms.Form):
    search = forms.CharField(label="",
                            min_length=1,
                            max_length=50,
                            widget=forms.TextInput
                            (attrs={'class':'form-control mr-sm-2',
				            'placeholder':'Name or category',
                            'type':'search',
                            'aria-label':'Search'
                            }))