import sys

import cobra
import cobra.cluster as c_cluster

def usage():
    print('Usage: python -m cobra.tools.workerd <clustername>')
    sys.exit(-1)

def main():

    if len(sys.argv) != 2:
        usage()

    cname = sys.argv[1]
    worker = c_cluster.ClusterClient(cname, docode=True)
    worker.processWork()

if __name__ == '__main__':
    # FIXME make this actually take arguments
    sys.exit(main())
