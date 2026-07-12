from django.db import models

class SearchHistory(models.Model):
  city= models.CharField(max_length=255)
  country= models.CharField(max_length=255)
  searched_at = models.DateTimeField(auto_now_add=True)
# auto_now_add=True — tự động set thời điểm hiện tại khi tạo record, không cần truyền vào thủ công.

class FavoriteCity(models.Model):
  city= models.CharField(max_length=255)
  country= models.CharField(max_length=255)
  added_at = models.DateTimeField(auto_now_add=True)