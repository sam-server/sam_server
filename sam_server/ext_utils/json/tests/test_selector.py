from django.test import TestCase

from ..field_selector import FieldSelector, FieldListSelector, Selector


class SelectorTests(TestCase):
    def test_field_selector(self):
        resource = {"prop": {"subprop": 4, "subprop2": 5}, "prop2": 6}
        field_selector = FieldSelector('prop', FieldSelector('subprop'))
        selected_resource = field_selector.select(resource)
        self.assertEqual(selected_resource, {"prop": {"subprop": 4}})

        resource_list = [
            {"prop1": 1, "prop2": 2},
            {"prop1": 4, "prop2": 5}
        ]
        selector = FieldSelector("prop1")
        self.assertEqual(
            selector.select(resource_list),
            [{"prop1": 1}, {"prop1": 4}]
        )

    def test_fieldlist_selector(self):
        resource = {
            "prop1": {"subprop11": 4, "subprop12": 5},
            "prop2": {"subprop21": 6}
        }
        selector = FieldListSelector([
            FieldSelector("prop1", FieldSelector("subprop11")),
            FieldSelector("prop2")
        ])
        selected = selector.select(resource)
        self.assertEqual(
            selected,
            {
                "prop1": {"subprop11": 4},
                "prop2": {"subprop21": 6}
            })

    def test_parse_selector(self):
        fields = 'prop1.prop2, prop3(prop4, prop5.prop6)'
        s = Selector.parse(fields)
        self.assertEqual(
            s,
            FieldListSelector([
                FieldSelector('prop1', FieldSelector('prop2')),
                FieldSelector('prop3', FieldListSelector([
                    FieldSelector('prop4'),
                    FieldSelector('prop5', FieldSelector('prop6'))
                ]))
            ])
        )
