post_url = "https://graphql.zeepkist-gtr.com"

top_gtr = """query MyQuery($first: Int) {
  allLevelPoints(orderBy: POINTS_DESC, first: $first) {
    nodes {
      levelByIdLevel {
        levelItemsByIdLevel(first: 1) {
          nodes {
            workshopId
            name
            fileAuthor
            fileUid
          }
        }
      }
    }
  }
}
"""