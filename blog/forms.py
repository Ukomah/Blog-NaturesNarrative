from django import forms
from django.shortcuts import render
from .models import Comment, Post, ContactMessage



class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Enter your name'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Enter your email address'}))
    to = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': "Enter receiver's email address"}))
    comments = forms.CharField(required=False, widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model =  Comment
        fields = ['name', 'email', 'body']



class SearchForm(forms.Form):
    query = forms.CharField()
    


class ContactForm(forms.ModelForm):
    class Meta:
        model =  ContactMessage
        fields = ['name', 'email', 'body']




