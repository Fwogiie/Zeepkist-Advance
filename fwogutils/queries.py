post_url = "https://graphql.zeepki.st/"

top_gtr = """query TopGtrLevels($first: Int, $offset: Int) {
  allLevelPoints(orderBy: POINTS_DESC, first: $first, offset: $offset) {
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

rankings = """query GetRankings($offset: Int, $limit: Int) {
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

levels_from_ids = """query GetLevelsFromIds($in: [BigFloat!] = "") {
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

get_user_pos = """query GetUserRanking($id: Int) {
  allUsers(condition: {id: $id}) {
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