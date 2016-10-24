'''
The envi.qt.html module contains the HTML template and javascript
code used by the renderers (which are based on QtWebKit)
'''

template = '''
<!DOCTYPE html>
<html id="mainhtml">
<head></head>

<style type="text/css">

body {
    color: #00ff00;
    background-color: #000000;
    white-space: pre;
    font: 12pt;
    font-family: "monospace";
}

div.memcanvas {
    color: #00ff00;
    background-color: #000000;
    font: 12pt;
    font-family: "monospace";
}

div.codeblock {
    color: #00ff00;
    background-color: #000000;
    border: 2px solid #00ff00;
    display: inline-block;
    font: 12pt;
    font-family: "monospace";
}

div.codeblock:hover {
    border: 2px solid #ff0000;
    font: 12pt;
    font-family: "monospace";
}

.envi-va {
    color: #4040ff;
    background-color: #000000;
    font: 12pt;
    font-family: "monospace";
}

.envi-va-selected {
    color: #000000;
    background-color: #4040ff;
    font: 12pt;
    font-family: "monospace";
}

.envi-va:hover {
    font-weight: 900;
    font: 12pt;
    font-family: "monospace";
}

.envi-name {
    color: #00ff00;
    background-color: #000000;
    font: 12pt;
    font-family: "monospace";
}

.envi-name-selected {
    color: #000000;
    background-color: #00ff00;
    font: 12pt;
    font-family: "monospace";
}

.envi-registers {
    color: #ff0000;
    background-color: #000000;
    font: 12pt;
    font-family: "monospace";
}

.envi-registers-selected {
    color: #000000;
    background-color: #ff0000;
    font: 12pt;
    font-family: "monospace";
}

.envi-mnemonic {
    color: #ffff00;
    background-color: #000000;
    font: 12pt;
    font-family: "monospace";
}

.envi-mnemonic-selected {
    color: #000000;
    background-color: #ffff00;
    font: 12pt;
    font-family: "monospace";
}

</style>

<style type="text/css" id="cmapstyle">
</style>

<script language="javascript">
{{{jquery}}}

var selclass = "name"
function nameclick(elem) {
    var elem = $(elem)
    var tagval = elem.attr('envival')
    var tagname = elem.attr('envitag')
    $("."+selclass).removeClass(selclass)
    selclass = "envi-" + tagname + "-selected"
    var newclass = "envi-" + tagname + "-" + tagval
    $("." + selclass).removeClass(selclass)
    $("." + newclass).addClass(selclass)
}

var curva = null;
function vaclick(elem) {
    var elem = $(elem)
    var vastr = elem.attr("va")
    selectva(vastr)
}

function selectva(vastr) {
    var vaselect = ".envi-va-" + vastr
    $(".envi-va-selected").removeClass("envi-va-selected")
    $(vaselect).addClass("envi-va-selected")
    vnav._jsSetCurVa(vastr)
}

function vagoto(elem) {
    vnav._jsGotoExpr($(elem).attr('va'))
}

function scrolltoid(name) {

    var elem = document.getElementById(name);

    var elemrect = elem.getBoundingClientRect();
    if ( elemrect.top < 0 ) {
        elem.scrollIntoView(true);
    }

    if ( elemrect.bottom > window.innerHeight ) {
        elem.scrollIntoView(false);
    }
}

</script>

<body id="vbody" width="999px"><div class="memcanvas" id="memcanvas"></div></body>

</html>
'''

