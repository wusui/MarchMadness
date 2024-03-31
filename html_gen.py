# Copyright (C) 2024 Warren Usui, MIT License
"""
Generate the html file used to output results.

The data input to make_html consists of records that will be formatted into
the table header and individual rows of the table, and text to be added to
the text header.
"""
import datetime

def table_header(solution):
    """
    Generate the html for the table header
    """
    def mk_games():
        def igms():
            return list(map(lambda a: list(a.keys()), solution[0]['games']))
        def set_tstr():
            return list(map(lambda a: '<th><div>' + a[0] + '</div><div>' + \
                        a[1] + '</div></th>', igms()))
        return ''.join(set_tstr())
    return '<table border="1">' + \
        '<tr><th>NAME</th><th><div>Winning</div>\n' + \
        '<div>Outcomes</div></th><th><div>Probable</div>\n' + \
        '<div>Payoff</div>\n' + mk_games() + '</th></tr>\n'

def get_ccode(fgame):
    """
    Handle the colors used by the individual cells in the table.
    """
    def gc_inner(dvals):
        def setf_dvals(cnumbs):
            def setbg_vals(icol):
                if icol < 256:
                    return f'#{icol:02x}ff00'
                return f'#ff{max(511 - icol, 0):02x}00'
            return setbg_vals(int(512 * cnumbs[0] / cnumbs[1] + .5))
        return setf_dvals([abs(dvals[0] - dvals[1]), dvals[0] + dvals[1]])
    return gc_inner(list(fgame.values()))

def table_body(solution):
    """
    Write the individual rows in the table
    """
    def strfy(nfloat):
        return f'{nfloat:.6f}'
    def const_row(row):
        def left_cols():
            return ['<td>' + row['name'] + '</td>',
                  '<td>' + str(row['w_outcomes']) + '</td>',
                  '<td>' + strfy(row['pct_pt']) + '</td>']
        def game_field(fgame):
            def gstyle(style_data):
                if style_data[0][1] == 0:
                    return '#000000;color:#ffffff'
                return get_ccode(fgame)
            def get_style(teams):
                if teams[0][1] == teams[1][1]:
                    return '<td>*</td>'
                return f'<td style=background-color:{gstyle(teams)}>' + \
                        f'{teams[1][0]}</td>'
            return get_style(sorted(list(zip(fgame.keys(), fgame.values())),
                            key=lambda a: a[1]))
        def group_cols():
            return left_cols() + list(map(game_field, row['games']))
        return '<tr>' + '\n'.join(group_cols()) + '</tr>'
    return '\n'.join(list(map(const_row, solution)))

def html_header(tourney):
    """
    Generate the html for the file header
    """
    return '<html>\n    <head>\n    <title>MAD AS A MARCH LLAMA' + \
           '    </title>\n    <link rel="icon" ' + \
           'href="../../src/main_page/basketball.png">\n' + \
           '    <style>\n        h1, tr, div, p, td {\n' + \
           '        text-align: center;\n        font-weight: bold;\n' + \
           '        font-family: Arial,sans-serif;}\n' + \
           '    table {\n        margin-left: auto;\n' + \
           '        margin-right: auto;}\n    </style>\n    </head>\n' + \
           '    <meta http-equiv="Content-Type" content="text/html; ' + \
           'charset=utf-8">\n    <body>\n    <center>\n' + \
           '<br><h1>Mad As A March Llama -- ' + \
           f"{datetime.date.today().year} {tourney} " + \
           'NCAA Tournament</h1><br><br>'

def html_trailer():
    """
    Generate the html for the file trailer
    """
    return '        </table>\n    </center>\n    </body>\n</html>'

def make_html(solution):
    """
    String together all the pieces that compose the html data returned
    as a string.
    """
    return html_header(solution[1]) + table_header(solution[0]) + \
            table_body(solution[0]) + html_trailer()
