from django.shortcuts import render
from osgithub import GithubClient

from .models import Repo


def landing(request):
    urls_expire_after = {
        "*/pulls": 60,  # expire requests to get pull requests after 60 secs
        "*/branches": 60 * 5,  # expire requests to get branches after 5 mins
        "*/commits": 30,  # expire requests to get commits after 30 secs
    }
    client = GithubClient(
        use_cache=True, expire_after=60 * 60, urls_expire_after=urls_expire_after
    )
    repos = [client.get_repo(repo.owner, repo.name) for repo in Repo.objects.all()]
    context = {"repos": repos}
    return render(request, "dashboard/landing.html", context)
