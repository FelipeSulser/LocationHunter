import argparse
import os
import pickle
from collections import Counter
from pymongo import MongoClient
from gensim.models import doc2vec
from gensim.models.keyedvectors import KeyedVectors

def counterDict2List(d, rep=True):
    """
    Args:
        rep: True for repeating hashtags; False otherwise
    """
    if rep:
        l = []
        for k, v in d.items():
            for _ in range(v):
                k_ = k.lower()
                l.append(k_)
        return l
    else:
        return list(d.keys())
    
class Model():
    """
    Doc2Vec model
    Example:
        # Retrieve place
        q = "widelife animal".split()
        inferred_vector = mdl.model.infer_vector(q)
        sims = mdl.model.docvecs.most_similar([inferred_vector], topn=5)
        res = {loc:locHashtag[loc] for loc, _ in sims}
    """
    def __init__(self, docs, args):
        self.args = args
        self.__word_embedding_file = os.path.join(args.save_dir, "word_embedding.doc2vec")
        self.__model_file = os.path.join(args.save_dir, "model.doc2vec")
        self.__vocab_file = os.path.join(args.save_dir, "vocab.doc2vec")
        # doc2vec model
        self.model = doc2vec.Doc2Vec(dm=1,  # distributed memory’ (PV-DM)
                        size=args.embedding_size, 
                        window=args.window_size,
                        min_count=args.min_count,
                        sample=10e5, # threshold for configuring which higher-frequency words are randomly downsampled
                        workers=args.num_threads,
                        iter=args.num_epochs,
                        negative=args.num_negative,
                        dm_mean=args.dm_mean,
                        dm_concat=args.dm_concat,
                        dbow_words=args.dbow_words)
        print("Building vocab...")
        self.model.build_vocab(docs)
        print("Training")
        self.model.train(docs, total_examples=self.model.corpus_count, epochs=self.model.iter)
        if not os.path.isdir(args.save_dir):
            os.mkdir(args.save_dir)
        self.model.wv.save_word2vec_format(self.__word_embedding_file, 
                                      fvocab=self.__vocab_file)
        self.model.save(self.__model_file)
        self.word_embedding = KeyedVectors.load_word2vec_format(self.__word_embedding_file, binary=False)
        # Save The Result
        with open(os.path.join(args.save_dir, "locvecs.pkl"), "wb") as f:
            pickle.dump(self.model.docvecs, f)
        with open(os.path.join(args.save_dir, "hashtagvecs.pkl"), "wb") as f:
            pickle.dump(self.word_embedding, f)
        
    def getDocVec(self, doc_tag):
        """
        Args:
            doc_tag: str
        Return:
            doc vector: np array [embedding_size,]
        Example:
            getDocVec("ikea")
        """
        if doc_tag in self.model.docvecs:
            return self.model.docvecs[doc_tag] # self.model.docvecs maps location id to its vector
        else:
            print("{} not found".format(doc_tag))
    
    def getWordVec(self, w):
        """
        Args:
            w: str
        Return:
            word_embedding of word w, array like [embedding_size,]
        Example:
            getWordVec("switzerland")
        """
        if w in self.word_embedding:
            return self.word_embedding[w]
        else:
            print("{} not found".format(w))

    def dumpAllHashtags(self):
        client = MongoClient('localhost', 27017)
        db = client.locationhunter
        hashtag_table = db.hashtag2vec
        words = {w:self.word_embedding[w] for w in self.word_embedding.vocab.keys()}
        for word in words:
            tag = word
            vec = self.getWordVec(word)
            if tag is not None:
                with open('./hashtags/'+tag+'.pkl', 'wb') as f:
                    pickle.dump(vec, f, pickle.HIGHEST_PROTOCOL)
                    print(tag)
            
            
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recommend trip.")
    parser.add_argument("--embedding_size", type=int, default=50,
                        help="embedding word size")
    parser.add_argument("--window_size", type=int, default=5,
                        help="context window size")
    parser.add_argument("--learning_rate", type=float, default=0.005,
                        help="learning rate")
    parser.add_argument("--min_count", type=int, default=5,
                        help="ignore all words with total frequency lower than this")
    parser.add_argument("--num_threads", type=int, default=2,
                        help="number of threads")
    parser.add_argument("--num_epochs", type=int, default=50,
                        help="number of iterations over the corpus")
    parser.add_argument("--num_negative", type=int, default=0,
                        help="negative sampling will be used, the int for negative\
                        specifies how many “noise words” should be drawn (usually between 5-20)")
    parser.add_argument("--dm_mean", type=int, default=0,
                        help="if 0 (default) sum, 1 for mean; only applies in non-concatenative mode")
    parser.add_argument("--dm_concat", type=int, default=1,
                        help="if 0 non-concatenative mode; 1 (default) otherwise")
    parser.add_argument("--dbow_words", default=1,
                        help=" if set to 1 trains word-vectors (in skip-gram fashion) simultaneous with DBOW doc-vector training; \
                        0 (faster training of doc-vectors only)")
    parser.add_argument("--save_dir", type=str, default="save",
                        help="directory to save model and results")
    args = parser.parse_args()

    # Connect Mongodb
    client = MongoClient("localhost", 27017)
    db = client["locationhunter"]
    collection = db["location_hashtags"]
    query = collection.find({}, {"_id":0, "location":1, "tag_map":1,'tag_order_list':1})
    # Construct a dict mapping a location to a list of hashtags (including duplicate)
    locHashtag = {}
    for item in query:
        loc = item["location"]
        tag_order_list = item["tag_order_list"]
        if loc and tag_order_list:
            #hashtags = counterDict2List(tag_map, rep=False)
            # flatten the list
            hashtags  = [tag for sublist in tag_order_list for tag in sublist]
            if loc not in locHashtag:
                locHashtag[loc] = hashtags
            else:
                locHashtag[loc] += hashtags

    #loc2int = {loc:i for i, loc in enumerate(locHashtag.keys())} # map a location (string) to its id
    #with open(os.path.join(args.save_dir, "loc2int.pkl"), "wb") as f:
        #pickle.dump(loc2int, f)
    # Construct documents
    docs = []
    for loc, tags in locHashtag.items():
        docs.append(doc2vec.TaggedDocument(tags, [loc]))
    
    mdl = Model(docs, args)
    #mdl.dumpAllHashtags()
    print(len(mdl.getDocVec("ikea")))
    