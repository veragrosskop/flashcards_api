from apps.cards.models import HierarchyItem


def create_hierarchy_item(*, owner, name, type, parent=None):
    return HierarchyItem.objects.create(owner=owner, name=name, type=type, parent=parent)


def update_hierarchy_item(item: HierarchyItem, **fields):
    for attr, value in fields.items():
        setattr(item, attr, value)
    item.save()
    return item
