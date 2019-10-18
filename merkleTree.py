import hashlib,json
from collections import OrderedDict

class MerkleTree(object):
    def __init__(self, data = []):
        self.data = data
        self.merkle_tree = OrderedDict()
        self.origData = data

    def create_merkle_tree(self):
        data = self.data
        temp = []
        merkle_tree = self.merkle_tree

        # loop through the data two at a time to grab both sibling nodes
        for index in range(0,len(data),2):
            # hash the current data and add it to our merkle tree
            current = data[index]
            current_hash = hashlib.sha512(current.encode('utf-8'))
            merkle_tree[data[index]] = current_hash.hexdigest()
            #prevent double hashing
            if current in merkle_tree.values():
                print("Double: ",current)
                merkle_tree[data[index]] = current
            if index + 1 != len(data):
                # do the same if there is a right node
                current_sibling = data[index + 1]
                # TODO fix the doublehashing here
                current_sibling_hash = hashlib.sha512(current_sibling.encode('utf-8'))
                merkle_tree[data[index + 1]] = current_sibling_hash.hexdigest()
                # concate both hashes and add them to a temp list
                # if the sibling has been hashed already then dont hash again
                if current_sibling in merkle_tree.values():
                    merkle_tree[data[index + 1]] = current_sibling
                    temp.append(current_hash.hexdigest() + current_sibling)
                else:
                    temp.append(current_hash.hexdigest() + current_sibling_hash.hexdigest())
            else:
                # otherwise just add the left node hash to the temp list
                if current in merkle_tree.values():
                    temp.append(current)
                else:
                    temp.append(current_hash.hexdigest())
        if len(data) != 1:
            # continue for rest of data
            self.data = temp
            self.merkle_tree = merkle_tree
            self.create_merkle_tree()

    def get_root_hash(self):
        last_key = list(self.merkle_tree.keys())[-1]
        return self.merkle_tree[last_key]

    def print_merkle_tree(self):
        print( "-" * 75)
        print(json.dumps(self.merkle_tree, indent=4))
        print( "-" * 75)

    def get_merkle_tree(self):
        return self.merkle_tree

    def insert(self,in_data):
        self.origData.append(in_data)
        self.data = self.origData
        self.merkle_tree = OrderedDict()
        self.create_merkle_tree()

    def generate_merkle_path(self,entry):
        if entry not in self.origData:
            print("path_not_found")
            return
        path = []
        current_key = entry
        tree = self.merkle_tree
        while tree[current_key] != str(self.get_root_hash()):
            index = list(tree.keys()).index(current_key)
            if tree[current_key] + list(tree.items())[index + 1][1] in tree.keys():
                #add sibling to path
                path.append(list(tree.items())[index + 1][1])
                #update current key
                current_key = str(tree[list(tree.keys())[index]]) + str(tree[list(tree.keys())[index+1]])
            elif list(tree.items())[index - 1][1] + tree[current_key] in tree.keys():
                # add sibling to path
                path.append(list(tree.items())[index - 1][1])
                #update current_key
                current_key = str(tree[list(tree.keys())[index-1]]) + str(tree[list(tree.keys())[index]])
            else:
                current_key = tree[current_key]
        return path

    def delete(self,entry):
        if entry not in self.origData:
            print("Entry not in  Merkle Tree")
        else:
            # remove this value
            index = self.origData.index(entry)
            # move most right node to index of element to be deleted
            self.origData[index] = self.origData[len(self.origData) - 1]
            # remove duplicate of right most node
            self.origData.pop()
            # construct merkle tree
            self.data = self.origData
            self.merkle_tree = OrderedDict()
            self.create_merkle_tree()

    def verify_merkle_path(self, entry, merkle_path):
        current_hash = hashlib.sha512(entry.encode('utf-8'))
        for node in merkle_path:
            current_hash = hashlib.sha512(str(current_hash.hexdigest() + node).encode('utf-8'))
        if current_hash.hexdigest() == self.get_root_hash():
            return True
        else:
            return False


if __name__ == "__main__":
    transaction = ['a','b']
    merkle_tree = MerkleTree()
    merkle_tree.insert('a')
    merkle_tree.insert('b')
    merkle_tree.insert('c')
    merkle_tree.insert('d')
    merkle_tree.insert('e')
    merkle_tree.insert('f')
    #merkle_tree.create_tree()
    print ('Final root of the tree : ',merkle_tree.get_root_hash())
    tree = merkle_tree.get_merkle_tree()
    merkle_tree.print_merkle_tree()
    path = merkle_tree.generate_merkle_path("a")
    print("Merkle path: ", path)

    if merkle_tree.verify_merkle_path("a", path):
        print("Merkle path is Correct")
    else:
        print("Merkle path is Incorrect")
    merkle_tree.delete('a')
    print ('Final root of the tree : ',merkle_tree.get_root_hash())
    merkle_tree.print_merkle_tree()
