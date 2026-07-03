from django import forms
from django.core.files.storage import default_storage

from .models import DevTool, Idea


class IdeaForm(forms.ModelForm):
    clear_image = forms.BooleanField(
        label="현재 이미지 삭제",
        required=False,
        widget=forms.CheckboxInput(),
    )
    interest = forms.IntegerField(
        label="관심도",
        min_value=0,
        widget=forms.NumberInput(attrs={"min": 0, "placeholder": "예: 10"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_image_name = (
            self.instance.image.name if self.instance and self.instance.pk and self.instance.image else ""
        )
        if not self.original_image_name:
            self.fields.pop("clear_image")

    class Meta:
        model = Idea
        fields = ["title", "image", "content", "interest", "devtool"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "예: AI 여행 플래너"}),
            "image": forms.FileInput(attrs={"accept": "image/*"}),
            "content": forms.Textarea(attrs={"rows": 8, "placeholder": "아이디어 내용을 적어주세요."}),
        }
        error_messages = {
            "title": {"required": "제목을 입력해주세요."},
            "content": {"required": "내용을 입력해주세요."},
            "devtool": {"required": "개발툴을 선택해주세요."},
        }

    def save(self, commit=True):
        idea = super().save(commit=False)
        self._sync_image_file(idea)

        if commit:
            idea.save()
            self.save_m2m()
        return idea

    def _sync_image_file(self, idea):
        if not self.original_image_name:
            return

        if self._should_clear_image():
            default_storage.delete(self.original_image_name)
            idea.image = ""
        elif self._has_replaced_image(idea):
            default_storage.delete(self.original_image_name)

    def _should_clear_image(self):
        return self.cleaned_data.get("clear_image", False) and not self.files.get("image")

    def _has_replaced_image(self, idea):
        return bool(self.files.get("image")) and self.original_image_name != idea.image.name


class DevToolForm(forms.ModelForm):
    class Meta:
        model = DevTool
        fields = ["name", "kind", "content"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "예: Django"}),
            "kind": forms.TextInput(attrs={"placeholder": "예: Backend Framework"}),
            "content": forms.Textarea(attrs={"rows": 8, "placeholder": "개발툴 설명을 적어주세요."}),
        }
        error_messages = {
            "name": {"required": "이름을 입력해주세요."},
            "kind": {"required": "종류를 입력해주세요."},
            "content": {"required": "설명을 입력해주세요."},
        }
