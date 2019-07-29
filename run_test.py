"""
Run start for FactoryGame test suite.
"""

## Whether to run GUI tests.
RUN_GUI_TESTS = 1


if __name__ != "__main__":
    exit(1)

if RUN_GUI_TESTS:
    # Create gui_test_manager object for root window.
    from test.template.template_gui import GuiTestManager
    gui_test_manager = GuiTestManager()
    
    # Add test for tkutils.
    from test.utils.tkutils_test import MotionInputTest
    gui_test_manager.add_test(MotionInputTest)

    # Add test for blueprints.
    from test.core.blueprint_test import GraphMotionTest
    gui_test_manager.add_test(GraphMotionTest)

    # Add test for engine.
    from test.core.engine_test import EngineTickTest
    gui_test_manager.add_test(EngineTickTest)

    # Start mainloop.
    gui_test_manager.mainloop()
