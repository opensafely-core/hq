import json

import requests
import requests_cache
from environs import Env
from furl import furl


env = Env()


class GithubAPIException(Exception):
    ...


class GithubClient:
    """
    A connection to the Github API, using cached requests by default
    """

    user_agent = "OpenSAFELY Repo Dashboard"
    base_url = "https://api.github.com"

    def __init__(self, use_cache=True):
        token = env.str("GITHUB_TOKEN", None)
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": self.user_agent,
        }
        if token:
            self.headers["Authorization"] = f"token {env.str('GITHUB_TOKEN')}"
        if use_cache:
            self.session = requests_cache.CachedSession(
                backend="sqlite",
                cache_name=env.str("REQUESTS_CACHE_NAME", "http_cache"),
            )
        else:
            self.session = requests.Session()

    def _get_json(self, path_segments, **add_args):
        """
        Builds and calls a url from the base and path segments
        Returns the response as json
        """
        f = furl(self.base_url)
        f.path.segments += path_segments
        if add_args:
            f.add(add_args)
        response = self.session.get(f.url, headers=self.headers)

        # Report some expected errors
        if response.status_code == 403:
            errors = response.json().get("errors")
            if errors:
                for error in errors:
                    if error["code"] == "too_large":
                        raise GithubAPIException("Error: File too large")
            else:
                raise GithubAPIException(json.dumps(response.json()))
        elif response.status_code == 404:
            raise GithubAPIException(response.json()["message"])
        # raise any other unexpected status
        response.raise_for_status()
        response_json = response.json()
        return response_json

    def get_repo(self, owner_and_repo):
        """
        Ensure a repo exists and return a GithubRepo
        """
        owner, repo = owner_and_repo.split("/")
        repo_path_seqments = ["repos", owner, repo]
        # call it to raise exceptions in case it doesn't exist
        self._get_json(repo_path_seqments)
        return GithubRepo(self, owner, repo)


class GithubRepo:
    """
    Fetch contents of a Github Repo
    """

    def __init__(self, client, owner, name, url=None):
        self.client = client
        self.owner = owner
        self.name = name
        self.repo_path_segments = ["repos", owner, name]
        self._url = url

    @property
    def url(self):
        if self._url is None:
            self._url = f"https://github.com/{self.owner}/{self.name}"
        return self._url

    def get_pull_requests(self):
        path_segments = [*self.repo_path_segments, "pulls"]
        return self.client._get_json(path_segments, state="open")

    @property
    def open_pull_request_count(self):
        return len(self.get_pull_requests())

    def get_branches(self):
        path_segments = [*self.repo_path_segments, "branches"]
        return self.client._get_json(path_segments)

    @property
    def branch_count(self):
        return len(self.get_branches())

    def get_commits_for_file(self, path, ref):
        path_segments = [*self.repo_path_segments, "commits"]
        response = self.client._get_json(path_segments, sha=ref, path=path)
        return response
