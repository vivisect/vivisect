'''
The envi.qt.html module contains the HTML template and javascript
code used by the renderers (which are based on QtWebEngine)
'''

template = '''
<!DOCTYPE html>
<html id="mainhtml">
<style type="text/css">

body {
    color: #00ff00;
    background-color: #000000;
    white-space: pre;
    font: 10pt Monospace;
}

div.memcanvas {
    color: #00ff00;
    background-color: #000000;
}

div.codeblock {
    color: #00ff00;
    background-color: #000000;
    border: 2px solid #00ff00;
    display: inline-block;
}

div.codeblock:hover {
    border: 2px solid #ff0000;
}

.envi-va {
    color: #4040ff;
    background-color: #000000;
}

.envi-va-selected {
    color: #000000;
    background-color: #4040ff;
}

.envi-va:hover {
    font-weight: 900;
}

.envi-name {
    color: #00ff00;
    background-color: #000000;
}

.envi-name-selected {
    color: #000000;
    background-color: #00ff00;
}

.envi-registers {
    color: #ff0000;
    background-color: #000000;
}

.envi-registers-selected {
    color: #000000;
    background-color: #ff0000;
}

.envi-mnemonic {
    color: #ffff00;
    background-color: #000000;
}

.envi-mnemonic-selected {
    color: #000000;
    background-color: #ffff00;
}

</style>

<style type="text/css" id="cmapstyle">
</style>

<head>
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
</head>
<script language="javascript">
{{{jquery}}}

var selclass = "name";
function nameclick(elem) {
    var elem = $(elem);
    var tagval = elem.attr('envival');
    var tagname = elem.attr('envitag');
    $("."+selclass).removeClass(selclass);
    selclass = "envi-" + tagname + "-selected";
    var newclass = "envi-" + tagname + "-" + tagval;
    $("." + selclass).removeClass(selclass);
    $("." + newclass).addClass(selclass);
}

var curva = null;
var vnav = null;

document.addEventListener("DOMContentLoaded", function () {
    webc = new QWebChannel(qt.webChannelTransport, function (channel) {
        vnav = channel.objects.vnav;
    });
});

function vaclick(elem) {
    var elem = $(elem);
    var vastr = elem.attr("va");
    selectva(vastr);
}

function selectva(vastr) {
    var vaselect = ".envi-va-" + vastr;
    $(".envi-va-selected").removeClass("envi-va-selected");
    $(vaselect).addClass("envi-va-selected");
    vnav._jsSetCurVa(vastr);
}

function vagoto(elem) {
    vnav._jsGotoExpr($(elem).attr('va'))
}

function scrolltoid(name) {

    var elem = document.getElementById(name);

    if (elem != null) {
        var elemrect = elem.getBoundingClientRect();
        if ( elemrect.top < 0 ) {
            elem.scrollIntoView(true);
        }

        if ( elemrect.bottom > window.innerHeight ) {
            elem.scrollIntoView(false);
        }
    } else {
        console.log("Failed to find element");
    }
}

</script>

<body id="vbody" width="999px"><div class="memcanvas" id="memcanvas"></div></body>

</html>
'''
