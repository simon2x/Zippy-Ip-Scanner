from PyQt5.QtCore import QSortFilterProxyModel


class FilteredModel(QSortFilterProxyModel):

    def __init__(self, parent):
        super(FilteredModel, self).__init__(parent)

    def filterAcceptsRow(self, sourceRow, sourceParent):
        '''This contains our new item acceptance condition

        :returns: bool
        '''
        # return True
        sourceModel = self.sourceModel()
        index2 = sourceModel.index(sourceRow, 2, sourceParent)

        data2 = sourceModel.data(index2)
        if not data2:
            return False
        return True
