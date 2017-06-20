from hunterapp.models import *
import time
import random
import numpy as np
import pickle
from gensim.models import doc2vec
from gensim.models.keyedvectors import KeyedVectors
connect('locationhunter')
with open('hashtagvecs.pkl', 'rb') as f:
    hashtag2vec = pickle.load(f)
def hasPassword(user_id):
    result = User.objects(user_id=user_id)
    if len(result) == 0:
       return False
    current_user = result[0]
    return not (current_user.password is None or current_user.password =='')

def updatePassword(user_id,password):
    logged_user = User.objects(user_id=user_id)[0]
    logged_user.password = password
    logged_user.save()

def updatePhoneNumber(user_id,phone_number):
    logged_user = User.objects(user_id=user_id)[0]
    logged_user.phone_number = phone_number
    logged_user.save()

def getPassword(user_id):
    logged_user = User.objects(user_id=user_id)[0]
    return logged_user.password

def getPhoneNumber(user_id):
    logged_user = User.objects(user_id=user_id)[0]
    return logged_user.phone_number

def recordDecline(user_id,declined_id):

    current_user = User.objects(user_id=user_id)[0]
    user_rec = UserRecomended()
    user_rec.user_id = str(declined_id)
    user_rec.date = int(time.time())
    current_user.declined_rec_users.append(user_rec)
    current_user.save()

def invalidateRecFriend(user_id,invalid_id):
    logged_user = User.objects(user_id=user_id)[0]
    new_fof = []
    for data_x in logged_user.fof:
        new_val = data_x.to_mongo()
        if data_x['user_id'] == invalid_id:
            new_val['is_valid'] = 0
        new_fof.append(new_val)
    logged_user.update(fof=new_fof)


def randomPickFollowingPeople(user_id):
    current_user = User.objects(user_id=user_id)[0]
    if len(current_user['followed_people_list']) == 0:
        return ""
    pos = random.randint(0, len(current_user['followed_people_list'])-1)
    return current_user['followed_people_list'][pos]['id']

def fliterDeclinedUser(user_id,rec_list):
    new_list = []
    current_user = User.objects(user_id=user_id)[0]
    for rec in rec_list:
        declined = False
        for dec in current_user.declined_rec_users:
            if(dec['user_id']==rec['user_id']):
                declined = True
        if(not declined):
            new_list.append(rec)
    return new_list

def alreadyFollowing(user_id,target_id):
    current_user = User.objects(user_id=user_id)[0]
    for following in current_user.followed_people_list:
        if following['id'] == target_id:
            return  True
    return False

def updateUserVector(user_id,hashtags):
    user_vector = [0]*50
    count = 0
    for hashtag in hashtags:
        vec = None
        if hashtag in hashtag2vec:
            vec = hashtag2vec[hashtag]
        if vec is not None:
            user_vector += vec
            count+=1
    if count == 0:
        user_vector = np.random.rand(50)
    else:
        user_vector = user_vector/count
    # Update the user vector
    with open('./hunterapp/users/'+user_id+'_z.pkl', 'wb') as f:
        pickle.dump(user_vector, f, pickle.HIGHEST_PROTOCOL)


