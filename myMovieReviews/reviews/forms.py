from django import forms

from .models import Review


RATING_CHOICES = [("", "별점을 선택하세요")] + [
    (f"{score / 2:.1f}", f"{score / 2:.1f}") for score in range(0, 11)
]


class ReviewForm(forms.ModelForm):
    release_year = forms.IntegerField(
        label="개봉 년도",
        widget=forms.TextInput(attrs={"placeholder": "예: 2021"}),
        error_messages={
            "required": "개봉 년도를 입력해주세요.",
            "invalid": "개봉 년도는 숫자로 입력해주세요.",
        },
    )
    running_time = forms.IntegerField(
        label="러닝타임",
        widget=forms.TextInput(attrs={"placeholder": "분 단위로 입력, 예: 148"}),
        error_messages={
            "required": "러닝타임을 입력해주세요.",
            "invalid": "러닝타임은 분 단위 숫자로 입력해주세요.",
        },
    )

    class Meta:
        model = Review
        fields = [
            "title",
            "release_year",
            "genre",
            "rating",
            "running_time",
            "poster",
            "review",
            "director",
            "actor",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "예: 스파이더맨: 노 웨이 홈"}),
            "rating": forms.Select(choices=RATING_CHOICES),
            "poster": forms.FileInput(attrs={"accept": "image/*"}),
            "review": forms.Textarea(
                attrs={
                    "rows": 7,
                    "placeholder": "영화를 보고 느낀 점을 자유롭게 적어주세요.",
                }
            ),
            "director": forms.TextInput(attrs={"placeholder": "예: 존 왓츠"}),
            "actor": forms.TextInput(attrs={"placeholder": "예: 톰 홀랜드, 젠데이아"}),
        }
        error_messages = {
            "title": {"required": "영화 제목을 입력해주세요."},
            "genre": {"required": "장르를 선택해주세요."},
            "rating": {"required": "별점을 선택해주세요."},
            "review": {"required": "리뷰 내용을 입력해주세요."},
            "director": {"required": "감독을 입력해주세요."},
            "actor": {"required": "주연 배우를 입력해주세요."},
        }

    def clean_release_year(self):
        release_year = self.cleaned_data.get("release_year")
        if release_year is None:
            raise forms.ValidationError("개봉 년도를 입력해주세요.")
        if release_year < 1888 or release_year > 2100:
            raise forms.ValidationError("개봉 년도는 1888년부터 2100년 사이로 입력해주세요.")
        return release_year

    def clean_running_time(self):
        running_time = self.cleaned_data.get("running_time")
        if running_time is None:
            raise forms.ValidationError("러닝타임을 분 단위 숫자로 입력해주세요.")
        if running_time <= 0:
            raise forms.ValidationError("러닝타임은 1분 이상으로 입력해주세요.")
        return running_time
