# Copyright (C) 2023 Warren Usui, MIT License
def gen_future(reality):
    def gf_wgc(nfutgames):
        def get_answer(sample):
            tpat = reality[:]
            fpatp = tpat[-nfutgames:]
            tsamp = sample
            cntr = nfutgames
            while len(tpat) < 63:
                fpindx = 0
                cntr //= 2
                for _ in range(cntr):
                    if tsamp % 2 == 0:
                        tpat.append(fpatp[fpindx])
                    else:
                        tpat.append(fpatp[fpindx + 1])
                    fpindx += 2
                    tsamp = tsamp // 2
                fpatp = tpat[-(64 - len(tpat)):]
            return tpat
        return list(map(get_answer, list(range(2 ** (nfutgames - 1)))))
    return gf_wgc(64 - len(reality))

def scrtab(gm1):
    if gm1 < 0:
        return[]
    return 2 ** gm1 * [5 * 2 ** (6 - gm1)] + scrtab(gm1 - 1)

def gen_ratings(futures, picks):
    def score(tfinfo):
        a1 = list(filter(lambda a: tfinfo[a[0]], enumerate(scrtab(5))))
        return sum(list(map(lambda a: a[1], a1)))
    pdata = {}
    for entry in picks.keys():
        pdata[entry] = list()
    for afut in futures:
        rpdata = []
        for brkt in picks:
            z = list(map(lambda a: afut[a] == picks[brkt][a], range(len(afut))))
            rpdata += [[brkt, score(z)]]
        best = max(list(map(lambda a: a[1], rpdata)))
        winners = list(filter(lambda a: a[1] == best, rpdata))
        for entry in winners:
            pdata[entry[0]] += [[len(winners), afut]]
    return pdata

def eval_plyr(presults, startp, choices):
    ret_data = list(map(lambda a: {a[0]: 0, a[1]: 0}, choices))
    for plyr in presults:
        value = 1 / plyr[0]
        for gindx in range(len(choices)):
            ret_data[gindx][plyr[1][gindx + startp]] += value
    key_info = list(ret_data[0].keys())
    return {'w_outcomes': len(presults),
            'pct_pt': (ret_data[0][key_info[0]] +
                       ret_data[0][key_info[1]]) / 2 ** (63 - startp),
            'games': ret_data}
     
def rank_picks(hdata):
    futures = gen_future(hdata[0])
    results = gen_ratings(futures, hdata[1])
    winners = list(filter(lambda a: results[a], results.keys()))
    pollorig = len(hdata[0])
    pollmax = ((64 - pollorig) // 2) + pollorig
    if pollmax == 62:
        pollmax = 63
    head_orig = 2 * pollorig - 64
    candp = []
    for delta in range(0, pollmax - pollorig):
        offset = head_orig + 2 * delta
        candp = candp + [[hdata[0][offset], hdata[0][offset + 1]]]
    line_data = {}
    for entry in winners:
        line_data[entry] = eval_plyr(results[entry], pollorig, candp)
    recs = list(map(lambda a: {'name': a} | line_data[a], line_data.keys()))
    return sorted(recs, key=lambda x: x['pct_pt'], reverse=True)
