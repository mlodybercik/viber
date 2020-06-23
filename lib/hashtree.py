def generate_tree(mesh):
    # freq1, freq2, delta_time
    # hash_tree[freq1][freq2] = {1,3,4,54}
    hash_tree = {}
    for i in mesh:
        # if freq1 in hashtree
        if i[0] in hash_tree:
            # if freq2 inside the dict in hashtree
            if i[1] in hash_tree[i[0]]:
                hash_tree[i[0]][i[1]].add(i[2])
            # if not create corresponding entry
            else:
                hash_tree[i[0]][i[1]] = {i[2]}
        # if first check fails, there is no need to check for the second check so,
        # we create dict with set inside with corresponding values
        else:
            hash_tree[i[0]] = {i[1]:{i[2]}}
    return hash_tree

def merge_trees(tree1, tree2):
    # merges tree2 -> tree1
    for freq1, branch in tree2.items():
        for freq2, times, in branch.items():
            if freq1 in tree1:
                if freq2 in tree1[freq1]:
                    tree1[freq1][freq2].update(times)
                else:
                    tree1[freq1][freq2] = times
            else:
                tree1[freq1] = branch
    
def extract_values_from_tree(tree):
    for freq1, branch in tree.items():
        for freq2, times in branch.items():
            for time in times:
                yield (freq1, freq2, time)