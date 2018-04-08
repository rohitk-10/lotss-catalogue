# Code to handle the per-source files generated by zoom.py (and maybe other things in the future)

class Source(object):
    def __init__(self,ctable=None):
        # ideally this rather clunky structure would be improved!
        self.cdict={} # per-source dictionary of component lists
        self.odict={} # per-source dictionary of optical IDs
        self.sdict={} # per-source dictionary of sizes
        self.mdict={} # per-source dictionary tracking how we got here
        self.idict={} # per-source dictionary tracking LGZ id number
        self.vdict={}
        # the changed_dict tracks any changes. Since initialization is
        # change, we also provide a function to reset changes
        self.changed_dict={}
        self.blends=[]
        self.ctable=ctable
        if ctable is not None:
            ctable.add_index('Source_Name')

    def iscomp(self,component):
        try:
            return (len(self.ctable.loc[component])>0)
        except KeyError:
            return False
            
    def add(self,source,component):
        if self.ctable is not None:
            # don't add artefacts
            try:
                r=self.ctable.loc[component]
                if r['Artefact_flag'] or r['Edge_flag']:
                    return
            except KeyError:
                # we are being asked to add a component that doesn't exist, e.g. by oneoff zoom
                pass
        if source in self.cdict:
            self.set_components(source,self.cdict[source]+[component])
        else:
            self.set_components(source,[component])
        

    def remove(self,source,component):
        self.changed_dict[source]=True
        self.cdict[source].remove(component)

    def set_components(self,source,clist):
        self.changed_dict[source]=True
        self.cdict[source]=clist
        for comp in clist:
            for k in self.cdict:
                if k!=source:
                    if comp in self.cdict[k]:
                        self.remove(k,comp)

    def set_lgz_number(self,source,i):
        self.idict[source]=i
                        
    def set_version(self,source,i):
        self.vdict[source]=i
                        
    def delete_source(self,source):
        self.changed_dict[source]=True
        self.cdict[source]=[]

    def get_comps(self,source):
        if source in self.cdict:
            return self.cdict[source]
        else:
            return []

    def get_ncomps(self,source):
        ncomps=[]
        for k in self.cdict:
            if k!=source:
                ncomps+=self.cdict[k]
        return ncomps

    def set_opt(self,source,ra,dec):
        self.changed_dict[source]=True
        self.odict[source]=(ra,dec)

    def set_size(self,source,size):
        self.changed_dict[source]=True
        self.sdict[source]=size

    def reset_changes(self,version=None):
        for k in self.changed_dict:
            if version is None or self.vdict[k]==version:
                self.changed_dict[k]=False
        
def parsefile(sourcename,ss,dir=''):
    lines=[l.rstrip() for l in open(dir+sourcename+'.txt').readlines()]
    lc=0
    while lc<len(lines):
        l=lines[lc]
        if l=="":
            lc+=1
            continue
        if l[0]=='#':
            bits=l.split()
            if bits[1]=="Components":
                comps=[]
                lc+=1
                while lines[lc]!="":
                    if ss.iscomp(lines[lc]):
                        comps.append(lines[lc])
                    lc+=1
                ss.set_components(sourcename,comps)
            elif bits[1]=="OptID":
                lc+=1
                l=lines[lc]
                ra,dec=[float(b) for b in l.split()]
                ss.set_opt(sourcename,ra,dec)
                lc+=1
            elif bits[1]=="Size":
                ss.set_size(sourcename,float(lines[lc+1]))
                lc+=1
            elif bits[1]=="Deleted":
                ss.delete_source(sourcename)
            elif bits[1]=="Blend":
                ss.blends.append(sourcename)
        lc+=1
    
