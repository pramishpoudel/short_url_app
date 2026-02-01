from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import string
import random 
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    



BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def encode_base62(num: int) -> str:
    if num == 0:
        return BASE62_ALPHABET[0]
    base = len(BASE62_ALPHABET)
    s = ''
    while num > 0:
        s = BASE62_ALPHABET[num % base] + s
        num //= base
    return s


class ShortURL(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='short_urls')
    original_url = models.URLField()
    key = models.CharField(max_length=32, unique=True, db_index=True)
    clicks = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.original_url} -> {self.key}"

    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at

    @property
    def short_path(self):
        return f"/s/{self.key}"

    def save(self, *args, **kwargs):
        # New object: save to get PK if needed to generate deterministic base62 key
        is_new = self.pk is None
        if is_new:
            # If a custom key was provided, let the initial save attempt enforce uniqueness
            super().save(*args, **kwargs)
            if not self.key:
                generated = encode_base62(self.pk)
                # ensure uniqueness (extremely unlikely for base62(pk), but handle just in case)
                key = generated
                suffix = 0
                while ShortURL.objects.filter(key=key).exists():
                    suffix += 1
                    key = f"{generated}{suffix}"
                # update directly to avoid recursion
                ShortURL.objects.filter(pk=self.pk).update(key=key)
        else:
            # On updates: if key removed, regenerate from pk
            if not self.key:
                self.key = encode_base62(self.pk)
            super().save(*args, **kwargs)

    def regenerate_key(self, suffix_len=4):
        """Regenerate the short key by appending a small random base62 suffix to the base62(pk).
        This produces a new, unique key while keeping base62(pk) as a prefix."""
        base = encode_base62(self.pk)
        alphabet = BASE62_ALPHABET
        # generate random suffix
       
        suffix = ''.join(random.choice(alphabet) for _ in range(suffix_len))
        new_key = f"{base}{suffix}"
        # ensure uniqueness
        attempts = 0
        while ShortURL.objects.filter(key=new_key).exists() and attempts < 10:
            suffix = ''.join(random.choice(alphabet) for _ in range(suffix_len))
            new_key = f"{base}{suffix}"
            attempts += 1
        if ShortURL.objects.filter(key=new_key).exists():
            # fallback - append timestamp
            import time
            new_key = f"{base}{int(time.time())}"
        self.key = new_key
        self.save()
        return self.key