# import needed libraires
import json
from csv import writer
from googleapiclient.discovery import build
import pandas as pd
import urllib.request
import urllib

# read youtube data api key from apikey.json
# use either videoID or channelID (you can't put both params in a request at once)
videoId = "a2y4_eOOn_Y"  # video of interest: sleeping position from Bob and Brad
channelId = "UC6_hQ4uWg9amkSo-5tYfThA"  # channel of interet: Tony C

# build service to call youtube API
def build_service(filename):
    with open(filename) as f:
        key = f.readline()
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=key)


# config function parameters for required variables to pass to service
def get_comments(
    part="snippet",
    maxResults=100,
    textFormat="plainText",
    order="time",
    allThreadsRelatedToChannelId=channelId,
    #  videoId=videoId,
    csv_filename="new_comments",
):
    # create empty lists to store desired info
    (
        comments,
        commentsId,
        authorurls,
        authornames,
        repliesCount,
        likesCount,
        viewerRating,
        dates,
        vidIds,
        vidTitles,
    ) = ([], [], [], [], [], [], [], [], [], [])
    # build our service from path/to/api
    service = build_service("./apikey.json")
    # make an API call using our service
    response = (
        service.commentThreads()
        .list(
            part=part,
            maxResults=maxResults,
            textFormat="plainText",
            order=order,
            # videoId=videoId,
            allThreadsRelatedToChannelId=channelId,
        )
        .execute()
    )

    while response:  # this loop continues to run till maxing out your quota

        for item in response["items"]:
            # index item for desired data features
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comment_id = item["snippet"]["topLevelComment"]["id"]
            reply_count = item["snippet"]["totalReplyCount"]
            like_count = item["snippet"]["topLevelComment"]["snippet"]["likeCount"]
            authorurl = item["snippet"]["topLevelComment"]["snippet"][
                "authorChannelUrl"
            ]
            authorname = item["snippet"]["topLevelComment"]["snippet"][
                "authorDisplayName"
            ]
            date = item["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
            vidId = item["snippet"]["topLevelComment"]["snippet"]["videoId"]
            vidTitle = get_vid_title(vidId)

            # append to lists
            comments.append(comment)
            commentsId.append(comment_id)
            repliesCount.append(reply_count)
            likesCount.append(like_count)
            authorurls.append(authorurl)
            authornames.append(authorname)
            dates.append(date)
            vidIds.append(vidId)
            vidTitles.append(vidTitle)

        try:
            if "nextPageToken" in response:
                response = (
                    service.commentThreads()
                    .list(
                        part=part,
                        maxResults=maxResults,
                        textFormat=textFormat,
                        order=order,
                        # videoId=videoId,
                        allThreadsRelatedToChannelId=channelId,
                        pageToken=response["nextPageToken"],
                    )
                    .execute
                )
            else:
                break
        except:
            break

    # return our data of interest
    return {
        "comment": comments,
        "commet_id": commentsId,
        "author_url": authorurls,
        "author_name": authornames,
        "reply_count": repliesCount,
        "like_count": likesCount,
        "date": dates,
        "vidid": vidIds,
        "vid_title": vidTitles,
    }


def get_vid_title(vidid):
    params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % vidid}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())
        return data["title"]


if __name__ == "__main__":
    new_comments = get_comments()
    df = pd.DataFrame(new_comments)
    print(df.shape)
    # print(df.head())
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["just_date"] = df["date"].dt.date
    df.to_csv("./new_comments.csv")
