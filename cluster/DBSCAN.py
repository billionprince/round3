import numpy as np
from sklearn.cluster.dbscan_ import DBSCAN

from util import dataHandler


def DBSCAN_user(user_dict, eps=0.5):
    user_mtx = [user_dict[key] for key in user_dict]
 
    # rec = StandardScaler().fit_transform(user_mtx)

    db = DBSCAN(eps=eps).fit(user_mtx)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    dataHandler.writeFile('result/DBSCAN_user.csv', labels)
      
    # Number of clusters in labels, ignoring noise if present.
    # n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    # print n_clusters_
     
    return (labels, user_dict)