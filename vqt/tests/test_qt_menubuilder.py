'''
Tests for vqt.menubuilder — VQMenuBar, VQMenu, ActionCall, FieldAdder.
'''
import unittest

from vqt.menubuilder import VQMenuBar, VQMenu, ActionCall
from vqt.tests.qt_testbase import VQtTestCase


class TestActionCall(VQtTestCase):

    def test_success(self):
        ac = ActionCall(lambda x, y: x + y, 3, 7)
        self.assertEqual(ac(), 10)

    def test_with_kwargs(self):
        ac = ActionCall(lambda name, prefix='Hello': f'{prefix} {name}',
                        'World', prefix='Hi')
        self.assertEqual(ac(), 'Hi World')

    def test_exception_handled(self):
        '''ActionCall should not propagate exceptions.'''
        ac = ActionCall(lambda: 1 / 0)
        result = ac()
        self.assertIsNone(result)


class TestVQMenu(VQtTestCase):

    def test_create(self):
        menu = VQMenu('TestMenu')
        self.assertEqual(menu.title(), 'TestMenu')

    def test_add_field(self):
        menu = VQMenu('root')
        menu.addField('item1', callback=lambda: None)
        actions = menu.actions()
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].text(), 'item1')

    def test_nested_fields(self):
        menu = VQMenu('root')
        menu.addField('sub.item1', callback=lambda: None)
        menu.addField('sub.item2', callback=lambda: None)
        self.assertIn('sub', menu.kids)
        submenu = menu.kids['sub']
        self.assertEqual(len(submenu.actions()), 2)


class TestVQMenuBar(VQtTestCase):

    def test_create(self):
        mbar = VQMenuBar()
        self.assertIsNotNone(mbar)

    def test_add_field_with_path(self):
        mbar = VQMenuBar()
        mbar.addField('File.Save', callback=lambda: None)
        self.assertIn('File', mbar.kids)

    def test_add_multiple_fields(self):
        mbar = VQMenuBar()
        mbar.addField('File.New', callback=lambda: None)
        mbar.addField('File.Open', callback=lambda: None)
        mbar.addField('Edit.Copy', callback=lambda: None)
        self.assertIn('File', mbar.kids)
        self.assertIn('Edit', mbar.kids)
        file_menu = mbar.kids['File']
        self.assertEqual(len(file_menu.actions()), 2)

    def test_add_dyn_menu(self):
        mbar = VQMenuBar()
        def dyncb(name=None):
            if name is None:
                return ('opt1', 'opt2')
            return name
        mbar.addDynMenu('Tools.Dynamic', dyncb)
        self.assertIn('Tools', mbar.kids)

    def test_custom_splitchar(self):
        mbar = VQMenuBar(splitchar='/')
        mbar.addField('File/Save', callback=lambda: None)
        self.assertIn('File', mbar.kids)

    def test_action_trigger(self):
        '''Triggering an action should invoke the callback.'''
        mbar = VQMenuBar()
        results = []
        mbar.addField('File.Save', callback=lambda: results.append('saved'))
        file_menu = mbar.kids['File']
        file_menu.actions()[0].trigger()
        self.assertEqual(results, ['saved'])


if __name__ == '__main__':
    unittest.main()
