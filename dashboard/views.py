from django.shortcuts import render

from .github import GithubClient
from .models import Repo


def landing(request):
    client = GithubClient(use_cache=False)
    repos = [
        client.get_repo(f"{repo.owner}/{repo.name}") for repo in Repo.objects.all()
    ]
    context = {"repos": repos}
    return render(request, "dashboard/landing.html", context)
