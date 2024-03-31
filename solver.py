# Copyright (C) 2024 Warren Usui, MIT License
"""
Create future bracket lists that contain all possible outcomes.
Run each individual against all possible brackets.
Find winning conditions for each individual and produce a sourted list
of possible winners and outcomes needed.
"""
from itertools import chain

def gen_future(reality):
    """
    Wrapper needed to pass already known data to xgen_future and make
    sure that results returned contain all of the past history plus
    future predictions.
    """
    def gf_wgc(nfutgames):
        return list(map(lambda a: reality + a,
                        xgen_future(reality[:][-nfutgames:])))
    return gf_wgc(64 - len(reality))

def xgen_future(reality):
    """
    Produce all possible future outcomes given a list of teams remaining
    sorted in bracket order.
    """
    def gen_bit_pattern(binfo):
        def get_bit_pattern(numb):
            if numb == 0:
                return []
            return get_bit_pattern(numb // 2) + [numb % 2]
        def gsize(vnumb):
            return [0] * (binfo[0] - len(vnumb)) + vnumb
        return gsize(get_bit_pattern(binfo[1]))
    def get_pairings(pring, numb):
        return list(zip(pring[::2], pring[1::2],
                        gen_bit_pattern([len(pring) // 2, numb])))
    def get_nre(pround, indx):
        return list(map(lambda a: a[a[2]], get_pairings(pround, indx)))
    def get_rnd(round2):
        def get_rnd_inn(count):
            return get_nre(round2, count)
        return get_rnd_inn
    def get_round(arnd):
        return list(map(get_rnd(arnd[0]),
                        list(range(2 ** (len(arnd[0]) // 2)))))
    def recur(xround):
        def rec_inner(rinfo):
            if len(rinfo[0]) == 1:
                return rinfo
            return list(map(recur, list(map(lambda a: [a, xround], rinfo[0]))))
        return rec_inner([get_round(xround), xround])
    def get_cparms(numb):
        if numb == 0:
            return []
        return [numb] + get_cparms(numb // 2)
    def xtract(drecs):
        def xtract_inner(cval):
            def irec(dval):
                if len(dval[1]) == 0:
                    return dval[0][1]
                return irec([dval[0][(cval >> (dval[1][0] - 1)) %
                                 2 ** dval[1][0]], dval[1][1:]])
            def rfmt(ival):
                if len(ival[0]) > sum(drecs[1]):
                    return []
                return rfmt(ival[1]) + ival[0]
            return rfmt(irec(drecs))
        return xtract_inner
    return list(map(xtract([recur([reality]), get_cparms(len(reality) // 2)]),
                     range(2 ** (len(reality) - 1))))

def gen_ratings(futures, picks):
    """
    Find scores for all picks and compare against all possible future
    outcomes.  Generates a dict indexed by bracket name containing a list
    of entries consisting of future outcomes that this bracket will win if
    they occur, and a count of how many brackets made this pick.
    """
    def scrtab(gm1):
        if gm1 < 0:
            return[]
        return 2 ** gm1 * [5 * 2 ** (6 - gm1)] + scrtab(gm1 - 1)
    def score(tfinfo):
        return sum(list(map(lambda a: a[1],
                list(filter(lambda a: tfinfo[a[0]], enumerate(scrtab(5)))))))
    def get_scrs(apick):
        def andwith(afuture):
            return score(list(map(lambda a: picks[apick][a] == afuture[a],
                               range(63))))
        return list(map(andwith, futures))
    def score_list():
        return list(map(get_scrs, picks))
    def get_columns(columns):
        def get_maxc(maxc):
            def find_winrs(column):
                return list(filter(lambda a: a[1] == maxc[column[0]],
                                 enumerate(column[1])))
            def xtract(indata):
                return list(map(lambda a: a[0], indata[1]))
            def fmt_data(retv):
                def fmt_wnames(nkeys):
                    def fmt_brack(pnumb):
                        def chk_it(f_ind):
                            return pnumb in f_ind[1]
                        return list(filter(chk_it, enumerate(retv)))
                    def ffmt(info):
                        def xlate(sfound):
                            return [len(sfound[1]), futures[sfound[0]]]
                        return [nkeys[info[0]], list(map(xlate, info[1]))]
                    def fmt_setup():
                        return list(map(fmt_brack, range(len(picks))))
                    def fmt_zfin():
                        return list(map(ffmt, enumerate(fmt_setup())))
                    return list(filter(lambda a: a[1], fmt_zfin()))
                return fmt_wnames(list(picks.keys()))
            return fmt_data(list(map(xtract, enumerate(
                        list(map(find_winrs, enumerate(columns)))))))
        return get_maxc(list(map(max, columns)))
    return dict(get_columns(list(map(list, zip(*score_list())))))

def eval_plyr(presults, choices):
    """
    Generate the lines to be displayed for each bracket
    """
    def evp_chc(teams):
        def evp_shrt(slist):
            def evalt(tname):
                def ev_sc(tinfo):
                    if tname in tinfo[1]:
                        return tinfo[0]
                    return 0
                return [tname, sum(list(map(ev_sc, slist)))]
            def ev_tpts(xteams):
                def ev_tpts2(xteams):
                    return list(zip(xteams[::2], xteams[1::2]))
                def ev_rdata(xpair):
                    return list(map(dict, xpair))
                return ev_rdata(ev_tpts2(xteams))
            def mk_dict(ret_data):
                return {'w_outcomes': len(presults),
                        'pct_pt': (ret_data[0][teams[0]] +
                                   ret_data[0][teams[1]]) / \
                                   2 ** (len(choices) * 2 - 1),
                        'games': ret_data}
            return mk_dict(ev_tpts(list(map(evalt, teams))))
        return evp_shrt(list(map(lambda a: [1 / a[0], a[1][0:len(choices)]],
                                 presults)))
    return evp_chc(list(chain.from_iterable(choices)))

def rank_picks(hdata):
    """
    Produce rows of bracket stats and pick outcome pairs.
    """
    def gp_max(orig):
        return ((64 - orig) // 2) + orig
    def mk_eval_data(gdata):
        return list(map(lambda a: [a[0], a[1][len(hdata[0]):]], gdata))
    def rank_res(results):
        def rankw(winners):
            def candp1(delta):
                def candp2(offset):
                    return [hdata[0][offset], hdata[0][offset + 1]]
                return candp2(2 * (len(hdata[0]) - 32 + delta))
            def candp():
                return list(map(candp1, range(0,
                                gp_max(len(hdata[0])) - len(hdata[0]))))
            def wrap_eval_plyr(entry):
                return [entry, eval_plyr(mk_eval_data(results[entry]),
                                         candp())]
            def hline_data(line_data):
                def recs_data(recs):
                    return sorted(recs, key=lambda x: x['pct_pt'],
                                  reverse=True)
                return recs_data(list(map(lambda a: {'name': a} |
                            line_data[a], line_data.keys())))
            return hline_data(dict(list(map(wrap_eval_plyr, winners))))
        return rankw(list(filter(lambda a: results[a], results.keys())))
    return rank_res(gen_ratings(gen_future(hdata[0]), hdata[1]))
