#!/usr/bin/env python

import client
import gtk
import threading
import gobject

class Window:
    class Swarm(threading.Thread):
        def __init__(self,options,status,model):
            threading.Thread.__init__(self)
            self.options = options
            self.quit = False
            self.tracker_client = client.Client(options)
            self.dataping = client.DataPing(options)
            self.status = status
            self.model = model

        def set_status(self,message):
            gobject.idle_add(lambda mess: self.status.set_label(mess),message)

        def update_model(self):
            def aa(peers):
                self.model.clear()
                for id,data in peers.items():
                    self.model.append((id,data[0],data[1]))

            gobject.idle_add(aa,self.tracker_client.peers)

        def run(self):
            while not self.quit:
                if not self.tracker_client.connected:
                    self.set_status("Connecting to tracker")
                    self.tracker_client.say_hi()
                    self.set_status("Connected to tracker")

                if self.tracker_client.chocke_tracker(self.dataping.links):
                    self.dataping.update(self.tracker_client.peers)
                    self.set_status("Updated peers (%d peers)" % len(self.tracker_client.peers))
                    self.update_model()

                updated_link = self.dataping.manage_pinger()
                if updated_link:
                    self.set_status("Pinger from %s" % updated_link.name)

                if self.quit: break
                client.time.sleep(self.options.chocke_time)

            self.tracker_client.say_bye()

    def __init__(self):
        self.options = client.parse_options()

        self.window = gtk.Window()
        self.window.connect("destroy",self.destroy)
        layout = gtk.Table(2,2)
        self.window.add(layout)

        self.status = gtk.Label("prout")
        self.status.set_size_request(200,-1)
        layout.attach(self.status,0,1,0,1)

        self.model = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING)
        self.view = gtk.TreeView(self.model)
        id_col = gtk.TreeViewColumn('id')
        id_col.set_sort_column_id(0)
        id_cell = gtk.CellRendererText()
        id_col.pack_start(id_cell,True)
        id_col.set_attributes(id_cell,text=0)
        self.view.append_column(id_col)
        ip_col = gtk.TreeViewColumn('ip')
        ip_col.set_sort_column_id(1)
        ip_cell = gtk.CellRendererText()
        ip_col.pack_start(ip_cell,True)
        ip_col.set_attributes(ip_cell,text=1)
        self.view.append_column(ip_col)
        name_col = gtk.TreeViewColumn('name')
        name_col.set_sort_column_id(2)
        name_cell = gtk.CellRendererText()
        name_col.pack_start(name_cell,True)
        name_col.set_attributes(name_cell,text=2)
        self.view.append_column(name_col)
        self.view.set_size_request(-1,300)
        self.view.set_search_column(0)
        self.view.set_reorderable(True)
        layout.attach(self.view,0,1,1,2)

        # Allow sorting on the column
        #self.tvcolumn.set_sort_column_id(0)

        self.window.show_all()

        self.swarm = Window.Swarm(self.options,self.status,self.model)
        self.swarm.start()

    def destroy(self,widget,data=None):
        self.swarm.quit = True
        self.swarm.join()
        gtk.main_quit()

if __name__=="__main__":
    gobject.threads_init()
    window = Window()
    gtk.main()

