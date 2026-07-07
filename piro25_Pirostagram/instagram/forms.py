from django import forms

from .models import Post, PostImage, Profile


class PostForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = Post
        fields = ["caption", "location"]
        widgets = {
            "caption": forms.Textarea(attrs={"rows": 10, "placeholder": "문구를 입력하세요."}),
            "location": forms.TextInput(attrs={"placeholder": "위치를 입력하세요."}),
        }

    def save(self, commit=True, author=None):
        post = super().save(commit=False)
        if author is not None:
            post.author = author
        if commit:
            post.save()
            image = self.cleaned_data.get("image")
            if image:
                post.images.all().delete()
                PostImage.objects.create(post=post, image=image)
        return post


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    def clean(self, data, initial=None):
        files = data if isinstance(data, (list, tuple)) else [data]
        cleaned_files = [forms.ImageField.clean(self, file, initial) for file in files if file]
        if self.required and not cleaned_files:
            raise forms.ValidationError("스토리에 올릴 사진을 선택하세요.")
        return cleaned_files


class StoryImageForm(forms.Form):
    images = MultipleImageField(
        widget=MultipleFileInput(attrs={"multiple": True, "accept": "image/*"}),
        required=True,
    )


class ProfileAvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar"]
