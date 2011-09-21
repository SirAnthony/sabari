## -*- coding: utf-8 -*-
<html>
    <head>
        <title>Index of ${path}</title>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <link href="/styles/mainst.css" rel="stylesheet" type="text/css">
        <script type="text/javascript" src="/scripts/sabari.js"></script>
        <style>a img{border: 0px;}</style>
    </head>
    <body>
        <h1>Index of ${path}</h1>
        <hr>
        <table>
            % for row in items:
            <tr>
                % for item in row:
                % if item:
                <td valign="top" align="center">
                    <a href="${ item.get('href') }">
                        <img src="${item.get('src', '')}" ${ item.has_key('w') and 'width="%s"' % item.get('w') } alt="${item.get('alt', '')}" name="${item.get('name', '')}"><br />
                        % if item.has_key('desc'):
                        ${ item.get('desc') }
                        % endif
                    </a>
                </td>
                % endif
                % endfor
            <tr>
            % endfor
        </table>
        <hr>
        <p class="ft">
            <span style="color: red;">
                At the end of the month site will be closed presumably for 2-3 weeks <s>due to aids</s> for maintenance. <br/>
                Access to video files permanently closed.
            </span><br />
            Sabari v ${version}<br />
            Time: <span name="time">${time}</span> s.<br />
            Original <a href="https://github.com/SirAnthony/sabari">script</a> by
            <a href="mailto:anthony[at]adsorbtion.org">Sir Anthony</a>
        </p>
    </body>
</html>
