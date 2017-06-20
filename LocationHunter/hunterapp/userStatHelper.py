def hashtagCount(hashtags):
    count_tags = {}
    for hashtag in hashtags:
        if hashtag in count_tags:
            count_tags[hashtag]+=1
        else:
            count_tags[hashtag] = 1
    count_tags = sorted(count_tags.items(),key=lambda x:-x[1])
    #print(count_tags)
    return count_tags[:5]
