"""Template for GUI test runs."""

from tkinter import Toplevel, Tk, Listbox
from tkinter.ttk import Label, Scrollbar, Frame, Button

class GuiTest(Toplevel):
    """Template class for GUI test runs. Inherit and override `def start(self)`
    for running GUI tests."""

    ## Test name and title of toplevel window. If left None, will use class name.
    _test_name = None
    
    @classmethod
    def get_test_name(self):
        if self._test_name is None:
            # Use class name if undefined.
            try:
                # Called on the class.
                return self.__name__
            except AttributeError:
                # Called on an instance.
                return type(self).__name__
        return self._test_name        
    
    def __init__(self, master=None, **kw):   
        """Create new toplevel window and start GUI test run."""

        # Initialise the Toplevel parent.
        Toplevel.__init__(self, master=master, width=400, height=300, **kw)

        # Set window title.
        self.title(self.get_test_name())

        # Run this test's suite. Override start method for tests.
        self.start()

    def start(self):
        """Called when initialised. Override for creating test widgets."""
        pass

class GuiTestManager(Tk):
    """Manager for GUI tests. Use `add_test` method to add a test class."""
    def __init__(self):
        """Initialise manager."""
        Tk.__init__(self)
        self.title("GUI Test Manager")
        self.geometry("400x300")

        ## Dictionary of Toplevel tests who are current active.
        self.active_tests = {}

        ## List of all available test classes.
        self.all_tests = []


        # Create widgets to show list of available tests.
        Label(self, text="Available Tests",
            font=("Comic Sans MS", "24")
            ).pack(padx=3, pady=3)

        Label(self, text="Click a test to open it, and again to close it.",
            font=["Comic Sans MS"]
            ).pack()

        # Create container for listbox and scrollbar.
        list_frame = Frame(self)
        list_frame.pack(fill="both", expand=1, padx=3, pady=3)
        
        # Add scrollbar for Listbox.
        list_scrollbar = Scrollbar(list_frame, orient="vertical")
        list_scrollbar.pack(side="right", fill="y")

        # Create Listbox next to scrollbar.
        self.all_tests_list = Listbox(list_frame, selectmode="multiple",
            yscrollcommand=list_scrollbar.set, selectborderwidth=5,
            font=("Comic Sans MS", "16", "italic"), activestyle="none",
            takefocus=1, cursor="pirate")
        # Bind the event for 0ms after a click, so the listbox can process first.
        self.all_tests_list.bind("<ButtonPress-1>", lambda e:
            self.after(0, lambda e=e: self.on_test_list_pressed(e)))
        self.all_tests_list.pack(side="left", fill="both", expand=1)

        # Link scrollbar and listbox scroll commands.
        list_scrollbar.config(command=self.all_tests_list.yview)

        # Perform initial refresh.
        self.refresh_available()

    def add_test(self, test_class):
        """Add a GUI test class to the test manager."""
        # Will do nothing if already added this test.
        self.all_tests = list(set(self.all_tests + [test_class]))
        self.refresh_available()

    def refresh_available(self):
        """Refresh list of available tests."""

        # Delete old options.
        old_selection = self.all_tests_list.curselection()
        self.all_tests_list.delete(0, "end")

        # Show new options in Listbox from set.
        for test_class in self.all_tests:
            self.all_tests_list.insert("end", test_class.get_test_name())

        # Maintain previous selection.
        for i in old_selection:
            self.all_tests_list.select_set(i)

    def on_test_list_pressed(self, event):
        """Called when mouse button 1 pressed on all_tests_list"""

        # All selected indexes.
        now_selected = set(self.all_tests_list.curselection())

        # Check all options in Listbox.
        for i, test_class in enumerate(self.all_tests):

            if i in now_selected and i not in self.active_tests:                

                # Index has been newly selected. Make the widget.
                new_wgt = test_class(self)
                new_wgt.protocol("WM_DELETE_WINDOW", lambda i=i: self.on_toplevel_destroyed(i))
                self.active_tests[i] = new_wgt

            elif i not in now_selected and i in self.active_tests:

                # Index has been newly deselected. Destroy the widget.
                self.active_tests.pop(i).destroy()

    def on_toplevel_destroyed(self, index):
        """Called when initialised test window is manually destroyed."""
        self.active_tests.pop(index).destroy()
        self.all_tests_list.select_clear(index)
