
'''
Render a graph full of gtk widgets and draw some lines!
'''

import gtk
import gtk.gdk as gdk

import vwidget.main as vw_main

import visgraph.renderers as vg_render
import visgraph.drawing.bezier as vw_bezier
import visgraph.drawing.catmullrom as vw_catmullrom

zero_zero = (0,0)

class GtkVisGraphOverview(gtk.DrawingArea):

    def __init__(self, graph, layout, scrollwin=None, ):
        gtk.DrawingArea.__init__(self)
        self._vg_graph = graph
        self._vg_layout = layout
        self._vg_scrollwin = scrollwin

        self.connect('expose-event', self.expose_event_cb)
        self.connect('button_press_event', self.button_press_event)
        self.set_events( self.get_events() | gtk.gdk.BUTTON_PRESS_MASK)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color())
        self.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(green=65535))

        if scrollwin is not None:
            scrollwin.connect('destroy', self.scroll_destroy_cb)

    def scroll_destroy_cb(self, widget):
        self.destroy()

    def expose_event_cb(self, layout, event):

        style = self.get_style()
        gc = style.fg_gc[gtk.STATE_NORMAL]

        rect = self.get_allocation()

        owidth = rect.width
        oheight = rect.height

        lwidth, lheight = self._vg_layout.getLayoutSize()

        for nid, ninfo in self._vg_graph.getNodes():

            nwidth, nheight = ninfo.get('size', zero_zero)
            if nwidth == 0:
                continue

            xpos, ypos = ninfo.get('position', zero_zero)

            drawx = ((xpos * owidth) / lwidth)
            drawy = (ypos * oheight) / lheight

            sizex = owidth * nwidth / lwidth
            sizey = oheight * nheight / lheight

            colorstr = ninfo.get('color')
            if colorstr is None:
                colorstr = '#0f0'

            color = gtk.gdk.color_parse(colorstr)

            #self.modify_fg(gtk.STATE_NORMAL, color)
            self.window.draw_rectangle(gc, False, drawx, drawy, sizex, sizey)

            #c = self.window.cairo_create()
            #c.set_source_rgb(color.red / float(65535), color.green / float(65535), color.blue / float(65535))
            #c.rectangle(drawx, drawy, sizex, sizey)# event.area.x, event.area.y, event.area.width, event.area.height)
            #c.set_line_width(0.5)
            #c.stroke()

    def button_press_event(self, widget, event):
        if self._vg_scrollwin:
            rect = self.get_allocation()
            xper = event.x / float(rect.width)
            yper = event.y / float(rect.height)

            hadj = self._vg_scrollwin.get_hadjustment()
            vadj = self._vg_scrollwin.get_vadjustment()

            hvis = hadj.page_size
            vvis = vadj.page_size

            hadj.value = min(max((hadj.upper * xper) - (hvis / 2), 0), hadj.upper - hvis)
            vadj.value = min(max((vadj.upper * yper) - (vvis / 2), 0), vadj.upper - vvis)

            self._vg_scrollwin.set_hadjustment(hadj)
            self._vg_scrollwin.set_vadjustment(vadj)

#FIXME use cairo to draw!
class GtkVisGraphRenderer(gtk.Layout, vg_render.GraphRenderer):

    def __init__(self, graph):
        gtk.Layout.__init__(self)
        vg_render.GraphRenderer.__init__(self, graph)

        self._vg_lines = []

        self.connect('expose-event', self.expose_event_cb)
        self.connect('button_press_event', self.button_press_event)

        self.set_events( self.get_events() | gtk.gdk.BUTTON_PRESS_MASK)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color())
        self.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(green=65535))

    def beginRender(self, width, height):
        vg_render.GraphRenderer.beginRender(self, width, height)
        self._vg_lines = []
        self.set_size(width, height)

    def renderNode(self, nid, ninfo, xpos, ypos):
        widget = ninfo.get('widget')
        # FIXME honor color, etc...?
        if widget is not None:
            self.move(widget, xpos, ypos)

    def renderEdge(self, eid, einfo, points):
        # FIXME deal with colors etc...
        self._vg_lines.append(points)

    def setNodeSizes(self, graph):

        for nid, ninfo in graph.getNodes():

            # Skip "ghost" nodes...
            if ninfo.get('ghost'):
                continue

            widget = ninfo.get('widget')
            if widget is None:
                widget = gtk.Label(str(nid))
                widget.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color())
                widget.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(green=65535))
                ninfo['widget'] = widget

            # Put them all at 0,0 for now...
            self.put(widget, 0, 0)

        # Get them all to render...
        self.show_all()
        vw_main.doiterations()

        # Now that we have rendered them...
        for nid, ninfo in graph.getNodes():
            widget = ninfo.get('widget')
            if widget is None:
                continue

            size = widget.size_request()
            ninfo['size'] = size

    def button_press_event(self, widget, event):
        pass

    def expose_event_cb(self, layout, event):

        style = self.get_style()

        gc = style.fg_gc[gtk.STATE_NORMAL]

        for points in self._vg_lines:
            self.bin_window.draw_lines(gc, points)
