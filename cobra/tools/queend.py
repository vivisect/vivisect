import sys

import cobra
import cobra.cluster as c_cluster

def usage():
    print('Usage: python -m cobra.tools.queend <ifaceip>')
    print('( ifaceip is the IP of the interface facing the cluster)')
    sys.exit(-1)

def main():
    if len(sys.argv) != 2:
        usage()

    ip = sys.argv[1]
    q = c_cluster.ClusterQueen(ip)

    daemon = cobra.CobraDaemon(port=c_cluster.queen_port)
    daemon.shareObject(q, 'ClusterQueen')
    daemon.serve_forever()

if __name__ == '__main__':
    sys.exit(main())
