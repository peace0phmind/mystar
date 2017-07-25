import urllib2
import json
import dot_dict

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

ONE_PAGE_SIZE = 1
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

    content = dot_dict.DotDict(json.loads(urllib2.urlopen(request).read().decode('utf-8')))

    repos_size = len(content.data.viewer.starredRepositories.edges)
    if repos_size != 0:
        g_cursor = content.data.viewer.starredRepositories.edges[repos_size - 1].get("cursor")

    return content


def main():
    while_count = 1

    content = get_next_page_content()

    while len(content.data.viewer.starredRepositories.edges) != 0 and while_count > 0:
        for repo in content.data.viewer.starredRepositories.edges:
            repo = dot_dict.DotDict(repo)
            node = repo.node

            repo_line = u"""
[//]: # ({} start)

## [{}]({}) 
| watchs: {} | stars: {} | forks: {} | license: {} |
| :--- | :--- | :--- | :--- |
| PL: {} | starredAt: {:.10s} | createdAt: {:.10s} | pushedAt: {:.10s} |
| prCount: {} | prUpdatedAt: {:.10s} | cmCount: {} | cmUpdatedAt: {:.10s} |
- {}

[//]: # ({} start)
""".format(
                node.nameWithOwner,

                node.nameWithOwner,
                node.url,

                node.watchers.totalCount,
                node.stargazers.totalCount,
                node.forks.totalCount,
                node.license,

                node.primaryLanguage.name,
                repo.starredAt,
                node.createdAt,
                node.pushedAt,

                node.pullRequests.totalCount,
                node.pullRequests.nodes[0].get("updatedAt"),
                node.commitComments.totalCount,
                node.commitComments.nodes[0].get("updatedAt"),

                node.description,

                node.nameWithOwner,
            )

            print repo_line

        content = get_next_page_content()
        while_count -= 1


if __name__ == '__main__':
    main()
