import copy

supply = [(144, 0, 12)]
needs = [(43, 2), (67, 8), (79, 2)]


class Needs():
    def __init__(self, needs):
        self.needs = needs
        self.cuts = []

    def add_cuts(self, board):
        self.cuts.append(board)
        for c in board.cuts:
            for i in range(len(self.needs)):
                n = self.needs[i]
                if c == n[0]:
                    self.needs[i] = (n[0], n[1] - 1)

    def satisfied(self):
        for n in self.needs:
            if n[1] > 0:
                return False

        return True

    def is_useful(self, board):
        for c in board.cuts:
            for n in filter(lambda x: x[1] > 0, self.needs):
                if c == n[0]:
                    return True
        return False

    def cost(self):
        return sum(map(lambda x: x.cost, self.cuts))

    def __str__(self):
        return "cost: (%i) %i [%s]" % (len(self.cuts), self.cost(), ", ".join(map(lambda x: str(x), self.cuts)))


class Board():
    def __init__(self, len, cost):
        self.len = len
        self.cuts = []
        self.cost = cost

    def remaining(self):
        return self.len - sum(self.cuts)

    def add_cut(self, cut):
        self.cuts.append(cut)
        self.cuts = sorted(self.cuts)

    def __str__(self):
        return "%i: %s ~ (%i)" % (self.len, ", ".join(map(lambda x: str(x), self.cuts)), self.remaining())

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def __hash__(self):
        return hash(self.__str__())

    @staticmethod
    def get_permutations(board, need_sizes):
        handleable_sizes = list(filter(lambda x: x < board.remaining(), need_sizes))

        if len(handleable_sizes) == 0:
            return [board]

        perms = []
        for hs in handleable_sizes:
            b = copy.deepcopy(board)
            b.add_cut(hs)
            perms += Board.get_permutations(b, need_sizes)

        return perms

    @staticmethod
    def prune_permutations(boards):
        return set(boards)

cuts_available = Board.get_permutations(Board(144, 12.00), list(map(lambda x: x[0], needs)))
print("Possible cuts:")
for p in Board.prune_permutations(cuts_available):
    print(p)

print("")

min_needs = None
def solution_found(needs):
    global min_needs
    updated = False
    if min_needs == None:
        min_needs = needs
        updated = True
    elif needs.cost() < min_needs.cost():
        min_needs = needs
        updated = True

    if updated:
        print(min_needs)

def calculate_cutlist(cuts_available, needs):
    global min_needs

    if needs.satisfied():
        solution_found(needs)
        return

    if min_needs is not None and needs.cost() >= min_needs.cost():
        return

    useful_boards = filter(lambda x: needs.is_useful(x), cuts_available)

    for ub in useful_boards:
        n = copy.deepcopy(needs)
        n.add_cuts(ub)
        calculate_cutlist(cuts_available, n)


calculate_cutlist(cuts_available, Needs(needs))