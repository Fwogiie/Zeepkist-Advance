post_url = "https://graphql-beta.zeepki.st/"

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

get_level_leaderboard = """query getLevelLeaderboard($idLevel: Int) {
  allRecords(condition: {idLevel: $idLevel}, orderBy: TIME_ASC) {
    edges {
      node {
        time
        userByIdUser {
          steamName
        }
      }
    }
  }
}"""

get_level_leaderboard_by_players = """query getLevelLeaderboardByPlayers($in: [Int!], $idLevel: Int) {
  allRecords(
    orderBy: TIME_ASC
    filter: {idUser: {in: $in}}
    condition: {idLevel: $idLevel}
  ) {
    edges {
      node {
        time
        userByIdUser {
          steamName
        }
      }
    }
  }
}"""

get_user_pb_by_id = """query getUserPbById($in: [Int!] = 10, $idLevel: Int = 10, $lessThan: Datetime = "") {
  allUsers(filter: {id: {in: $in}}) {
    nodes {
      recordsByIdUser(
        condition: {idLevel: $idLevel}
        orderBy: TIME_ASC
        first: 1
        filter: {dateUpdated: {lessThan: $lessThan}, dateCreated: {lessThan: $lessThan}}
      ) {
        edges {
          node {
            time
            userByIdUser {
              steamName
            }
          }
        }
      }
    }
  }
}"""