# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

@python_2_unicode_compatible
class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=255)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

from datetime import timedelta

# # Custom extensions for raters:
# References:
# -   https://stackoverflow.com/questions/28748281/extending-user-profile-in-django-1-7
# -   https://docs.djangoproject.com/en/1.9/topics/auth/customizing/
@python_2_unicode_compatible
class Rater(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # 年齢　　＿＿＿＿歳
    age = models.IntegerField(verbose_name='年齢')
    gender = models.CharField(verbose_name='性別', choices=(('男性', '男性'), ('女性', '女性')), max_length=2) # -> RadioSelect
    # ボランティアを含む日本語教師経験年数　＿＿＿＿年／なし
    volunteer_experience_time = models.IntegerField(verbose_name='ボランティアを含む日本語教師経験年数') # TODO how to pass in the right data from form?
    # 海外在留期間　　　＿＿＿＿年＿＿＿＿ヶ月／なし
    time_abroad = models.IntegerField(verbose_name='海外在留期間')
    job = models.CharField(verbose_name='職業', max_length=255, default='学生', choices=(('学生', '学生'), ('主婦', '主婦'), ('会社員', '会社員'), ('公務員', '公務員'), ('教員', '教員'), ('自営業', '自営業'), ('その他', 'その他')))

    # see: https://django-localflavor.readthedocs.org/en/latest/localflavor/jp/
    # https://github.com/yubinbango/yubinbango
    JP_PREFECTURES = [(prefecture, prefecture) for prefecture in ('北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県', '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県', '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県', '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県', '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県', '海外')]
    place_of_birth  = models.CharField(verbose_name='出身地', max_length=255, choices=JP_PREFECTURES)
    current_address = models.CharField(verbose_name='現住所', max_length=255, choices=JP_PREFECTURES)
    language_use_information = models.CharField(verbose_name='標準語・方言使用', max_length=255, choices=(('標準語と方言をどちらもよく使う', '標準語と方言をどちらもよく使う'), ('普段の生活では方言、公的な場では標準語を使用', '普段の生活では方言、公的な場では標準語を使用'), ('常時標準語を使用', '常時標準語を使用'), ('常時方言を使用', '常時方言を使用')))
    dialect_used = models.CharField(verbose_name='使用している方言', max_length=255) # TODO
    best_foreign_language = models.CharField(verbose_name='一番よく話せる外国語', max_length=255, choices=(('外国語で日常会話が出来る', '外国語で日常会話が出来る'), ('たどたどしいが意思の疎通が出来る', 'たどたどしいが意思の疎通が出来る'), ('基本的に話せない', '基本的に話せない')))
    usual_foreign_language_use = models.CharField(verbose_name='普段の生活での外国語使用', max_length=255, choices=(('日本語と同程度，あるいはそれ以上に、外国語を話す', '日本語と同程度，あるいはそれ以上に、外国語を話す'), ('仕事など特定の場面で話す', '仕事など特定の場面で話す'), ('外国語を話すことは全くないか，殆ど無い', '外国語を話すことは全くないか，殆ど無い')))
    speaking_with_foreigners = models.CharField(verbose_name='外国人と日本語で話す機会', max_length=255, choices=(('日常的にあるか、よくある', '日常的にあるか、よくある'), ('日常的ではないが、たまに話すことはある', '日常的ではないが、たまに話すことはある'), ('殆どないか、全くない', '殆どないか、全くない')))

    def __str__(self):
        return self.user.__str__()

    def get_absolute_url(self):
        return reverse('users:rater_detail', kwargs={'user': self.user.__str__()})

# Define an inline admin descriptor for Rater model
# which acts a bit like a singleton

from django.contrib import admin
from .admin import MyUserAdmin as BaseUserAdmin

@python_2_unicode_compatible
class RaterInline(admin.StackedInline):
    model = Rater
    can_delete = False
    verbose_name_plural = 'rater'

# Define a new User admin
@python_2_unicode_compatible
class UserAdmin(BaseUserAdmin):
    inlines = (RaterInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
