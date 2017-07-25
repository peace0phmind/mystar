import urllib2
import json
import dot_dict

headers = {
    "Authorization": "bearer f16ca3824d8ca9b6ec110ace1ea99b1ed217c074"
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
              primaryLanguage {
                name
              }
              url
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

    content = dot_dict.DotDict(json.load(urllib2.urlopen(request)))

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

            print "|[%s](%s)|%s|%s|%s|%s|%s|%d|%d|%d|%s|%d|%s|" % (
                node.nameWithOwner,
                node.url,
                repo.starredAt,
                node.license,
                node.createdAt,
                node.pushedAt,
                node.primaryLanguage.name,
                node.stargazers.totalCount,
                node.forks.totalCount,
                node.pullRequests.totalCount,
                node.pullRequests.nodes[0].get("updatedAt"),
                node.commitComments.totalCount,
                node.commitComments.nodes[0].get("updatedAt")
            )

        content = get_next_page_content()
        while_count -= 1


if __name__ == '__main__':
    main()
