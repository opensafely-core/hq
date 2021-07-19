from django.db import models


class Repo(models.Model):

    owner = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ("owner", "name")

    def __str__(self):
        return f"{self.owner}/{self.name}"
