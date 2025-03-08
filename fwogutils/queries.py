post_url = "https://graphql.zeepki.st/"

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

rankings = """query MyQuery($offset: Int, $limit: Int) {
  allUserPoints(offset: $offset, first: $limit, orderBy: RANK_ASC) {
    nodes {
      points
      rank
      worldRecords
      userByIdUser {
        steamName
        discordId
        steamId
      }
    }
  }
}
"""

levels_from_ids = """query MyQuery($in: [BigFloat!] = "") {
  allLevelItems(filter: {workshopId: {in: $in}}) {
    edges {
      node {
        fileUid
        fileAuthor
        workshopId
        deleted
        name
      }
    }
  }
}"""

get_user_pos = """query MyQuery($discordId: BigFloat) {
  allUsers(condition: {discordId: $discordId}) {
    edges {
      node {
        userPointsByIdUser {
          edges {
            node {
              rank
            }
          }
        }
      }
    }
  }
}"""