post_url = "https://graphql.zeepki.st/"

top_gtr = """query TopGtrLevels($first: Int, $offset: Int) {
  levels(
    orderBy: LEVEL_POINT_MAX_POINTS_DESC
    first: $first
    offset: $offset
    filter: {levelItems: {some: {levelId: {isNull: false}}}}
  ) {
    nodes {
      levelItems(first: 1) {
        nodes {
          fileUid
          fileAuthor
          name
          workshopId
        }
      }
    }
  }
}
"""

rankings = """query GetRankings($offset: Int, $limit: Int) {
  userPoints(offset: $offset, first: $limit, orderBy: POINTS_DESC) {
    nodes {
      points
      rank
      worldRecords
      user {
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
  users(condition: {id: $id}, first: 1) {
    edges {
      node {
        userPoints {
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
  users(filter: {id: {in: $in}}) {
    nodes {
      records(
        condition: {levelId: $idLevel}
        orderBy: TIME_ASC
        first: 1
        filter: {dateUpdated: {lessThan: $lessThan}, dateCreated: {lessThan: $lessThan}}
      ) {
        edges {
          node {
            time
            user {
              steamName
            }
          }
        }
      }
    }
  }
}"""