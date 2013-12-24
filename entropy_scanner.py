
import argparse
import os
import Image
from math import log
import math

class EntropyScanner():
    def __init__(self,source_path=None,threshold=10,valid_extensions=['jpg','png'],frame_distance=10):
        self.source_path=source_path
        self.threshold=threshold*10000
        self.extensions=valid_extensions
        self.frame_distance=frame_distance
        self.distances=[]
        self.valid_files=[]
        self.chunks=[]

    def scan(self,progress_call_back=None):
        filelist=os.listdir(self.source_path)
        prev_histogram=(0,0,0)
        for i in range(0,len(filelist)):
            valid=False
            for e in self.extensions:
                if filelist[i].endswith(e):
                    valid=True
            if valid:
                histogram=self.getEntropy(os.path.join(self.source_path,filelist[i]))
                diff=int(self.distance(prev_histogram,histogram))
                self.distances.append(diff)
                self.valid_files.append(filelist[i])
                prev_histogram=histogram
            if progress_call_back:
                progress_call_back(i,len(filelist),filelist[i])

    def chunk(self):
        chunks=[]
        sequence_chunk=[]
        for i in range(0,len(self.valid_files)):
            if self.distances[i] > self.threshold and len(sequence_chunk) > self.frame_distance:
                print "Scene detect:"+str(self.valid_files[i])+":"+str(self.distances[i])+":"+str(self.threshold)
                chunks.append(sequence_chunk)
                sequence_chunk=[]
            sequence_chunk.append(self.valid_files[i])
        return chunks


    def distance(self,arr1,arr2):
        sq_total=0
        for i in range(0,len(arr1)):
            a=arr1[i]-arr2[i]
            sq_total=sq_total+a*a
        return math.sqrt(sq_total)


    def entropy(self,histogram):
        total = len(histogram)
        log2 = lambda x:log(x)/log(2)
        counts = {}
        for item in histogram:
            counts.setdefault(item,0)
            counts[item]+=1
            #print "Count:"+str(counts[item])
        ent = 0
        entropy = 0
        for i in counts:
            p = float(counts[i])/total
            ent -=p*log2(p)
        if ent > 0:
            entropy= -ent*log2(1/ent)
        return entropy

    def getEntropy(self,filename):
        im = Image.open(filename)
        h = im.histogram()
        red=h[0:256]
        green=h[257:512]
        blue=h[513:768]
        return (self.entropy(red),self.entropy(green),self.entropy(blue))

    def getHistogram(self,filename):
        im = Image.open(filename)
        h = im.histogram()
        return h


def call_back(number,total,filename):
    (x,y)=divmod(number,100)
    if y==0:
        print "*"+filename


if __name__ == '__main__':
    parser= argparse.ArgumentParser(description='Scan image sequence for entropy changes (scene detection)')
    parser.add_argument('sequence_path', type=str, help="Path of image sequence to analyze")
    parser.add_argument('-d',type=str,help="Destination for split image sequences",default="./new_sequence")
    parser.add_argument('-p',type=str,help="Sequence prefix (default shot_)",default="shot_")
    parser.add_argument('-t',type=int,help="Threshold value for scene detection (default 10)",default=10)
    parser.add_argument('-n',type=int,help="Number of digit padding for sequencing (default 7)",default=7)
    parser.add_argument('-r',type=int,help="Restripe sequences to start at giving number default(1000)",default=1000)
    parser.add_argument('-f',type=int,help="Minimum frame distance(10)",default=10)
    parser.add_argument('-v',type=bool,help="Restripe sequences to start at giving number default(1000)",default=False)

    args=parser.parse_args()
    print str(args)
    es=EntropyScanner(source_path=args.sequence_path,threshold=args.t,frame_distance=args.f)
    es.scan(progress_call_back=call_back)
    print es.chunk()
