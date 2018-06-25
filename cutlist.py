import copy


class Needs():
    def __init__(self, needs):
        self.needs = needs
        self.cuts = []
        self._cost = 0.0

    def add_cuts(self, board):
        self.cuts.append(board)
        for c in board.cuts:
            for i in range(len(self.needs)):
                n = self.needs[i]
                if c == n[0]:
                    self.needs[i] = (n[0], n[1] - 1)
        self._cost = sum(map(lambda x: x.cost, self.cuts))

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
        return self._cost

    def __str__(self):
        return "cost: (%i) $%.2f [%s]" % (len(self.cuts), self.cost(), ", ".join(map(lambda x: str(x), self.cuts)))


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


class Optimizer():
    def __init__(self, boards, needs):
        self.boards = boards
        self.needs = Needs(needs)
        self.needed_lengths = list(map(lambda x: x[0], needs))
        self.min_needs = None

    def optimize(self):
        cuts_available = []
        for b in self.boards:
            cuts_available += Board.get_permutations(b, self.needed_lengths)

        cuts_available = Board.prune_permutations(cuts_available)
        cuts_available = sorted(cuts_available, key=lambda x: x.remaining())

        print("Possible cuts:")
        for c in cuts_available:
            print(c)

        self.calculate_cutlist(cuts_available, self.needs)

    def _solution_found(self, needs):
        updated = False
        if self.min_needs == None:
            self.min_needs = needs
            updated = True
        elif needs.cost() < self.min_needs.cost():
            self.min_needs = needs
            updated = True

        if updated:
            print("Current best: %s" % str(self.min_needs))

    def calculate_cutlist(self, cuts_available, needs):
        if needs.satisfied():
            self._solution_found(needs)
            return

        if self.min_needs is not None and needs.cost() >= self.min_needs.cost():
            return

        useful_boards = filter(lambda x: needs.is_useful(x), cuts_available)

        for ub in useful_boards:
            n = copy.deepcopy(needs)
            n.add_cuts(ub)
            self.calculate_cutlist(cuts_available, n)


needs = [(43, 2), (67, 8), (79, 2)]
# supply = [Board(144, 12.00), Board(192, 16.00), Board(96, 8.00)]
# supply = [Board(144, 12.00), Board(192, 16.00)]
supply = [Board(144, 12.00)]


o = Optimizer(supply, needs)
o.optimize()


print("========= SUMMARY =========")
print("Needed Cuts:")
for x in needs:
    print(f'\t{x[1]} x {x[0]}"')
print("From availabe sizes:")
for x in supply:
    print(f'\t{x.len}" @ ${x.cost:.2f}')
print(f"Can be achieved for ${o.min_needs.cost():.2f} by making the following cuts:")
for x in o.min_needs.cuts:
    print(f'from {x.len}" make cuts: {x.cuts} yields waste of {x.remaining()}"')