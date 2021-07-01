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

svgns = "http://www.w3.org/2000/svg";

function createSvgElement(ename, attrs) {
    var elem = document.createElementNS(svgns, ename);
    for (var aname in attrs) {
        elem.setAttribute(aname, attrs[aname]);
    }
    return elem
}

function svgwoot(parentid, svgid, width, height) {

    var elem = document.getElementById(parentid);

    var svgelem = createSvgElement("svg", { "height":height.toString(), "width":width.toString() })
    svgelem.setAttribute("id", svgid);

    elem.appendChild(svgelem);
}

function addSvgForeignObject(svgid, foid, width, height) {
    var foattrs = {
        "class":"node",
        "id":foid,
        "width":width,
        "height":height
    };

    var foelem = createSvgElement("foreignObject", foattrs);

    var svgelem = document.getElementById(svgid);
    svgelem.appendChild(foelem);
}

function addSvgForeignHtmlElement(foid, htmlid) {

    var foelem = document.getElementById(foid);
    var htmlelem = document.getElementById(htmlid);
    htmlelem.parentNode.removeChild(htmlelem);

    //foelem.appendChild(htmlid);

    var newbody = document.createElement("body");
    newbody.setAttribute("xmlns", "http://www.w3.org/1999/xhtml");
    newbody.appendChild( htmlelem );

    foelem.appendChild(newbody);
}

function moveSvgElement(elemid, xpos, ypos) {
    var elem = document.getElementById(elemid);
    elem.setAttribute("x", xpos);
    elem.setAttribute("y", ypos);
}

function plineover(pline) {
    pline.setAttribute("style", "fill:none;stroke:yellow;stroke-width:2")
}

function plineout(pline) {
    pline.setAttribute("style", "fill:none;stroke:green;stroke-width:2")
}

function drawSvgLine(svgid, lineid, points) {
    var plineattrs = {
        "id":lineid,
        "points":points,
        "style":"fill:none;stroke:green;stroke-width:2",
        "onmouseover":"plineover(this)",
        "onmouseout":"plineout(this)",
    };

    var lelem = createSvgElement("polyline", plineattrs);
    var svgelem = document.getElementById(svgid);

    //var rule = "polyline." + lineclass + ":hover { stroke: red; }";
    //document.styleSheets[0].insertRule(rule, 0);

    svgelem.appendChild(lelem);
}

</script>

<body id="vbody" width="999px"><div class="memcanvas" id="memcanvas"></div></body>

</html>
'''
