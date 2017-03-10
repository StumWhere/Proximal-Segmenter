# -*- coding: utf-8 -*-
"""
Author: Alex Stum
Created for EarthLab
Created on Fri Feb 17 12:47:19 2017
This code was produced for the intent of identifying fire complexes as it
progresses day to day. The dataset has the day of year (doy) a pixel burned.
This code initially finds the first occurence of fire and groups (creates a
labled region) of all pixels which are within a specified rectangular window. 
It then moves through each day a new pixel burns and determins whether it is 
near (if there is 'hot spot' within its rectangular extent) a recently burned 
pixel. This code can be easily adapted for other segementation exercises where
proximity beyond 8 nearest neighbors is desired for segmentation.

***NOTE*** that if unburned pixels are distinguished by NaN, they need to be 
converted to -1, enable to encode connectivity across unburned pixels)

"""
import numpy as np
from scipy import ndimage as nd
from skimage import measure

howRec = 3 #absolute measure of similarity (e.g. how many days ago)
howClose = (5,5)  #window size
s3x3 = nd.generate_binary_structure(2,2)

rIN = open(r"C:\stuff\days4.txt",'r')
dayText = rIN.readlines()
rIN.close()
dayList = [l.split('\t') for l in dayText]
days = np.array(dayList,dtype=int)

daySet = np.unique(days) #unique returns an ordered set

dayOne = days==daySet[1]  #find first burn
#define initial fire complex. The maximum filter works by taking advantage of
#fact that unburned pixels have a negative value 
neigh = nd.maximum_filter(dayOne,howClose)
#Establish fire regions
Fire = measure.label(neigh*dayOne,background=False)  #multiplying masks out unburned pixels
Fire[Fire!=0] = Fire[Fire!=0]+1 #Add one to all Fired pixels, ignoring background
prevDay = daySet[1]

for day in daySet[2:]:   #Move through each day with burned pixel
    #Just burned that day
    active = days == day
    actNeigh = nd.maximum_filter(active, howClose) #active fire complexes
    newFire,nNF = nd.label(actNeigh,structure=s3x3)
    #List of newFire IDs
    nID = np.arange(1,nNF+1)
    #if the span between previous day with fire is > than horRec, there will be 
    #no hotSpot pixels:
    if (day-prevDay)<=howRec:
        #lag is hot spots so as not to look for negative days
        if day<=howRec: lag = 1
        else: lag = day-howRec
        #Find hot spots in previously id'd fires, which have burned in the past 'howRec' days
        hotSpots = np.zeros_like(Fire)
        hotSpots[(days>= lag) & (days<day)] = Fire[(days>= lag) & (days<day)]

        #find new fires that overlap (within howClose) with hot spots
        fireAssign = nd.maximum(hotSpots,newFire,index=nID)
        #if fire ID is 0 then it is a new fire, create new ID
        fireAssign[fireAssign==0] = nID[fireAssign==0]+Fire.max()
    else: #no hot spots, all newFire complexes retain their new
        fireAssign = nID+Fire.max()
    #mask out unburned pixels
    newFire[~active]=0
    #relabel newFires  have adjacent existing Fire
    for i,c in enumerate(fireAssign):
        Fire[newFire==nID[i]]=c
    prevDay = day
#References:
    #http://scikit-image.org/docs/dev/api/skimage.measure.html#skimage.measure.label
    #https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.ndimage.measurements.label.html#scipy.ndimage.measurements.label
    #https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.ndimage.measurements.maximum.html
    #https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.ndimage.maximum_filter.html#scipy.ndimage.maximum_filter