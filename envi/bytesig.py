"""
A byte and mask based decision engine for creating byte
sequences (and potential comparison masks) for general purpose
signature matching.

Currently used by vivisect function entry sig db and others.
"""


class SignatureTree:
    """
    A byte based decision tree which uses all the RAMs but is
    really fast....

    Signatures consist of a byte sequence and an optional mask
    sequence.  If present each mask byte is used to logical and
    the byte being compared before comparison.  This allows the
    creation of signatures which have parts of the sig generalized.

    FIXME allow sigs to have a reliability rating
    FIXME allow sig nodes to store depth and truncate the tree early (and then mask the rest)
    """

    def __init__(self):
        # each node in the tree is a tuple consisting of the depth we're at,
        # the signatures in this particular subtree, and the list of subtree nodes
        self.basenode = (0, [], [None] * 256, [])
        self.sigs = {}  # track duplicates

    def _addChoice(self, siginfo, node):

        todo = [(node, siginfo),]

        # Recursion is for the weak minded.
        while len(todo):

            node, siginfo = todo.pop()
            depth, sigs, choices, term = node
            bytes, masks, o = siginfo
            siglen = len(sigs)
            if len(bytes) > depth:
                sigs.append(siginfo)
            else:
                term.append(siginfo)
                continue
            # If one sig is [85, 139, 236] and another is [85, 139, 236, 232, 144], then
            # we're gonna hit an IndexException without this check
            if siglen == 0:
                pass # we just don't want the "else" here, if we're the only
                # one on this node, just let it ride.

            elif siglen == 1:
                # If it has one already, we *both* need to add another level
                # (because if it is the only one, it thought it was last choice)
                for sig in sigs:
                    chval = sig[0][depth] # get the choice byte from siginfo
                    nnode = self._getNode(depth, choices, chval)
                    todo.append((nnode, sig))

            else: # This is already a choice node, keep on choosing...
                chval = bytes[depth]
                nnode = self._getNode(depth, choices, chval)
                todo.append((nnode, siginfo))

    def _getNode(self, depth, choices, choice):
        # Chose, (and or initialize) a sub node
        nnode = choices[choice]
        if nnode is None:
            nnode = (depth+1, [], [None] * 256, [])
            choices[choice] = nnode
        return nnode

    def addSignature(self, bytes, masks=None, val=None):
        """
        Add a signature to the search tree.  If masks goes unspecified, it will be
        assumed to be all ones (\\xff * len(bytes)).

        Additionally, you may specify "val" as the object to get back with
        getSignature().
        """
        # FIXME perhaps make masks None on all ff's
        if masks is None:
            masks = b'\xff' * len(bytes)

        if val is None:
            val = True

        # Detect and skip duplicate additions...
        bytekey = bytes + masks
        if self.sigs.get(bytekey) is not None:
            return

        self.sigs[bytekey] = True

        siginfo = (bytes, masks, val)
        self._addChoice(siginfo, self.basenode)

    def isSignature(self, bytes, offset=0):
        return self.getSignature(bytes, offset=offset) is not None

    def getSignature(self, bytes, offset=0):
        matches = []
        node = self.basenode
        while True:
            depth, sigs, choices, term = node
            matches.extend(term)
            # Once we get down to one sig, there are no more branches,
            # just check the byte sequence.
            if len(sigs) == 1:
                sbytes, smasks, sobj = sigs[0]
                is_match = True
                for i in range(depth, len(sbytes)):
                    realoff = offset + i
                    # we still have pieces of the signature left to match, but bytes wasn't long enough
                    if realoff >= len(bytes):
                        is_match = False
                        break
                    masked = bytes[realoff] & smasks[i]
                    if masked != sbytes[i]:
                        is_match = False
                        break
                if is_match:
                    matches.append(sigs[0])
                break

            # There are still more choices, keep branching.
            node = None # Lets go find a new one
            for sig in sigs:
                sbytes, smasks, sobj = sig
                if offset+depth >= len(bytes):
                    continue
                # we've reached the end of this signature, so we're just going to mask the rest
                masked = bytes[offset+depth] & smasks[depth]
                if sbytes[depth] == masked: # We have a winner!
                    # FIXME find the *best* winner! (because of masking)
                    node = choices[masked]
                    break

            # We failed to make our next choice
            if node is None:
                break
        if len(matches) == 0:
            return None
        return sorted(matches, key=lambda m: len(m[0]), reverse=True)[0][2]
