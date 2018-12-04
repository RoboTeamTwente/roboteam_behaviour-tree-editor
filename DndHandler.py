import datetime
import globals
import keyboard


class DndHandler:

    root = None
    window = None
    clicked = []

    def __init__(self, source, event):
        if event.num > 5:
            return
        root = event.widget._root()
        try:
            root.__dnd
            return # Don't start recursive dnd
        except AttributeError:
            root.__dnd = self
            self.root = root

        self.time = datetime.datetime.now()

        self.source = source
        self.target = None
        self.initial_button = button = event.num
        self.initial_widget = widget = event.widget
        self.release_pattern = "<B%d-ButtonRelease-%d>" % (button, button)
        self.save_cursor = widget['cursor'] or ""
        widget.bind(self.release_pattern, self.on_release)
        widget.bind("<Motion>", self.on_motion)
        widget['cursor'] = "hand2"

    def __del__(self):
        root = self.root
        self.root = None
        if root:
            try:
                del root.__dnd
            except AttributeError:
                pass

    def click(self):
        if keyboard.is_pressed('d'):
            if not DndHandler.clicked:
                DndHandler.clicked.append(self.source)
            elif len(DndHandler.clicked) == 1:
                DndHandler.clicked.append(self.source)
                self.source.drawLine(DndHandler.clicked[0], DndHandler.clicked[1])
                DndHandler.clicked = []

        if keyboard.is_pressed('r'):
            for line in self.source.lines.copy():
                self.source.canvas.after(10, self.source.canvas.delete, line.id)
                self.source.lines.remove(line)
                line.delete()

            for node in self.source.nodes.copy():
                for line in node.lines:
                    if line.a == self.source or line.b == self.source:
                        line.delete()

            self.initial_widget.destroy()
            self.source.delete()
            return True

        globals.main_window.spawnProperties(self.source)

        return False

    def on_motion(self, event):
        x, y = event.x_root, event.y_root
        target_widget = self.initial_widget.winfo_containing(x, y)
        source = self.source
        new_target = None
        while target_widget:
            try:
                attr = target_widget.dnd_accept
            except AttributeError:
                pass
            else:
                new_target = attr(source, event)
                if new_target:
                    break
            target_widget = target_widget.master
        old_target = self.target
        if old_target is new_target:
            if old_target:
                old_target.dnd_motion(source, event)
        else:
            if old_target:
                self.target = None
                old_target.dnd_leave(source, event)
            if new_target:
                new_target.dnd_enter(source, event)
                self.target = new_target

    def on_release(self, event):
        deleted = False
        ms = (datetime.datetime.now() - self.time).microseconds / 1000
        if ms < 150:
            deleted = self.click()

        self.finish(event, 1, deleted)

    def cancel(self, event=None):
        self.finish(event, 0)

    def finish(self, event, commit=0, deleted=False):
        target = self.target
        source = self.source
        widget = self.initial_widget
        root = self.root
        try:
            del root.__dnd
            if not deleted:
                self.initial_widget.unbind(self.release_pattern)
                self.initial_widget.unbind("<Motion>")
                widget['cursor'] = self.save_cursor
            self.target = self.source = self.initial_widget = self.root = None
            if target:
                if commit:
                    target.dnd_commit(source, event)
                else:
                    target.dnd_leave(source, event)
        finally:
            source.dnd_end(target, event)