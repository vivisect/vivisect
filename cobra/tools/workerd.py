import sys
import argparse

import cobra.cluster as c_cluster


def setup():
    ap = argparse.ArgumentParser('Cluster worker tool')
    ap.add_argument('cluster', help='Name of the cluster to attach to')
    return ap


def main(argv):
    opts = setup().parse_args(argv)
    worker = c_cluster.ClusterClient(opts.cluster, docode=True)
    worker.processWork()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
