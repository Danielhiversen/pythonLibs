# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 16:11:28 2015

@author: dahoiv

For calulating Hausdorf distance and modified Hausdorf distance with multy threads

"""

# Time-stamp: <Last changed 03-06-2013 11:17:35 by Daniel Hoyer Iversen, dahoiv>
import numpy as np
import scipy.spatial.distance

import time
import multiprocessing


def Hausdorff_distance(curve1,curve2,metric='euclidean'):

    def _helpHausdorff_distance(curve1,curve2):

        D=0
        D_mod=0
        processes = multiprocessing.cpu_count()
        print 'processes', processes



        def _helpHausdorff_distance2(c1,q):
                d=np.Inf
                for c2 in range(0,len(curve2)):
                    d=np.min([d,scipy.spatial.distance.euclidean(curve1[c1], curve2[c2])])
                q.put((c1-0,d))

        q = multiprocessing.Queue()
        jobs = []
        nrJobs=0
        c1=0
        k=0
        while c1 < len(curve1)-0:
            if nrJobs<processes:
                nrJobs=nrJobs+1
                print c1 /float( len(curve1))
                p = multiprocessing.Process(target=_helpHausdorff_distance2, args=(c1,q))
                p.start()
                jobs.append(p)
                c1=c1+1
            if not q.empty():
                nrJobs=nrJobs-1
                (c1_,d)=q.get()
                jobs[c1_].join()
                D=max(D,d)
                D_mod=D_mod+d
                k=k+1
        if not nrJobs<processes and q.empty():
            time.sleep(1)



        while k < 15: #len(curve1)-0:
            if not q.empty():
                (c1_,d)=q.get()
                D=max(D,d)
                jobs[c1_].join()
                D_mod=D_mod+d
                k=k+1
        else:
            time.sleep(0.5)


        D_mod=D_mod/float(k)

        print "res",D,D_mod
        return D,D_mod

    if metric=='euclidean' and len(curve1)*len(curve2)>1e5:
        print len(curve1)*len(curve2)
        H1=_helpHausdorff_distance(curve1,curve2)
        print "50%"
        H2=_helpHausdorff_distance(curve2,curve1)
        return max(H1,H2)

    # http://stackoverflow.com/questions/13692801/distance-matrix-of-curves-in-python
    D = scipy.spatial.distance.cdist(curve1, curve2, metric)
    H1 = np.max(np.min(D, axis=1))
    H2 = np.max(np.min(D, axis=0))

    H1_mod = np.mean(np.min(D, axis=1))
    H2_mod = np.mean(np.min(D, axis=0))
    return [max(H1,H2),max(H1_mod,H2_mod)]




if __name__ == '__main__':
    result=True

    C1= np.random.rand(100,3)
    assert Hausdorff_distance(C1,C1)[0] < 10**-13

    C1= np.array([1,2,3, 1,2,3]).reshape((2,3)).transpose()
    C2 = np.array([1,2,1,2]).reshape((2,2)).transpose()
    C3= np.array([1,2,3, 1,2,4]).reshape((2,3)).transpose()
    C4=np.array([1,3,6,7]).reshape(1,4).transpose()
    C5=np.array([3,6]).reshape(1,2).transpose()

    C6=np.array([1,2,3, 1,2,3, 1,2,3]).reshape((3,3)).transpose()



    assert Hausdorff_distance(C1,C1)[0] < 10**-13
    Hausdorff_distance(C1,C2)
    assert Hausdorff_distance(C1,C3)[0] == 1.0
    assert Hausdorff_distance(C4,C5)[0] == 2.0 # from http://en.wikipedia.org/wiki/Hausdorff_distance


    assert Hausdorff_distance(C6,C6)[0] < 10**-13

    if result:
        print('Passed all tests')
