# Copyright (c) 2016-2017 Koninklijke Philips N.V. All rights reserved. A
# copyright license for redistribution and use in source and binary forms,
# with or without modification, is hereby granted for non-commercial,
# experimental and research purposes, provided that the following conditions
# are met:
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimers.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimers in the
#   documentation and/or other materials provided with the distribution. If
#   you wish to use this software commercially, kindly contact
#   info.licensing@philips.com to obtain a commercial license.
# 
# This license extends only to copyright and does not include or grant any
# patent license or other license whatsoever.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import sys

fns = dict()
eqs = dict()
blocks = dict()

def contextualize(lst):
    global context
    context = None
    def nxt(z):
        global context
        l,m,r=z.partition("/")
        if m!="":
            if context!=None and l!=context:
                print >>sys.stderr, "*** Inconsistent contexts", l, context, "in:", lst
            context=l
            return r
        return l
    ctl = map(nxt, lst)
    return context, ctl
    
print >>sys.stderr, "*** opening combined qap file", sys.argv[1]

schedf = open(sys.argv[1]+".schedule", "w")

for ln in open(sys.argv[1]):
    ln = ln.strip()
    if ln=="" or ln[0]=="#": continue
    toks = ln.strip().split(" ")
    
    if toks[0]=="[function]":
        fns[toks[2]]=toks[1]
        print >>schedf, ln
        #print "function ", toks[2], toks[1]
    elif toks[0]=="[ioblock]":
        chk,lst = contextualize(toks[3:])
        if chk!=toks[1]:
            print >>sys.stderr, "*** Inconsistent contexts ", chk, toks[1]
        if not toks[1] in blocks: blocks[toks[1]]=[]
        blocks[toks[1]].append((toks[2],lst))
        #print "block", toks[1], toks[2], lst
    elif toks[0]=="[input]" or toks[0]=="[output]" or toks[0]=="[glue]":
        print >>schedf, ln
    else:
        qap, tokn = contextualize(toks)
        if not qap in eqs: eqs[qap]=[]
        eqs[qap].append(tokn)
        #print "eq", qap, tokn
        
def getqap(nm):
    if not nm in blocks: blocks[nm]=[]
    if not nm in eqs: eqs[nm]=[]
    
    bstr = lambda x: "[ioblock] " + x[0] + " " + " ".join(x[1])
    eqstr = lambda eq: " ".join(eq)

    return sorted(map(bstr, blocks[nm])+map(eqstr, eqs[nm]))
    
hexs = dict()

print >>sys.stderr, "found qaps: "

qapl = open(sys.argv[1]+".qaplist", "w")
print >>qapl, " ".join(set(sorted([fns[x] for x in sorted(fns)])))
qapl.close()
        
for x in fns:
    q = getqap(x)
    hs = hex(abs(hash(str(q))))[2:]
    print "  ", x, fns[x], hs, len(eqs[x]),
    if fns[x] in hexs and hexs[fns[x]]!=hs:
        print "*** Inconsistent functions", fns[x]+"."+hs, fns[x]+"."+hexs[fns[x]]
    if not fns[x] in hexs:
        outf = open(sys.argv[1]+"."+fns[x], "w")
        print >>outf, "\n".join(q+[])
        outf.close()
        hexs[fns[x]]=hs
        print "*"
    else:
        print "."
