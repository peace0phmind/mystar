import urllib2
import json
import dot_dict
import io
import re

with open('.token', 'r') as token_file:
    token = token_file.read().replace('\n', '')

headers = {
    "Authorization": "bearer " + token
}

data = """{
    "query":
    "query {
      viewer {
        starredRepositories(first: %d, %s) {
          totalCount
          edges {
            cursor
            node {
              nameWithOwner
              description
              createdAt
              pushedAt
              license
              url
              primaryLanguage {
                name
              }
              watchers {
                totalCount
              }
              stargazers {
                totalCount
              }
              forks {
                totalCount
              }
              pullRequests(last: 1) {
                totalCount
                nodes {
                  updatedAt
                }
              }
              commitComments(last: 1) {
                totalCount
                nodes {
                  updatedAt
                }
              }
            }
            starredAt
          }
        }
      }
    }"
}"""

ONE_PAGE_SIZE = 100
# global g_cursor
g_cursor = None


def get_next_page_content():
    global g_cursor

    payload = data.translate(None, '\n')

    if g_cursor:
        payload = payload % (ONE_PAGE_SIZE, "after: \\\"%s\\\" " % g_cursor)
    else:
        payload = payload % (ONE_PAGE_SIZE, "")

    # print payload

    request = urllib2.Request("https://api.github.com/graphql", payload, headers)
    # request.get_method = lambda: 'POST'

    content = dot_dict.DotDict(json.load(urllib2.urlopen(request)))

    repos_size = len(content.data.viewer.starredRepositories.edges)
    if repos_size != 0:
        g_cursor = content.data.viewer.starredRepositories.edges[repos_size - 1].get("cursor")

    return content


def main():
    # while_count = 3

    content = get_next_page_content()
    total_count = content.data.viewer.starredRepositories.totalCount

    print "total_count: {}".format(total_count)

    with io.open("README.md", "r", encoding="utf8") as f:
        readme_file_data = f.read()

    while len(content.data.viewer.starredRepositories.edges) != 0:
        for repo in content.data.viewer.starredRepositories.edges:
            repo = dot_dict.DotDict(repo)
            node = repo.node

            repo_line = u"""
[//]: # (github_star:{} start)

## [{}]({})
- {}

| watchs: {} | stars: {} | forks: {} | license: {} |
| :--- | :--- | :--- | :--- |
| PL: {} | starredAt: {:.10s} | createdAt: {:.10s} | pushedAt: {:.10s} |
| prCount: {} | prUpdatedAt: {:.10s} | cmCount: {} | cmUpdatedAt: {:.10s} |

[//]: # (github_star:{} end)
""".format(
                node.nameWithOwner,

                node.nameWithOwner,
                node.url,

                node.description,

                node.watchers.totalCount,
                node.stargazers.totalCount,
                node.forks.totalCount,
                node.license,

                node.primaryLanguage.name if node.primaryLanguage else None,
                repo.starredAt,
                node.createdAt,
                node.pushedAt,

                node.pullRequests.totalCount,
                node.pullRequests.nodes[0].get("updatedAt") if len(node.pullRequests.nodes) > 0 else None,
                node.commitComments.totalCount,
                node.commitComments.nodes[0].get("updatedAt") if len(node.commitComments.nodes) > 0 else None,

                node.nameWithOwner,
            )

            repo_r = ur"\n\[//\]: # \(github_star:{} start\)(?:.|\n)+\[//\]: # \(github_star:{} end\)\n".format(
                node.nameWithOwner, node.nameWithOwner)

            if re.search(repo_r, readme_file_data, re.M):
                readme_file_data = re.sub(repo_r, repo_line, readme_file_data, flags=re.M)
            else:
                readme_file_data += repo_line

            total_count -= 1

        content = get_next_page_content()

        print "residue total_count: {}".format(total_count)

    with io.open("./README.md", "w", encoding="utf8") as f:
        f.write(readme_file_data)


if __name__ == '__main__':
    main()
