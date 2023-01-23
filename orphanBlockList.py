class OrhpanBlockList:
    orphanBlockList = []        # list of received orphanBlocks

    def push(self, orphanBlock):
        self.orphanBlockList.append(orphanBlock)

    def exists(self, orphanBlock):
        return orphanBlock in self.orphanBlockList

    def getOrphanBlockList(self):
        return self.orphanBlockList

    def print(self):
        print("Contained orphan blocks:")
        for orphanBlock in self.orphanBlockList:
            print(orphanBlock)
