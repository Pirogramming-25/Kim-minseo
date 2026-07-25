from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['created_at', 'updated_at']
        widgets = {
            'calories': forms.NumberInput(
                attrs={
                    'step': '0.01',
                    'min': '0',
                }
            ),
            'carbohydrate': forms.NumberInput(
                attrs={
                    'step': '0.01',
                    'min': '0',
                }
            ),
            'protein': forms.NumberInput(
                attrs={
                    'step': '0.01',
                    'min': '0',
                }
            ),
            'fat': forms.NumberInput(
                attrs={
                    'step': '0.01',
                    'min': '0',
                }
            ),
        }